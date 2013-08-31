#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from urllib import urlencode

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.sql import functions as sqlfuncs
from sqlalchemy.orm import validates

from .const import *
from .lib import md5, get_spath, get_ext


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.Integer, primary_key=True)
    email = db.Column('user_email', db.String(120), unique=True, index=True, nullable=False)
    name = db.Column('user_name', db.String(16), unique=True, index=True, nullable=False)
    password = db.Column('user_password', db.String(60), nullable=False)
    token = db.Column('user_token', db.String(32), unique=True, index=True, nullable=True)

    @property
    def profile_image_url(self):
        url = 'https://secure.gravatar.com/avatar/%s?%s' % (md5(self.email.lower()), urlencode({'d': USER_DEFAULT_ICON}))
        return url

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % self.email


class Upload(db.Model):
    __tablename__ = 'upload'
    id = db.Column('upload_id', db.Integer, primary_key=True, index=True)
    url = db.Column('url', db.String(8), unique=True, index=True, nullable=True)
    object_id = db.Column('upload_obj_id', db.Integer, db.ForeignKey('object.object_id'), nullable=False)
    object = db.relationship('Object', backref=db.backref('uploads', lazy='dynamic'))
    user_id = db.Column('upload_user_id', db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    user = db.relationship('User', backref=db.backref('uploads', lazy='dynamic'))
    time = db.Column('upload_time', db.DateTime, nullable=False, default=sqlfuncs.now())
    view_count = db.Column('upload_view_count', db.Integer, nullable=False, default=0)
    title = db.Column('upload_title', db.String(120), nullable=False)
    desc = db.Column('upload_desc', db.String(320), nullable=True)
    nsfw = db.Column('upload_nsfw', db.Boolean, default=False)

    def __repr__(self):
        return '<Upload %r>' % self.id


class Object(db.Model):
    __tablename__ = 'object'
    id = db.Column('object_id', db.Integer, primary_key=True, index=True)
    code = db.Column('object_code', db.String(40), unique=True, nullable=False)
    discriminator = db.Column('type', db.Integer)
    __mapper_args__ = {'polymorphic_on': discriminator}


class Image(Object):
    __tablename__ = 'image'
    __mapper_args__ = {'polymorphic_identity': TYPE_IMAGE}
    id = db.Column('image_id', db.Integer, db.ForeignKey('object.object_id'), primary_key=True, index=True)
    server = db.Column('image_srv', db.Integer, nullable=False)

    @property
    def original_url(self):
        return OBJECT_URL[self.server] % get_spath('', self.code)

    @property
    def thumbnail_url(self):
        return OBJECT_URL[self.server] % get_spath('thumb', self.code)

    @property
    def ext(self):
        return get_ext(self.code)

    def __repr__(self):
        return '<Image %r>' % self.id


class File(Object):
    __tablename__ = 'file'
    __mapper_args__ = {'polymorphic_identity': TYPE_FILE}
    id = db.Column('file_id', db.Integer, db.ForeignKey('object.object_id'), primary_key=True, index=True)
    type = db.Column('file_type', db.Integer, nullable=False)

    def __repr__(self):
        return '<File %r>' % self.id


class Text(Object):
    __tablename__ = 'text'
    __mapper_args__ = {'polymorphic_identity': TYPE_TEXT}
    id = db.Column('text_id', db.Integer, db.ForeignKey('object.object_id'), primary_key=True, index=True)
    cont = db.Column('text_cont', db.Text, nullable=False)

    @validates('cont')
    def generate_code(self, key, cont):
        self.code = md5(cont)
        return cont

    def __repr__(self):
        return '<Text %r>' % self.id


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column('log_id', db.Integer, primary_key=True, index=True)
    target = db.Column('log_target', db.String(16), nullable=False)
    target_id = db.Column('log_target_id', db.Integer, nullable=False)
    ip = db.Column('log_by_ip', db.String(16), nullable=True)
    user = db.Column('log_by_user', db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    _user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))
