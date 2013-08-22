#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from .const import USERNAME_BLACKLIST


REGEX_EMAIL = re.compile(r'^[^@]+@[^\.]+\...+$')
REGEX_USERNAME = re.compile(r'^[A-Za-z0-9_]{4,16}$')


def email(mail):
    if len(mail) > 120:
        return False
    m = REGEX_EMAIL.search(mail)
    return True if m else False

def username(name):
    if name in USERNAME_BLACKLIST:
        return False
    if len(name) < 4 or len(name) > 16:
        return False
    m = REGEX_USERNAME.search(name)
    return True if m else False

def password(pw):
    if len(pw) < 8:
        return False
    return True
