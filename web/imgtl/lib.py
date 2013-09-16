#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import md5 as md5module
from wand.image import Image as wImage
import shortuuid

from flaskext.bcrypt import Bcrypt

from .const import URL_BLACKLIST, AVAILABLE_FORMAT


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
        wim = wImage(blob=fs)
        if wim.format not in AVAILABLE_FORMAT:
            raise
    except:
        return False
    else:
        return True

def get_ext(fn):
    return os.path.splitext(fn)[1][1:]

def get_spath(path, code):
    return os.path.join(path, code[0], code[1], code)

def create_thumbnail(fs):
    im = wImage(blob=fs)
    im.transform(resize='%dx%d^' % (135, 135))
    return im
