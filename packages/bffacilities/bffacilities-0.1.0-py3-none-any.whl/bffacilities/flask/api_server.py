import logging
import os.path as osp
from flask import Flask, request
import sys
from bffacilities.dbmodel import Database
from datetime import datetime
import flask_login
from flask_login import LoginManager, current_user, \
    logout_user, login_required
from flask import render_template, redirect, url_for
from flask import session, request, jsonify

logger = logging.getLogger("bff.api")
class FlaskApplication(Flask):

    def __init__(self, *args, **kwargs):
        super(FlaskApplication, self).__init__(*args, **kwargs)
        self.logger = logger
        self.db = None
        self.sio = None

        self.config['SESSION_TYPE'] = 'sqlalchemy'
        self.config['CORS_SUPPORTS_CREDENTIALS'] = True

    def init(self, config):
        self._app_config = config
        if config.FLASK_COMPRESS_JS:
            self.add_url_rule("/static/js/<path:path>", view_func=send_compressed_js)
        self.getDb()
        self.config['SESSION_SQLALCHEMY'] = self.db
    
    def init_login_feature(self):
        self.login_mgr = LoginManager(self)
        self.register_error_handler(404, handle_web_error)
        self.add_url_rule('/', 'index', auth_index, methods=['GET'])
        self.add_url_rule('/index', 'auth_index', auth_index, methods=['GET'])
        self.add_url_rule('/login', 'auth_login', auth_login, methods=['GET'])
        
        self.add_url_rule('/api/logout', 'userlogout', user_logout, methods=['GET', 'POST'])

    def getDb(self, **kwargs):
        if self.db:
            return self.db
        config = self._app_config
        if config.DB_TYPE == "SQLITE":
            databasename = f"sqlite:///{config.DB_NAME}"
        elif config.DB_TYPE == "MYSQL":
            driver = "mysql+pymysql"
            databasename = f"{driver}://{config.DB_Account}:{config.DB_Passwd}@{config.DB_Address}:{config.DB_Port}/{config.DB_DB}?charset=utf8mb4"
        else:
            raise ValueError("Not Supported DB Type")
        # kwargs["encoding"] = 'utf8mb4'
        from flask import _request_ctx_stack
        db = Database(databasename, pool_recycle=7200, scopefunc=_request_ctx_stack.__ident_func__, **kwargs)
        db.create_all()
        self.db = db
        return db
def handle_web_error(e):
    return redirect(url_for("auth_login"))

def auth_index():
    if not current_user.is_authenticated:
        logger.info("User not authenticated")
        return redirect(url_for("auth_login"))
    return render_template('index.html')

def auth_login():
    return render_template('login.html')
    
def user_logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({"status": "success"})
    return redirect(url_for("auth_login"))

import flask_admin
class MyAdminIndexView(flask_admin.AdminIndexView):

    @flask_admin.expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('auth_login'))
        return super().index()
        

from flask import send_from_directory        
def send_compressed_js(path):
    path += ".gz"
    response = send_from_directory("templates/static/js", path)
    response.headers['Content-Encoding'] = 'gzip'
    return response

def after_request(response):
    accept_encoding = request.headers.get('Accept-Encoding', '')

    if response.status_code < 200 or \
        response.status_code >= 300 or \
        response.direct_passthrough or \
        'gzip' not in accept_encoding.lower() or \
        'Content-Encoding' in response.headers:
        return response
    # response.set_data(gzip_buffer.getvalue())
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.get_data())

    return response
