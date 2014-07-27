#!/usr/bin/env python
# -*- coding: utf-8 -*

from collections import OrderedDict

BASE_URL = 'https://img.tl/%s'

# SERVERS
SERVERS = OrderedDict((
    ('S1', 's1.img.tl'),
    ('S2', 's2.img.tl'),
))

# OBJ_TYPE
TYPE_IMAGE = 1
TYPE_FILE = 2
TYPE_TEXT = 3

# EXPIRE_BEHAVIOR
EXPIRE_BEHAVIORS = (
    'delete',
    'private',
)

USER_DEFAULT_ICON = BASE_URL % 'img/user_icon.png'

USERNAME_BLACKLIST = ['admin', 'root', 'mail', 'beta', 'test', 'static']
URL_BLACKLIST = ['login', 'signup', 'logout', 'upload', 'img', 'css', 'js', 'fonts']

AVAILABLE_FORMAT = ['JPEG', 'PNG', 'GIF', 'SVG']

ADMIN_IDS = (1, )
