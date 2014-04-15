#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shortuuid
import md5 as md5module
from wand.image import Image as wImage
from struct import unpack
from datetime import datetime, timedelta

from flask.ext.bcrypt import Bcrypt

from .const import URL_BLACKLIST, AVAILABLE_FORMAT, SERVERS, EXPIRE_BEHAVIORS


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
    im.transform(resize='x150>')
    return im

def get_prop(fs):
    exif = {}
    im = wImage(blob=fs)
    exif.update((k[5:], v) for k, v in im.metadata.items() if k.startswith('exif:'))
    p = {
            'width': im.width,
            'height': im.height,
            'filesize': len(fs),
            'exif': exif,
        }
    return p

def get_server_id(name):
    return SERVERS.keys().index(name) + 1

def calc_expire_time(minute):
    return datetime.now() + timedelta(minutes=minute)

def get_expire_behavior_id(behavior_str):
    if not behavior_str:
        return None
    return EXPIRE_BEHAVIORS.index(behavior_str)

def get_expire_behavior(behavior_id):
    return EXPIRE_BEHAVIORS[behavior_id]

# code from https://dpk.net/2013/02/21/simple-python-script-to-strip-exif-data-from-a-jpeg/
def strip_exif(image):
    begin_exif = image.find(b'\xff\xe1')
    if begin_exif >= 0:
        ret = image[0:begin_exif]
        exif_size = unpack('>H', image[begin_exif+2:begin_exif+4])[0]
        ret += image[begin_exif+exif_size+2:]
        return ret
    return image
