#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, request, redirect, url_for, render_template, abort, make_response, flash, jsonify, session
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.oauthlib.client import OAuth

from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
from imgtl.i18n import i18n
from imgtl.common import get_upload, do_upload_image, do_update_image, do_delete_image, do_log
from imgtl.template import jinja2_filter_nl2br, jinja2_filter_dt
import imgtl.lib
import imgtl.validator


app = Flask(__name__)
app.config.from_pyfile('imgtl.cfg')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters['nl2br'] = jinja2_filter_nl2br
app.jinja_env.filters['dt'] = jinja2_filter_dt

db.init_app(app)
db.app = app
log_db.init_app(app)
log_db.app = app

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = i18n('youmustlogin')
login_manager.init_app(app)

oauth = OAuth()
oauth.init_app(app)
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    access_token_method='POST',
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    if current_user.is_anonymous():
        return render_template('index.html')
    else:
        return render_template('mypage.html', user=current_user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'GET':
        return render_template('settings.html', user=current_user)
    elif request.method == 'POST':
        if request.form['what'] == 'token':
            while 1:
                try:
                    current_user.token = imgtl.lib.make_token()
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    continue
                else:
                    break
            return jsonify({'token': current_user.token})
        elif request.form['what'] == 'update':
            if request.form.get('password', '') != '':
                if not imgtl.validator.password(request.form['password']):
                    flash(i18n('invalidpassowrd'), 'error')
                    return redirect(url_for('settings'))
                elif request.form['password'] != request.form['passwordconfirm']:
                    flash(i18n('passwordmismatch'), 'error')
                    return redirect(url_for('settings'))
                else:
                    current_user.password = request.form['password']
                    db.session.commit()
            new_email = request.form['email']
            new_username = request.form['username']
            if not imgtl.validator.email(new_email):
                flash(i18n('invalidemail'), 'error')
                return redirect(url_for('settings'))
            if not imgtl.validator.username(new_username):
                flash(i18n('invalidusername'), 'error')
                return redirect(url_for('settings'))
            if current_user.email != new_email:
                if User.query.filter_by(email=new_email).first():
                    flash(i18n('alreadyexistemail'), 'error')
                    return redirect(url_for('settings'))
            if current_user.name != new_username:
                if User.query.filter_by(name=new_username).first():
                    flash(i18n('alreadyexistname'), 'error')
                    return redirect(url_for('settings'))
            current_user.email = new_email
            current_user.name = new_username
            db.session.commit()
            flash(i18n('accupdatesuccess'), 'success')
            return redirect(url_for('settings'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return redirect(url_for('login', _anchor='register'))
    elif request.method == 'POST':
        if not imgtl.validator.email(request.form['email']):
            flash(i18n('invalidemail'), 'error')
            return redirect(url_for('signup'))
        if not imgtl.validator.username(request.form['username']):
            flash(i18n('invalidusername'), 'error')
            return redirect(url_for('signup'))
        if not imgtl.validator.password(request.form['password']):
            flash(i18n('invalidpassword'), 'error')
            return redirect(url_for('signup'))
        if request.form['password'] != request.form['passwordconfirm']:
            flash(i18n('passwordmismatch'),'error')
            return redirect(url_for('signup'))
        user = User.query.filter((User.email==request.form['email']) | (User.name==request.form['username'])).first()
        if user:
            if user.email == request.form['email']:
                flash(i18n('alreadyexistemail'), 'error')
                return redirect(url_for('signup'))
            elif user.name == request.form['username']:
                flash(i18n('alreadyexistname'), 'error')
                return redirect(url_for('signup'))
        user = User(email=request.form['email'], name=request.form['username'], password=imgtl.lib.pw_hash(request.form['password']))
        while 1:
            try:
                user.token = imgtl.lib.make_token()
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue
            else:
                break
        db.session.add(user)
        db.session.commit()
        login_user(user)
        do_log('web', 'signup', user.id)
        flash(i18n('signupsuccess'), 'success')
        return redirect(url_for('index'))

@app.route('/signup/check', methods=['POST'])
def signup_check():
    if request.form['what'] not in ['email', 'username']:
        abort(400)
    res = False
    if 'except' not in request.form or request.form['except'] != request.form['value']:
        if request.form['what'] == 'email':
            user = User.query.filter_by(email=request.form['value']).first()
            if user:
                res = True
        elif request.form['what'] == 'username':
            if request.form['value'] in USERNAME_BLACKLIST:
                res = True
            else:
                user = User.query.filter_by(name=request.form['value']).first()
                if user:
                    res = True
    return jsonify({'res': res})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        user = User.query.filter((User.email==request.form['emailuser']) | (User.name==request.form['emailuser'])).first()
        if user and user.password and imgtl.lib.pw_verify(user.password, request.form['password']):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash(i18n('loginfailed' if not user or user.password else 'loginfailed-oauthuser'), 'error')
            return redirect(url_for('login'))

@app.route('/oauth/login')
def oauth_login():
    if session.has_key('twitter_token'):
        del session['twitter_token']
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth/authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)
    user = User.query.filter_by(oauth_uid=resp['user_id']).first()
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret'],
    )
    if user:
        login_user(user)
        return redirect(next_url)
    else:
        session['oauth_signup'] = {
            'name': resp['screen_name'],
            'oauth_uid': resp['user_id'],
        }
        return redirect(url_for('oauth_signup'))

@app.route('/oauth/signup', methods=['GET', 'POST'])
def oauth_signup():
    if not session.has_key('oauth_signup'):
        flash(i18n('invalidaccess'), 'error')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('oauth_signup.html', user=current_user, sess=session['oauth_signup'])
    elif request.method == 'POST':
        if not imgtl.validator.email(request.form['email']):
            flash(i18n('invalidemail'), 'error')
            return redirect(url_for('oauth_signup'))
        if not imgtl.validator.username(request.form['username']):
            flash(i18n('invalidusername'), 'error')
            return redirect(url_for('oauth_signup'))
        user = User.query.filter((User.email==request.form['email']) | (User.name==request.form['username'])).first()
        if user:
            if user.email == request.form['email']:
                flash(i18n('alreadyexistemail'), 'error')
                return redirect(url_for('oauth_signup'))
            elif user.name == request.form['username']:
                flash(i18n('alreadyexistname'), 'error')
                return redirect(url_for('oauth_signup'))
        user = User(email=request.form['email'], name=request.form['username'], oauth_uid=session['oauth_signup']['oauth_uid'])
        while 1:
            try:
                user.token = imgtl.lib.make_token()
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue
            else:
                break
        db.session.add(user)
        db.session.commit()
        login_user(user)
        do_log('web', 'signup_by_oauth', user.id)
        del session['oauth_signup']
        flash(i18n('signupsuccess'), 'success')
        return redirect(url_for('index'))

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/logout')
def logout():
    if session.has_key('twitter_token'):
        del session['twitter_token']
    logout_user()
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if current_user.is_authenticated():
        user = current_user
    else:
        user = None
    expire = None
    try:
        exp = int(request.form['expire'])
        if exp != -1:
            if exp != 0:
                expire = int(exp)
            else:
                expire = int(request.form['expire-custom']) * int(request.form['expire-custom-unit'])
            if expire > 518400:
                flash(i18n('invalidexpiretime-toolong'), 'error')
                return redirect(url_for('index'))
            expire = imgtl.lib.calc_expire_time(expire)
    except ValueError:
        flash(i18n('invalidexpiretime'), 'error')
        return redirect(url_for('index'))
    upload = do_upload_image(user, request.files['image'], request.form.get('desc'),
                                request.form.get('nsfw') == 'on', request.form.get('anonymous') == 'on', request.form.get('private') == 'on',
                                request.form.get('keep-exif') == 'on', expire, request.form.get('expire-behavior'))
    if isinstance(upload, str):
        flash(i18n(upload), 'error')
        return redirect(url_for('index'))
    else:
        if current_user.is_anonymous():
            if 'anon_uploads' not in session: session['anon_uploads'] = []
            session['anon_uploads'].append(upload.id)
        flash(i18n('uploadsuccess'), 'success')
        return redirect(url_for('show', url=upload.url))

@app.route('/<url>', methods=['GET', 'PUT', 'DELETE'])
def show(url):
    if request.method == 'DELETE':
        res = do_delete_image(current_user, url)
        if res == 'success':
            flash(i18n('deletesuccess'), 'success')
        return jsonify({'res': res})
    elif request.method == 'PUT':
        res = do_update_image(current_user, url, request.form.get('nsfw') == 'true', request.form.get('anonymous') == 'true', request.form.get('private') == 'true')
        return jsonify({'res': res})
    elif request.method == 'GET':
        upload = get_upload(url)
        if (not upload) or upload.deleted:
            abort(404)
        if upload.private and (current_user != upload.user):
            abort(403)
        obj = Object.query.get(upload.object_id)
        if 'views' not in session: session['views'] = []
        if upload.id not in session.get("views"):
            session['views'].append(upload.id)
            upload.view_count += 1
            db.session.commit()
        if isinstance(obj, Image):
            return render_template('show/image.html', user=current_user, upload=upload)

@app.route('/<url>.<ext>')
def show_only_image(url, ext):
    upload = get_upload(url)
    if not upload:
        abort(404)
    obj = Object.query.get(upload.object_id)
    if isinstance(obj, Image):
        if (not upload) or upload.deleted or obj.ext != ext:
            abort(404)
        if upload.private and (current_user != upload.user):
            abort(403)
        fpath = imgtl.lib.get_spath(app.config['UPLOAD_DIR'], obj.code)
        r = make_response()
        r.headers['Cache-Control'] = 'public'
        r.headers['Content-Type'] = ''
        r.headers['Content-Disposition'] = 'inline; filename="%s"' % upload.title.encode('utf8')
        r.headers['X-Accel-Redirect'] = imgtl.lib.get_spath('/x', obj.code)
        return r

@app.route('/thumb/<url>')
def show_thumbnail(url):
    upload = get_upload(url)
    obj = Object.query.get(upload.object_id)
    if (not upload) or upload.deleted:
        abort(404)
    if upload.private and (current_user != upload.user):
        abort(403)
    fpath = imgtl.lib.get_spath(os.path.join(app.config['UPLOAD_DIR'], 'thumb'), obj.code)
    r = make_response()
    r.headers['Cache-Control'] = 'public'
    r.headers['Content-Type'] = ''
    r.headers['Content-Disposition'] = 'inline; filename="%s"' % upload.title.encode('utf8')
    r.headers['X-Accel-Redirect'] = imgtl.lib.get_spath('/x/thumb', obj.code)
    return r

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=2560)
