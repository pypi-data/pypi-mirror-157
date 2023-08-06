# -*- coding: utf-8 -*-
"""Description: This module is used to provide email feature to all
other sub modules so that they can send email by a simple api.

Author: BriFuture

Modified: 2019/03/17 12:35
Modified: 2022/06/23 18 兼容新版本
"""


__version__ = '0.2.0'

import logging
import sqlalchemy
from datetime import datetime
logger = logging.getLogger('bff.email')

class EmailEntity( sqlalchemy.Model ):
    __tablename__ = 'email'
    id = sqlalchemy.Column( sqlalchemy.Integer, primary_key = True, autoincrement = True )
    to = sqlalchemy.Column( sqlalchemy.String( 255 ), nullable=False )
    content = sqlalchemy.Column( sqlalchemy.Text )
    time = sqlalchemy.Column( sqlalchemy.DateTime, default=datetime.now )
    subject = sqlalchemy.Column( sqlalchemy.String( 255 ) )
    ip = sqlalchemy.Column( sqlalchemy.String( 255 ) ) # sender ip
    type = sqlalchemy.Column( sqlalchemy.String( 255 ) )
    remark = sqlalchemy.Column( sqlalchemy.String( 255 ) )
    session = sqlalchemy.Column( sqlalchemy.String( 255 ) )

    def to_dict(self):
        di = {
            'id': self.id,
            'to': self.to,
            'content': self.content,
            'time': self.time.timestamp(),
            'subject': self.subject,
            'ip': self.ip,
            'type': self.type,
            'remark': self.remark,
            'session': self.session,            
        }
        return di
    def is_valid(self):
        if len(self.to) == 0:
            # logger.warning("Remote address not set in an email")
            return False
        if len(self.subject) == 0:
            # logger.warning("Empty subject found in an email")
            return False
        if len(self.content) == 0:
            # logger.warning("Empty content found in an email")
            return False
        return True

    def __repr__(self):
        return "<Email to: {}, subject: {}, content: {}, time: {}>"\
            .format(self.to, self.subject, self.content, self.time)

from queue import Queue
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


class MailSender(object):
    """``EmailSender`` is a wrapper of ``email`` module
    """
    def __init__(self, host, account, password, port, *args, **kwargs):
        self._host = host
        self._account = account
        self._password = password
        self._port = port
        self.server = smtplib.SMTP_SSL(self._host, self._port)

    def reset_server(self):
        self.server = smtplib.SMTP_SSL(self._host, self._port)

    def send(self, email: EmailEntity):
        msg = MIMEText(email.content, 'html', 'utf-8')
        msg['Subject'] = Header(email.subject, 'utf-8').encode()
        msg['From'] = self.__format_addr('SSPY-Mgr <{}>'.format(self._account))
        msg['To'] = self.__format_addr('Receiver <{}>'.format(email.to) )
        self.server.connect( self._host, self._port )
        # self.server.starttls()
        self.server.ehlo()
        self.server.login( self._account, self._password)
        self.server.sendmail( self._account, email.to, msg.as_string())
        self.server.quit()

    def __format_addr( self, s ):
        name, addr = parseaddr(s)
        return formataddr( ( Header(name, 'utf-8').encode(), addr ) )

from flask import jsonify 
def admin_getAllEmails():
    emails = EmailEntity.query.all()
    em = [e.to_dict() for e in emails]
    return jsonify({'status': 'success', 'emails': em})
from .utils import getPageArgs

def admin_getPageEmails():
    page, per_page = getPageArgs()
    emails = EmailEntity.query.paginate(page=page, per_page=per_page)
    return jsonify({'status': 'success', 'emails': emails})


class EmailManager(object):
    """Used for generating ``Email`` database record and sending email
    config
    {
        email: # sender email name
            account
            password
            host
            port
        debug: whether to debug
    }
    """
    def __init__(self, config, database, *args, **kwargs):
        # self.config = config
        email = config.email
        self.db = database
        self._test = config.debug
        self._host = email[ 'host' ]
        if self._host == 'smtp host':
            logger.warning( '[Email] Please Place Your smtp account into config file')
            import sys
            sys.exit( 1 )
        if( self._host == None ) :
            raise ValueError

        self.sender = MailSender(self._host, email[ 'account' ], email[ 'password' ], email.get( 'port', 465))
        self._process_pending = False
        self._sendQueue = Queue()

    def registerApi(self, api):
        api.add_url_rule('/email/getAll', view_func=admin_getAllEmails, methods=['GET', 'POST'])
        api.add_url_rule('/email/getPage', view_func=admin_getPageEmails, methods=['GET', 'POST'])
        logger.info("Email Api registered")
        
    def add_email(self, email : EmailEntity):
        """append an email object to queue, the mail will be sent at proper time,
        Empty subject or content is not allowed.
        
        email = EmailEntity(
            to=to,
            subject=subject,
            content=content,
            type=type,
            remark="pending")
        """
        if email.is_valid():
            self._sendQueue.put(email)
    
    def send(self, email: EmailEntity):
        self._sendQueue.put(email)

    def checkRemain(self):
        """Check it if there exists any pending emails that need to be sent
        """
        if self._sendQueue.empty():
            self._checkPending()
            return
        email = self._sendQueue.get()
        self._send_email(email, commit=True)

    def _checkPending(self):
        if self._process_pending == True:
            return
        self._process_pending = True
        emails = EmailEntity.query.filter_by(remark='pending').all()
        for e in emails:
            self._send_email(e)
        self.db.session.commit()
        self._process_pending = False

    def _send_email(self, email: EmailEntity, commit = False):
        """Do the action of sending email, 
        ``commit`` set True to invoke db session commit.
        """
        logger.debug("Geting email and ready to send it")
        if self._test:
            email.remark = "debugNotSend"
            logger.info("Email generated but not send: {}".format(email))
        else:
            self.sender.reset_server()
            self.sender.send(email)
            email.remark = "sent"
            logger.debug("Email generated and send: {}".format(email))
        with self.db.session as sess:
            sess.add(email)
            if commit:
                sess.commit()

