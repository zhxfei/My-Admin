from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os.path
import pymysql

app = Flask(__name__)
db = SQLAlchemy(app)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:zhxfei..192@localhost/admin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '387c335e2ba847b68fad8ddf8b819752'
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/upload_files')

from app.admin import admin as admin_blue_print
app.register_blueprint(admin_blue_print)


#
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('admin/404.html'), 404

