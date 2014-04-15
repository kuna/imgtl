#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import simplejson

from web import app, db
from imgtl.db import *
from imgtl.lib import pw_hash
from imgtl.i18n import i18n as _i18n

class ImgTLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
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

    def login(self, emailuser, password):
        data = {'emailuser': emailuser,
                'password': password,
                }
        return self.app.post('/login', data=data, follow_redirects=True)

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
        r = self.login(emailuser='tests@img.tl', password='password1234')
        self.assertIn('tests@img.tl', r.data)

    def test_login_process_success_username(self):
        r = self.login(emailuser='tests', password='password1234')
        self.assertIn('tests@img.tl', r.data)

    def test_login_process_invalid_email(self):
        r = self.login(emailuser='nonexists@img.tl', password='password1234')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_invalid_username(self):
        r = self.login(emailuser='nonexists', password='password1234')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_with_email_invalid_password(self):
        r = self.login(emailuser='tests@img.tl', password='password5678')
        self.assertIn(self.i18n('loginfailed'), r.data)

    def test_login_process_with_username_invalid_password(self):
        r = self.login(emailuser='tests', password='password5678')
        self.assertIn(self.i18n('loginfailed'), r.data)

if __name__ == '__main__':
    unittest.main()
