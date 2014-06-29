#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import simplejson

from imgtl.db import *
from imgtl.lib import pw_hash
from imgtl.i18n import i18n as _i18n

class ImgTLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['TESTING'] = 'true'
        from web import app, db
        cls.app = app.test_client()
        db.create_all()
        # add default user
        db.session.add(User(email='tests@img.tl', name='tests', password=pw_hash('password1234')))
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        db.session.begin(subtransactions=True)

    def tearDown(self):
        db.session.rollback()
        db.session.close()

    def i18n(self, key):
        return _i18n(key).encode('utf-8')

    def signup(self, email, username, password, passwordconfirm):
        data = {'email': email,
                'username': username,
                'password': password,
                'passwordconfirm': passwordconfirm,
                }
        return self.app.post('/signup', data=data, follow_redirects=True)

    def signup_check(self, what, value, exc=None):
        data = {'what': what,
                'value': value,
                }
        if exc: data['except'] = exc
        return self.app.post('/signup/check', data=data)

    def login(self, emailusername, password):
        data = {'emailusername': emailusername,
                'password': password,
                }
        return self.app.post('/login', data=data, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def upload(self, image, desc='', keep_exif=True, expire=-1, expire_behavior='delete', expire_custom=None, expire_custom_unit=1):
        data = {'image': image,
                'desc': desc,
                'keep-exif': 'on' if keep_exif else 'off',
                'expire': expire,
                'expire-behavior': expire_behavior,
                'expire-custom': expire_custom,
                'expire-custom-unit': expire_custom_unit,
                }
        return self.app.post('/upload', data=data, follow_redirects=True)

    def test_index(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)

    def test_signup_form(self):
        r = self.app.get('/signup', follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        # TODO: add redirect check

    def test_signup_process_success(self):
        r = self.signup(email='new@img.tl', username='new_username', password='password1234', passwordconfirm='password1234')
        count = User.query.filter_by(name='new_username').count()
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('signupsuccess'), r.data)
        self.assertEqual(count, 1)
        self.logout()

    def test_signup_process_invalid_email(self):
        r = self.signup(email='new@imgtl', username='new_username', password='password1234', passwordconfirm='password1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('invalidemail'), r.data)

    def test_signup_process_invalid_username_short_length(self):
        r = self.signup(email='new@img.tl', username='new', password='password1234', passwordconfirm='password1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('invalidusername'), r.data)

    def test_signup_process_invalid_username_long_length(self):
        r = self.signup(email='new@img.tl', username='this_is_new_username', password='password1234', passwordconfirm='password1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('invalidusername'), r.data)

    def test_signup_process_invalid_username_character(self):
        r = self.signup(email='new@img.tl', username='new*username', password='password1234', passwordconfirm='password1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('invalidusername'), r.data)

    def test_signup_process_invalid_password_length_short(self):
        r = self.signup(email='new@img.tl', username='new_username', password='1234', passwordconfirm='1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('invalidpassword'), r.data)

    def test_signup_process_password_mismatch(self):
        r = self.signup(email='new@img.tl', username='new_username', password='password1234', passwordconfirm='password5678')
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.i18n('passwordmismatch'), r.data)

    def test_signup_check_email_success(self):
        r = self.signup_check(what='email', value='nonexists@img.tl')
        json = simplejson.loads(r.data)
        self.assertEqual(json['res'], False)

    def test_signup_check_email_exists(self):
        r = self.signup_check(what='email', value='tests@img.tl')
        json = simplejson.loads(r.data)
        self.assertEqual(json['res'], True)

    def test_signup_check_username_success(self):
        r = self.signup_check(what='username', value='nonexists')
        json = simplejson.loads(r.data)
        self.assertEqual(json['res'], False)

    def test_signup_check_username_exists(self):
        r = self.signup_check(what='username', value='tests')
        json = simplejson.loads(r.data)
        self.assertEqual(json['res'], True)

    def test_signup_check_nonexists_what(self):
        r = self.signup_check(what='hello', value='world')
        self.assertEqual(r.status_code, 400)

    def test_login_form(self):
        r = self.app.get('/login', follow_redirects=True)
        self.assertEqual(r.status_code, 200)

    def test_login_process_success_email(self):
        r = self.login(emailusername='tests@img.tl', password='password1234')
        self.assertIn('tests@img.tl', r.data)
        self.logout()

    def test_login_process_success_username(self):
        r = self.login(emailusername='tests', password='password1234')
        self.assertIn('tests@img.tl', r.data)
        self.logout()

    def test_login_process_invalid_email(self):
        r = self.login(emailusername='nonexists@img.tl', password='password1234')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_invalid_username(self):
        r = self.login(emailusername='nonexists', password='password1234')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_with_email_invalid_password(self):
        r = self.login(emailusername='tests@img.tl', password='password5678')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_with_username_invalid_password(self):
        r = self.login(emailusername='tests', password='password5678')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_upload_success(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'))
        self.assertIn(self.i18n('uploadsuccess'), r.data)
        self.assertIn('test.png', r.data)

    def test_upload_success_with_desc(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), desc='hulahulahoo')
        self.assertIn('hulahulahoo', r.data)

    def test_upload_parse_exif(self):
        fdata = open('tests/images/exif.jpg', 'r')
        r = self.upload(image=(fdata, 'exif.jpg'))
        self.assertIn('C6603', r.data)

    def test_upload_strip_exif(self):
        fdata = open('tests/images/exif.jpg', 'r')
        r = self.upload(image=(fdata, 'exif.jpg'), keep_exif=False)
        self.assertNotIn('C6603', r.data)

    def test_upload_no_exif(self):
        fdata = open('tests/images/exif_deleted.jpg', 'r')
        r = self.upload(image=(fdata, 'exif.jpg'))
        self.assertNotIn('C6603', r.data)

    def test_upload_fix_orientation(self):
        fdata = open('tests/images/exif_rotate_90.jpg', 'r')
        r = self.upload(image=(fdata, 'exif.jpg'))
        self.assertIn('90deg', r.data)

    def test_upload_fail_notimage(self):
        from StringIO import StringIO
        fdata = StringIO('dummy data')
        r = self.upload(image=(fdata, 'dummy.jpg'))
        self.assertIn(self.i18n('notimage'), r.data)

    def test_upload_fail_invalid_expire_time(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), expire=0, expire_custom='wahoo')
        self.assertIn(self.i18n('invalidexpiretime'), r.data)

    def test_upload_success_expire_time_not_too_long(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), expire=0, expire_custom=365, expire_custom_unit=1440)
        self.assertIn(self.i18n('uploadsuccess'), r.data)

    def test_upload_fail_expire_time_too_long(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), expire=0, expire_custom=366, expire_custom_unit=1440)
        self.assertIn(self.i18n('invalidexpiretime-toolong'), r.data)

if __name__ == '__main__':
    unittest.main()
