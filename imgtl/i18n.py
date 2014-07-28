#!/usr/bin/env python
# -*- coding: utf-8 -*-

i18n_dict = {
    'ko': {
        'youmustlogin': '로그인을 해야 합니다',
        'invalidemail': '잘못된 이메일 주소입니다.',
        'invalidusername': '잘못된 사용자명입니다. 사용자명은 최소 4글자여야 합니다.',
        'invalidpassword': '잘못된 비밀번호입니다. 비밀번호는 최소 8글자여야 합니다.',
        'passwordmismatch': '두 비밀번호가 일치하지 않습니다.',
        'alreadyexistemail': '이미 존재하는 이메일입니다.',
        'alreadyexistname': '이미 존재하는 사용자 이름입니다.',
        'loginfailed': '잘못된 이메일, 계정명 또는 비밀번호입니다.',
        'loginfailed-oauthuser': '외부 사이트 연동을 통해 가입된 사용자입니다. 가입한 서비스를 이용해 로그인을 해 주십시오.',
        'wrongimage': '파일이 첨부되지 않았습니다.',
        'notimage': '파일이 이미지가 아니거나 업로드가 가능한 이미지 종류(JPG, PNG, GIF, SVG)가 아닙니다.',
        'accupdatesuccess': '계정 정보가 갱신되었습니다.',
        'uploadsuccess': '업로드가 완료되었습니다.',
        'signupsuccess': '가입이 완료되었습니다.',
        'deletesuccess': '이미지가 삭제되었습니다.',
        'invalidexpiretime': '잘못된 만료 시간입니다.',
        'invalidexpiretime-toolong': '만료 시간은 1년을 넘을 수 없습니다.',
        'nopassword': '비밀번호를 설정해야 합니다.',
        'oauth-connected': '외부 계정이 ImgTL 계정에 연결되었습니다.',
        'oauth-disconnected': '외부 계정 연결이 해제되었습니다.'
    }
}

def i18n(key, lang='ko'):
    try:
        return i18n_dict[lang][key].decode('utf-8')
    except KeyError:
        return key
