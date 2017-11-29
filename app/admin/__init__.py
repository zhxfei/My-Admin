# encoding: utf-8

from flask import Blueprint


admin = Blueprint('admin', __name__)

import app.admin.view

