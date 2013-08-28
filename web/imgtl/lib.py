#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import md5 as md5module
from wand.image import Image as wImage
import shortuuid

from flaskext.bcrypt import Bcrypt

from .const import URL_BLACKLIST


bcrypt = Bcrypt()
shortuuid.set_alphabet("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

def md5(stri):
    m = md5module.new()
    m.update(stri)
    return m.hexdigest()

def make_url(l=4):
    url = shortuuid.uuid()[:l]
    if url in URL_BLACKLIST:
        return make_url(l)
    return url

def make_token():
    return md5(shortuuid.uuid())

def pw_hash(plainpw):
    return bcrypt.generate_password_hash(plainpw)

def pw_verify(hashedpw, plainpw):
    return bcrypt.check_password_hash(hashedpw, plainpw)

def is_image(fs):
    try:
        wImage(blob=fs)
        return True
    except:
        return False

def get_ext(fn):
    return os.path.splitext(fn)[1][1:]

def get_spath(path, code):
    return os.path.join(path, code[0], code[1], code)


def do_upload(user, f, desc):
    if not f:
        return 'imagenotattached'
    fn = f.filename
    fs = f.read()
    if not is_image(fs):
        return 'wrongimage'
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
        except IntegirityError:
            db.session.rollback()
            continue
        else:
            break
    db.session.add(image)
    db.session.commit()
    return upload
