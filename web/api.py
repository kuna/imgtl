#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, request
from flask.ext.restful import Api, Resource

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from imgtl.db import *
from imgtl.const import *
import imgtl.lib


app = Flask(__name__)
app.config.from_pyfile('imgtl.cfg')
db.init_app(app)
db.app = app
api = Api(app)

def success(data):
    return {'status': 'success', 'data': data}

def error(msg):
    return {'status': 'error', 'error': msg}

class Upload(Resource):
    def post(self):
        user = None
        if 'token' in request.form:
            user = User.query.filter_by(token=request.form['token']).first()
            if not user:
                return error('wrongtoken')
        if 'image' not in request.files:
            return error('imagenotattached')
        f = request.files['image']
        if not f:
            return error('wrongimage')
        fn = f.filename
        fs = f.read();
        if not imgtl.lib.is_image(fs):
            return error('notimage')
        code = "%s.%s" % (imgtl.lib.md5(fs), imgtl.lib.get_ext(fn))
        image = Image.query.filter_by(code=code).first()
        if not image:
            image = Image(server=SERVER_S1, code=code)
            fp = imgtl.lib.get_spath(app.config['UPLOAD_DIR'], code)
            if not os.path.exists(os.path.dirname(fp)):
                os.makedirs(os.path.dirname(fp))
            with open(fp, 'w') as f:
                f.write(fs)
        desc = request.form['desc'] if 'desc' in request.form else None
        upload = imgtl.db.Upload(object=image, user=user, title=fn, desc=desc)
        while True:
            try:
                upload.url = imgtl.lib.make_url()
                db.session.add(upload)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue
            else:
                break
        db.session.add(image)
        db.session.commit()
        return success({'url': {'page': 'https://img.tl/%s' % upload.url, 'direct': 'https://img.tl/%s.%s' % (upload.url, image.ext), 'original': image.original_url}})

class Url(Resource):
    def get(self, url):
        upload = imgtl.db.Upload.query.filter_by(url=url).first()
        if not upload:
            return error('nosuchupload')
        user = {'name': upload.user.name, 'profile_image_url': upload.user.profile_image_url} if upload.user else None
        return success({'url': {'page': 'https://img.tl/%s' % upload.url, 'direct': 'https://img.tl/%s.%s' % (upload.url, upload.object.ext), 'original': upload.object.original_url}, 'title': upload.title, 'desc': upload.desc, 'upload_at': upload.time.strftime('%s'), 'user': user, 'view_count': upload.view_count})


api.add_resource(Upload, '/upload')
api.add_resource(Url, '/url/<string:url>')

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=2561)
