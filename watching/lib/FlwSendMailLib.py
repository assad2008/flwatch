#!/usr/bin/python
#encoding=utf-8

# by chenchangming
import os,sys
import smtplib
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from FlwUtil import loadconfig
from FlwLogLib import *

def smtp_conn(host, port, user, password):
    ''' smtp connection
        param host: str
        param port: int
        param user: str
        param password: str
        return: smtplib.SMTP instance
    '''
    try:
        session = smtplib.SMTP(host, port, timeout = 60)
        session.login(user, password)
        return session
    except smtplib.SMTPConnectError as msg:
        log_error("smtp_conn():" + str('Connect to server Error, Please check host and port!'))
        return False
    except smtplib.SMTPAuthenticationError as msg:
        log_error("smtp_conn():" + str('Authentication Failure.  Please check username and password!'))
        return False
		
def sendMail(session, sender, recipient, subject, body):
    ''' use smtp send email
        param session: smtplib.SMTP instance
        param sender: str
        param recipient: list
        param subject: str
        param body: string
        return: bool
    '''
    msg = MIMEMultipart()
    msg['to'] = str(','.join(recipient))
    msg['from'] = sender
    msg['subject'] = Header(subject, 'utf-8') 
    msg.attach(MIMEText(body,_subtype = 'html',_charset = 'utf-8'))
    try:
        status = session.sendmail(sender, recipient, msg.as_string())
        if status:
            return False
        else:
            return True
    except (smtplib.SMTPHeloError,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPSenderRefused,
            smtplib.SMTPDataError) as msg:
        log_error("sendMail():" + str(msg))
        return False
		

def sendmail(to, subject, body):
	session = smtp_conn(loadconfig('EMAIL','SMTP_SERVER'), int(loadconfig('EMAIL','PORT')), loadconfig('EMAIL','USER'), loadconfig('EMAIL','PASSWD'))
	if session:
		ret = sendMail(session, loadconfig('EMAIL','FROM'), to, subject, body)
		return ret
	else:
		log_error("smtp_conn():" + str('Email session Failure.  Please check username and password!'))