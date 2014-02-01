#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from jinja2 import evalcontextfilter, Markup, escape

RE_NL2BR = re.compile(r'(\\r)?\\n', re.UNICODE | re.MULTILINE)

@evalcontextfilter
def jinja2_filter_nl2br(eval_ctx, value):
    res = RE_NL2BR.sub('<br>\n', unicode(escape(value)))
    if eval_ctx.autoescape:
        res = Markup(res)
    return res

def jinja2_filter_dt(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)
