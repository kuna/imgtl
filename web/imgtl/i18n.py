#!/usr/bin/env python
# -*- coding: utf-8 -*-

i18n_dict = {
        'ko': {
            'youmustlogin': '로그인을 해야 합니다',
            'invalidemail': '잘못된 이메일 주소입니다.',
            'invalidusername': '잘못된 사용자명입니다.',
            'passwordmismatch': '비밀번호가 일치하지 않습니다.',
            'alreadyexistemail': '이미 존재하는 이메일입니다.',
            'alreadyexistname': '이미 존재하는 사용자 이름입니다.',
            'loginfailed': '잘못된 이메일, 계정명 또는 비밀번호입니다.',
            'imagenotattached': '파일이 첨부되지 않았습니다',
            'fileisnotimage': '파일이 이미지가 아닙니다.',
            }
        }

def i18n(key, lang='ko'):
    try:
        return i18n_dict[lang][key].decode('utf-8')
    except KeyError:
        return None
