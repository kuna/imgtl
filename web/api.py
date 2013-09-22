#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, request
from flask.ext.restful import Api, Resource

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
from imgtl.common import do_upload_image, do_delete_image
import imgtl.lib


app = Flask(__name__)
app.config.from_pyfile('imgtl.cfg')

db.init_app(app)
db.app = app
log_db.init_app(app)
log_db.app = app

api = Api(app)


def success(data):
    return {'status': 'success', 'data': data}

def error(msg):
    return {'status': 'error', 'error': msg}


class Upload(Resource):
    def post(self):
        user = request.headers.get('X-IMGTL-TOKEN')
        if user:
            user = User.query.filter_by(token=user).first()
            if not user:
                return error('wrongtoken'), 403
        if 'image' not in request.files:
            return error('imagenotattached'), 400
        upload = do_upload_image(user, request.files['image'], request.form['desc'] if 'desc' in request.form else None)
        if isinstance(upload, str):
            return error(upload), 403
        else:
            return success({'url': {'page': 'https://img.tl/%s' % upload.url, 'direct': 'https://img.tl/%s.%s' % (upload.url, upload.object.ext), 'original': upload.object.original_url}}), 201


class Url(Resource):
    def get(self, url):
        upload = imgtl.db.Upload.query.filter_by(url=url).first()
        if not upload or upload.deleted:
            return error('nosuchupload'), 404
        user = {'name': upload.user.name, 'profile_image_url': upload.user.profile_image_url} if upload.user else None
        return success({'url': {'page': 'https://img.tl/%s' % upload.url, 'direct': 'https://img.tl/%s.%s' % (upload.url, upload.object.ext), 'original': upload.object.original_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'user': user, 'view_count': upload.view_count})

    def delete(self, url):
        token = request.headers.get('X-IMGTL-TOKEN')
        if not token:
            return error('notoken'), 403
        user = User.query.filter_by(token=token).first()
        if not user:
            return error('wrongtoken'), 403
        res = do_delete_image(user, url)
        if res == 'success':
            return {'status': 'success'}
        else:
            return error(res), 403

class UserInfo(Resource):
    def get(self):
        token = request.headers.get('X-IMGTL-TOKEN')
        if not token:
            return error('notoken'), 403
        user = User.query.filter_by(token=token).first()
        if not user:
            return error('wrongtoken'), 403
        return {'name': user.name, 'email': user.email, 'profile_image_url': user.profile_image_url, 'uploads_count': len(user.uploads.all())}


api.add_resource(Upload, '/upload')
api.add_resource(Url, '/url/<string:url>')
api.add_resource(UserInfo, '/user/info')

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=2561)
