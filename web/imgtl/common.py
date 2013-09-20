#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import request, current_app

from sqlalchemy.exc import IntegrityError

from .lib import md5, is_image, get_ext, get_spath, make_url, create_thumbnail, get_prop
from .const import SERVER_S1
from .db import *


def do_log(target, action, action_id, user):
    if user:
        log = Log(target=target, action=action, action_id=action_id, user_id=user.id)
    else:
        log = Log(target=target, action=action, action_id=action_id, ip=request.remote_addr)
    log_db.session.add(log)
    log_db.session.flush()

def do_upload_image(user, f, desc):
    if not f:
        return 'wrongimage'
    fn = f.filename
    fs = f.read()
    if not is_image(fs):
        return 'notimage'
    code = '%s.%s' % (md5(fs), get_ext(fn))
    image = Image.query.filter_by(code=code).first()
    if not image:
        image = Image(server=SERVER_S1, code=code, prop=get_prop(fs))
        fp = get_spath(current_app.config['UPLOAD_DIR'], code)
        tfp = get_spath(os.path.join(current_app.config['UPLOAD_DIR'], 'thumb'), code)
        if not os.path.exists(os.path.dirname(fp)):
            os.makedirs(os.path.dirname(fp))
        if not os.path.exists(os.path.dirname(tfp)):
            os.makedirs(os.path.dirname(tfp))
        with open(fp, 'w') as fi:
            fi.write(fs)
        create_thumbnail(fs).save(filename=tfp)
    upload = Upload(object=image, user=user, title=fn, desc=desc)
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

def do_delete_image(user, upload_url):
    upload = Upload.query.filter_by(url=upload_url).first()
    if not upload or upload.deleted:
        return 'nosuchimage'
    if upload.user != user:
        return 'notmine'
    upload.deleted = 1
    db.session.commit()
    do_log(current_app.name, 'delete', upload.id, user)
    return 'success'
