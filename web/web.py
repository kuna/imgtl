#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, request, redirect, url_for, render_template, abort, make_response, flash, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
from imgtl.i18n import i18n
from imgtl.common import do_upload_image
import imgtl.lib
import imgtl.validator


app = Flask(__name__)
app.config.from_pyfile('imgtl.cfg')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db.init_app(app)
db.app = app
log_db.init_app(app)
log_db.app = app

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = i18n('youmustlogin')
login_manager.init_app(app)


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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return redirect(url_for('login', _anchor='register'))
    elif request.method == 'POST':
        if not imgtl.validator.email(request.form['email']):
            flash(i18n('invalidemail'))
            return redirect(url_for('signup'))
        if not imgtl.validator.username(request.form['username']):
            flash(i18n('invalidusername'))
            return redirect(url_for('signup'))
        if not imgtl.validator.password(request.form['password']):
            flash(i18n('invalidpassword'))
            return redirect(url_for('signup'))
        if request.form['password'] != request.form['passwordconfirm']:
            flash(i18n('passwordmismatch'))
            return redirect(url_for('signup'))
        user = User.query.filter(or_(User.email==request.form['email'], User.name==request.form['username'])).first()
        if user:
            if user.email == request.form['email']:
                flash(i18n('alreadyexistemail'))
                return redirect(url_for('signup'))
            elif user.name == request.form['username']:
                flash(i18n('alreadyexistname'))
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
        return redirect(url_for('index'))

@app.route('/signup/check', methods=['POST'])
def signup_check():
    if request.form['what'] not in ['email', 'username']:
        abort(400)
    res = False
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
        user = User.query.filter(or_(User.email==request.form['emailuser'], User.name==request.form['emailuser'])).first()
        if user and imgtl.lib.pw_verify(user.password, request.form['password']):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash(i18n('loginfailed'))
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if current_user.is_authenticated():
        user = current_user
    else:
        user = None
    upload = do_upload_image(user, request.files['image'], request.form['desc'] if 'desc' in request.form else None)
    if isinstance(upload, str):
        flash(i18n(upload))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('show', url=upload.url))

@app.route('/<url>')
def show(url):
    upload = Upload.query.filter_by(url=url).first()
    if not upload:
        abort(404)
    obj = Object.query.get(upload.object_id)
    if isinstance(obj, Image):
        return render_template('show/image.html', user=current_user, upload=upload)

@app.route('/<url>.<ext>')
def show_only_image(url, ext):
    upload = Upload.query.filter_by(url=url).first()
    if not upload:
        abort(404)
    obj = Object.query.get(upload.object_id)
    if isinstance(obj, Image):
        if obj.ext != ext:
            abort(404)
        fpath = imgtl.lib.get_spath(app.config['UPLOAD_DIR'], obj.code)
        r = make_response()
        r.headers['Cache-Control'] = 'public'
        r.headers['Content-Type'] = ''
        r.headers['Content-Disposition'] = 'inline; filename="%s"' % upload.title.encode('utf8')
        r.headers['X-Accel-Redirect'] = imgtl.lib.get_spath('/x', obj.code)
        return r

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=2560)
