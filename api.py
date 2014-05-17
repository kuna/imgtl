#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests

from flask import Flask, request
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.restful.reqparse import RequestParser, Argument
from werkzeug.datastructures import FileStorage

from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
from imgtl.common import get_upload, do_upload_image, do_delete_image
import imgtl.lib


app = Flask(__name__)
if os.environ.get('TESTING'):
    app.config.from_pyfile('.imgtl.tests.cfg')
else:
    app.config.from_pyfile('imgtl.cfg')

db.init_app(app)
db.app = app
log_db.init_app(app)
log_db.app = app

api = Api(app)
arg_token = Argument('X-IMGTL-TOKEN', type=str, location='headers', dest='token')


def success(data):
    return {'status': 'success', 'data': data}

def error(msg):
    return {'status': 'error', 'error': msg}

class Index(Resource):
    def get(self):
        return 'imgTL api service'

class Upload(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument(arg_token)
        parser.add_argument('file', type=FileStorage, location='files')
        parser.add_argument('desc', type=unicode, location='form')
        args = parser.parse_args()
        f = args['file']
        user = args['token']
        if user:
            user = User.query.filter_by(token=user).first()
            if not user:
                return error('wrongtoken'), 403
        if not f:
            return error('imagenotattached'), 400
        upload = do_upload_image(user, f, args['desc'])
        if isinstance(upload, str):
            return error(upload), 403
        else:
            return success({'url': {'part': upload.url, 'page': BASE_URL % upload.url, 'direct': upload.direct_url}}), 201

# http://tapbots.net/tweetbot/custom_media/
class TweetbotUpload(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('X-VERIFY-CREDENTIALS-AUTHORIZATION', type=str, location='headers', dest='authorization')
        parser.add_argument('X-AUTH-SERVICE-PROVIDER', type=str, location='headers', dest='authorization_url')
        parser.add_argument('media', type=FileStorage, location='files')
        parser.add_argument('message', type=unicode, location='form')
        parser.add_argument('source', type=unicode, location='form')
        args = parser.parse_args()
        if args['source'] != 'Tweetbot for iOS':
            return error('nottweetbot'), 403
        f = args['media']
        if not f:
            return error('imagenotattached'), 400
        headers = {'Authorization': args['authorization']}
        r = requests.get(args['authorization_url'], headers=headers)
        json = r.json()
        user = User.query.filter_by(oauth_uid=json['id']).first()
        message = '' if json['protected'] else args.get('message')
        desc = "%svia Tweetbot for iOS" % (('%s\r\n\r\n' % message) if message else '')
        upload = do_upload_image(user, f, desc)
        if isinstance(upload, str):
            return error(upload), 403
        else:
            return {'url': BASE_URL % upload.url}, 201

class Url(Resource):
    def get(self, url):
        upload = get_upload(None, url)
        if not upload or upload.deleted:
            return error('nosuchupload'), 404
        user = {'name': upload.user.name, 'profile_image_url': upload.user.profile_image_url} if upload.user else None
        return success({'type': upload.object.__tablename__, 'url': {'page': BASE_URL % upload.url, 'direct': upload.direct_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'user': user, 'view_count': upload.view_count, 'properties': upload.object.prop})

    def delete(self, url):
        parser = RequestParser()
        parser.add_argument(arg_token)
        args = parser.parse_args()
        if not args['token']:
            return error('notoken'), 403
        user = User.query.filter_by(token=args['token']).first()
        if not user:
            return error('wrongtoken'), 403
        res = do_delete_image(user, url)
        if res == 'success':
            return {'status': 'success'}
        else:
            return error(res), 403

class UserInfo(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument(arg_token)
        parser.add_argument('with_uploads', type=int, location='args')
        args = parser.parse_args()
        if not args['token']:
            return error('notoken'), 403
        user = User.query.filter_by(token=args['token']).first()
        if not user:
            return error('wrongtoken'), 403
        res = {'name': user.name, 'email': user.email, 'profile_image_url': user.profile_image_url, 'uploads_count': user.uploads.count()}
        if args['with_uploads'] == 1:
            uploads = []
            for upload in user.uploads:
                uploads.append({'type': upload.object.__tablename__, 'url': {'page': BASE_URL % upload.url, 'direct': upload.direct_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'view_count': upload.view_count, 'properties': upload.object.prop})
            res['uploads'] = uploads
        return success({'user': res})

api.add_resource(Index, '/')
api.add_resource(Upload, '/upload')
api.add_resource(TweetbotUpload, '/tweetbot')
api.add_resource(Url, '/url/<string:url>')
api.add_resource(UserInfo, '/user/info')

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=2561)
