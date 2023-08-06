# -*- coding: utf-8 -*-

"""Description: There are two main purpose of this module:
1. provide sqlalchemy as DB to other sub modules so they can define 
their database models even the database instance is not created yet.
2. provide a function called ``createDatabase`` to attach database to 
sqlalchemy, so it can get access to these databases (which would be sqlite
or mysql database).

Author: BriFuture

Modified: 2020/05/13 20:56
解决了 mysql 中 lost connection 的错误
@refrence 
    1. https://towardsdatascience.com/use-flask-and-sqlalchemy-not-flask-sqlalchemy-5a64fafe22a4
    2. https://github.com/pallets/flask-sqlalchemy/
    3. https://docs.sqlalchemy.org/en/13/orm/contextual.html

Modified: 2020/06/19 replace property session with scoped_session_maker
Modified: 2021/10/21
    解决 context 中的 内存泄漏问题

Usage
```
from . import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % SQLITE_DATABASE_LOC
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy( app )
```
"""

__version__ = '0.3.0'
import math

def paginate(self, page=None, per_page=None, to_dict=True):
    """
    分页函数
    :param self:
    :param page:
    :param per_page:
    :return:
    """
    if page is None:
        page = 1

    if per_page is None:
        per_page = 20

    items = self.limit(per_page).offset((page - 1) * per_page).all()

    if not items and page != 1:
        return {'total': 0, 'page': page, 'error': 'no such items'}
        
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = self.order_by(None).count()
    
    if to_dict:
        ditems = [item.to_dict() for item in items]
    else:
        ditems = items

    return {
        'page': page, 
        'per_page': per_page, 
        'total': total, 
        'items': ditems
    }
    # return Pagination(self, page, per_page, total, items)

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, as_declarative, declared_attr
# Model = declarative_base()

@as_declarative()
class _Model(object):
    # @declared_attr
    # def query():
    #     return 
    query = None
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    # id = Column(Integer, primary_key=True)
sqlalchemy.Model = _Model
orm.Query.paginate = paginate

# Database Proxy
import time
import logging, sys
import threading
from bffacilities.utils import createLogger

class DatabaseV1(object):
    """Recommond Usage: 
    ```
    db = Database(dbname)  # dbname sqlite:///
    db.create_all()
    with db as sess:
        sess.add(Record())
        sess.commit()
    ```
    But it is compatible with flask_sqlalchemy, 
    but scopefunc must be set when construct database instance, @see create_engine
    """
    Column = sqlalchemy.Column
    Integer = sqlalchemy.Integer
    SmallInteger = sqlalchemy.SmallInteger
    BigInteger = sqlalchemy.BigInteger
    Boolean = sqlalchemy.Boolean
    Enum = sqlalchemy.Enum
    Float = sqlalchemy.Float
    Interval = sqlalchemy.Interval
    Numeric = sqlalchemy.Numeric
    PickleType = sqlalchemy.PickleType
    String = sqlalchemy.String
    Text = sqlalchemy.Text
    DateTime = sqlalchemy.DateTime
    Date = sqlalchemy.Date
    Time = sqlalchemy.Time
    Unicode = sqlalchemy.Unicode
    UnicodeText = sqlalchemy.UnicodeText
    LargeBinary = sqlalchemy.LargeBinary
    # MatchType = sqlalchemy.MatchType
    # SchemaType = sqlalchemy.SchemaType
    ARRAY = sqlalchemy.ARRAY
    BIGINT = sqlalchemy.BIGINT
    BINARY = sqlalchemy.BINARY
    BLOB = sqlalchemy.BLOB
    relationship = sqlalchemy.orm.relationship
    ForeignKey = sqlalchemy.ForeignKey
    Table = sqlalchemy.Table

    Model = _Model
    create_all = _Model.metadata.create_all
    drop_all = _Model.metadata.drop_all
    

    def __init__(self, dbname, logger=None,
        pool_recycle = 600, **kwargs):
        """db used to replace flask_sqlalchemy to provide more convinient ways to manage app
        @pool_recycle 默认的刷新时间为 10 分钟
        @Session use Session instead session property to get scoped session, 
            but scopefunc must be set before Session could be used
        @see createEngine

        kwargs 
            scopefunc  is used for flask app
            delay_engine_create is removed
        """
        if logger is None: logger = logging.getLogger("bff.db")
        self.logger = logger
        self.engine = None
        if dbname is not None:
            self.create_engine(dbname, pool_recycle, **kwargs)

    def create_engine(self, dbname, pool_recycle, **kwargs):
        """::kwargs:: 
        scopefunc
            if flask is used, 
            `scopefunc=_app_ctx_stack.__ident_func__`  or `scopefunc=_request_ctx_stack.__ident_func__` 
            could be passed in kwargs
        """
        if self.engine is not None:
            raise ValueError("Currently Not Support Multiple engine")

        scopefunc = kwargs.pop('scopefunc', None)
        engine = sqlalchemy.create_engine(dbname, pool_recycle=pool_recycle, **kwargs)
        _Model.metadata.bind = engine
        self._SessionFactory = orm.sessionmaker(bind=engine)
        # _Session is the scoped session maker
        self.Session = orm.scoped_session(self._SessionFactory, scopefunc=scopefunc)
        # used for compatibility with flask_sqlalchemy, session is scoped
        _Model.query = self.Session.query_property()

        self.engine = engine
        self._locks = {}
    
    def __del__(self):
        self.done()
    
    @property
    def session(self):
        """compat with flask_sqlalchemy
        """
        return self.Session()


    def check_sessions(self):
        # remove useless sessions
        pass

    @staticmethod
    def valid_session(sess):
        try:
            # Try to get the underlying session connection, If you can get it, it's up
            connection = sess.connection()
            # connection.close()
        except:
            return False
        return True

    def done(self):
        self.Session.remove()

class Database(DatabaseV1):
    pass

# Database Proxy
def createDatabase(dbname, **kwargs):
    """create instance of sqlalchemy Database
    """
    raise ValueError("This Api has been deprecated")