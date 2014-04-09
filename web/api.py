#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, request
from flask.ext.restful import Api, Resource, reqparse

from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
from imgtl.common import get_upload, do_upload_image, do_delete_image
import imgtl.lib


app = Flask(__name__)
app.config.from_pyfile('imgtl.cfg')

db.init_app(app)
db.app = app
log_db.init_app(app)
log_db.app = app

api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('X-IMGTL-TOKEN', type=str, location='headers', dest='token')
parser.add_argument('desc', type=unicode, location='form')
parser.add_argument('with_uploads', type=int, location='args')


def success(data):
    return {'status': 'success', 'data': data}

def error(msg):
    return {'status': 'error', 'error': msg}


class Upload(Resource):
    def post(self):
        args = parser.parse_args()
        f = request.files.get('file')
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


class Url(Resource):
    def get(self, url):
        upload = get_upload(url)
        if not upload or upload.deleted:
            return error('nosuchupload'), 404
        user = {'name': upload.user.name, 'profile_image_url': upload.user.profile_image_url} if upload.user else None
        return success({'type': upload.object.__tablename__, 'url': {'page': BASE_URL % upload.url, 'direct': upload.direct_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'user': user, 'view_count': upload.view_count})

    def delete(self, url):
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
                uploads.append({'type': upload.object.__tablename__, 'url': {'page': BASE_URL % upload.url, 'direct': upload.direct_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'view_count': upload.view_count})
            res['uploads'] = uploads
        return success({'user': res})


api.add_resource(Upload, '/upload')
api.add_resource(Url, '/url/<string:url>')
api.add_resource(UserInfo, '/user/info')

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=2561)
