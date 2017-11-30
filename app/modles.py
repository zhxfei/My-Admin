# encoding: utf-8
from app import db

# from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# import os.path
# import pymysql
#
# app = Flask(__name__)
# db = SQLAlchemy(app)
# app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:zhxfei..192@localhost/admin'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))
    face = db.Column(db.String(255))
    add_time = db.Column(db.DateTime, default=datetime.now())
    entry_time = db.Column(db.DateTime, default=datetime.now())
    sex = db.Column(db.String(255))
    department_id = db.Column(db.Integer)
    info = db.Column(db.Text)
    is_admin = db.Column(db.Boolean)
    state = db.Column(db.String(255))

    def __repr__(self):
        return '<User: %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    mail_sender = db.Column(db.String(100))
    mail_receiver = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    time = db.Column(db.DateTime)

    def __repr__(self):
        return '<mail_sender: %r mail_receiver: %r subject: %r time: %r >' % (
            self.mail_sender, self.mail_receiver, self.subject, self.time)


class SyncLog(db.Model):
    __tablename__ = 'synclog'
    id = db.Column(db.Integer, primary_key=True)
    ptr = db.Column(db.Integer)
    update_time = db.Column(db.DateTime, default=datetime.now())
    has_view = db.Column(db.Boolean)

    def __repr__(self):
        return '<Ptr: %r>' % self.ptr


class RecordInfo(db.Model):
    __tablename__ = 'record_info'
    id = db.Column(db.Integer, primary_key=True)
    sp_id = db.Column(db.String(100))
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
    type = db.Column(db.String(100))
    monitor_status = db.Column(db.String(100))
    updated_time = db.Column(db.DateTime)
    ttl = db.Column(db.String(100))
    use_status = db.Column(db.Boolean)
    domain_name = db.Column(db.String(100))

    def __repr__(self):
        return '<sp_id: %r name: %r value: %r type: %r monitor_status: %r updated_time: %r ' \
               'ttl: %r  use_status: %r  domain_name: %r >' % (
                   self.sp_id, self.name, self.value, self.type, self.monitor_status, self.updated_time, self.ttl,
                   self.use_status, self.domain_name)

# db.drop_all()
# db.create_all()
# user = User(
#     name='zhxfei',
#     pwd='pbkdf2:sha256:50000$DGQvoDOb$66f4f98e5b4ad67f166e84fe9d4a10ada88ef987debc238fe49b0a1aba6a46fa',
#     sex='男',
#     department_id=1,
#     info='互动娱乐部',
#     is_admin=True
# )
# db.session.add(user)
# db.session.commit()
