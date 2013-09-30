#!/usr/bin/env python
# -*- coding: utf-8 -*

# SERVER
SERVER_S1 = 1
SERVER_S2 = 2
SERVER_S3 = 3

BASE_URL = 'https://img.tl/%s'

# OBJECT_URL
OBJECT_URL = {
    SERVER_S1: 'https://s1.img.tl/%s',
    SERVER_S2: 'https://s2.img.tl/%s',
}

# OBJ_TYPE
TYPE_IMAGE  = 1
TYPE_FILE   = 2
TYPE_TEXT   = 3

USER_DEFAULT_ICON = BASE_URL % 'img/user_icon.png'

USERNAME_BLACKLIST = ['admin', 'root', 'mail', 'beta', 'test', 'static']
URL_BLACKLIST = ['login', 'signup', 'logout', 'upload', 'img', 'css', 'js']

AVAILABLE_FORMAT = ['JPEG', 'PNG', 'GIF', 'SVG']
