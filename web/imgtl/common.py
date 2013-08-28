#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import request, current_app

from sqlalchemy.exc import IntegrityError

from .lib import md5, is_image, get_ext, get_spath, make_url
from .const import SERVER_S1
from .db import *


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
        image = Image(server=SERVER_S1, code=code)
        fp = get_spath(current_app.config['UPLOAD_DIR'], code)
        if not os.path.exists(os.path.dirname(fp)):
            os.makedirs(os.path.dirname(fp))
        with open(fp, 'w') as fi:
            fi.write(fs)
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
    return upload
