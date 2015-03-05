#!/usr/bin/env python
# -*- coding: utf-8 -*

from collections import OrderedDict

# if you want to use HTTPS connection, change it into https protocol.
BASE_URL = 'http://127.0.0.1:2560/%s'

# SERVERS
SERVERS = OrderedDict((
    ('S1', '127.0.0.1:2560'),
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
