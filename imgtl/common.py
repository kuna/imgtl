#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import request, session, current_app

from sqlalchemy.exc import IntegrityError

from .lib import md5, is_image, get_ext, get_spath, make_url, create_thumbnail, get_prop, strip_exif, get_server_id, get_expire_behavior_id, get_expire_behavior
from .db import *


def do_log(target, action, action_id, user=None):
    if user and user.is_authenticated():
        log = Log(target=target, action=action, action_id=action_id, user_id=user.id)
    else:
        log = Log(target=target, action=action, action_id=action_id, ip=request.remote_addr)
    log_db.session.add(log)
    log_db.session.flush()

def get_upload(user, url):
    upload = Upload.query.filter_by(url=url).first()
    if upload and upload.is_expired:
        b = get_expire_behavior(upload.expire_behavior)
        if b == 'delete':
            upload.deleted = True
        elif b == 'private':
            upload.private = True
        upload.expire_time = None
        upload.expire_behavior = None
        db.session.commit()
        do_log(current_app.name, 'expire', upload.id, user)
    return upload

def do_upload_image(user, f, desc='', is_nsfw=False, is_anonymous=False, is_private=False, keep_exif=True, expire=None, expire_behavior=None):
    if not f:
        return 'wrongimage'
    fn = f.filename
    fs = f.read()
    if not is_image(fs):
        return 'notimage'
    if not keep_exif:
        fs = strip_exif(fs)
    code = '%s.%s' % (md5(fs), get_ext(fn))
    image = Image.query.filter_by(code=code).first()
    if not image:
        image = Image(server=get_server_id('S1'), code=code, prop=get_prop(fs))
        fp = get_spath(current_app.config['UPLOAD_DIR'], code)
        tfp = get_spath(os.path.join(current_app.config['UPLOAD_DIR'], 'thumb'), code)
        if not os.path.exists(os.path.dirname(fp)):
            os.makedirs(os.path.dirname(fp))
        if not os.path.exists(os.path.dirname(tfp)):
            os.makedirs(os.path.dirname(tfp))
        with open(fp, 'w') as fi:
            fi.write(fs)
        create_thumbnail(fs).save(filename=tfp)
    if not expire:
        expire_behavior = None
    elif not user:
        expire_behavior = 'delete'
    upload = Upload(object=image, user=user, title=fn, desc=desc, nsfw=is_nsfw, anonymous=is_anonymous, private=is_private, expire_time=expire, expire_behavior=get_expire_behavior_id(expire_behavior))
    while 1:
        try:
            upload.url = make_url()
            db.session.add(upload)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue
        else:
            break
    db.session.add(image)
    db.session.commit()
    do_log(current_app.name, 'upload', upload.id, user)
    return upload

def do_update_image(user, upload_url, is_nsfw, is_anonymous, is_private):
    upload = get_upload(user, upload_url)
    if not upload or upload.deleted:
        return 'nosuchimage'
    if (upload.user != user) and (upload.id not in session.get('anon_uploads', [])):
        return 'notmine'
    upload.nsfw = is_nsfw
    if upload.user == user:
        upload.anonymous = is_anonymous
        upload.private = is_private
    db.session.commit()
    do_log(current_app.name, 'update', upload.id, user)
    return 'success'

def do_delete_image(user, upload_url):
    upload = get_upload(user, upload_url)
    if not upload or upload.deleted:
        return 'nosuchimage'
    if (upload.user != user) and (upload.id not in session.get('anon_uploads', [])):
        return 'notmine'
    upload.deleted = True
    db.session.commit()
    do_log(current_app.name, 'delete', upload.id, user)
    return 'success'
