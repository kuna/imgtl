#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import simplejson

from imgtl.db import *
from imgtl.lib import pw_hash, make_token
from imgtl.i18n import i18n as _i18n

class ImgTLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['TESTING'] = 'true'
        from api import app, db
        cls.app = app.test_client()
        db.create_all()
        # add default user
        db.session.add(User(email='tests@img.tl', name='tests', password=pw_hash('password1234'), token='THISISTESTTOKEN'))
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

    def upload(self, image, desc='', token=None):
        data = {'file': image,
                'desc': desc,
                }
        headers = dict()
        if token:
            headers['X-IMGTL-TOKEN'] = token
        return self.app.post('/upload', data=data, headers=headers)

    def userinfo(self, token=None, with_uploads=False):
        params = {'with_uploads': 1 * with_uploads}
        headers = dict()
        if token:
            headers['X-IMGTL-TOKEN'] = token
        return self.app.get('/user/info', query_string=params, headers=headers)

    def test_index(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)

    def test_upload_success(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'))
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(json['status'], 'success')

    def test_upload_success_with_token(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), token='THISISTESTTOKEN')
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(json['status'], 'success')

    def test_upload_fail_wrongtoken(self):
        fdata = open('tests/images/test.png', 'r')
        r = self.upload(image=(fdata, 'test.png'), token='wahoo')
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(json['error'], 'wrongtoken')

    def test_upload_fail_imagenotattached(self):
        r = self.upload(image=None)
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json['error'], 'imagenotattached')

    def test_upload_fail_notimage(self):
        from StringIO import StringIO
        fdata = StringIO('dummy data')
        r = self.upload(image=(fdata, 'dummy.jpg'))
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(json['error'], 'notimage')

    def test_userinfo_success(self):
        r = self.userinfo(token='THISISTESTTOKEN', with_uploads=False)
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json['status'], 'success')

    def test_userinfo_success_with_uploads(self):
        r = self.userinfo(token='THISISTESTTOKEN', with_uploads=True)
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json['status'], 'success')
        self.assertIn('uploads', json['data']['user'])

    def test_userinfo_fail_notoken(self):
        r = self.userinfo()
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(json['error'], 'notoken')

    def test_userinfo_fail_wrongtoken(self):
        r = self.userinfo(token='heyho!')
        json = simplejson.loads(r.data)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(json['error'], 'wrongtoken')

if __name__ == '__main__':
    unittest.main()
