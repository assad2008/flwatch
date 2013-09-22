#!/usr/bin/python
#encoding=utf-8

import sys,os,time
sys.path.append('./lib')
from FlwSendMailLib import sendmail
from FlwSendMsmLib import sendMsg
from FlwMsmNotice import *
from FlwNoticeAlarm import *
from FlwLogLib import *
from FlwMysqlLib import *
from FlwUtil import checkip,loadconfig
from urlparse import urlparse
from FlwDaemon import FlwDaemon

def getIp(domain):
	import socket
	myaddr = socket.getaddrinfo(domain,'http')[0][4][0]
	return myaddr
	
def get_server_ip(url):
	if checkip(url):
		return url
	else:
		parsed_uri = urlparse( url )
		domain = parsed_uri.netloc
		return getIp(domain.split(':')[0])

def get_user_email_and_cellphone(id):
	ret = exce_select('fjk_users',"user_id = %s AND status = 1" % int(id))
	try:
		return ret[0][3],ret[0][4]
	except:
		return None
	
def sendalarmofemail(iteminfo,level = 1,reason = '请求异常'):
	item_name = iteminfo[1]
	item_name = item_name
	item_type = iteminfo[3]
	itemobject = get_server_ip(iteminfo[8])
	if item_type == 'http':
		ret = website_alarm_content(item_name,itemobject,reason,level)
	elif item_type == 'ping':
		ret = ping_alarm_content(item_name,itemobject,level)
	elif item_type == 'app':
		ret = custom_alarm_content(item_name,itemobject,reason,level)
	return ret

def sendalarmofsms(iteminfo,level = 1,reason = '请求异常'):
	item_name = iteminfo[1]
	item_name = item_name
	item_type = iteminfo[3]
	itemobject = get_server_ip(iteminfo[8])
	if item_type == 'http':
		ret = website_alarm_msm_content(item_name,itemobject,reason,level)
	elif item_type == 'ping':
		ret = ping_alarm_msm_content(item_name,itemobject,level)
	elif item_type == 'app':
		ret = custom_alarm_msm_content(item_name,itemobject,reason,level)
	return ret

def sendnorice(itemid,level = 1,reason = ''):
	ret = exce_select('fjk_monitors',"itemid = %d AND is_stop = 0 AND status = 1" % itemid)[0]
	try:
		smstext = sendalarmofsms(ret,level,reason)[0]
		emailtext = sendalarmofemail(ret,level,reason)
		noticer = ret[10]
		noticertuple = noticer.split(',')
		mailsenderlist = []
		for i in noticertuple:
			userconnectinfo = get_user_email_and_cellphone(i)
			emailaddress = userconnectinfo[0]
			cellhpone = userconnectinfo[1]
			mailsenderlist.append(emailaddress)
			ret = sendMsg(cellhpone,smstext)
		eret = sendmail(mailsenderlist,emailtext[1],emailtext[0])
		return True
	except:
		return False

def noricelist():
	ret = exce_select("SELECT * FROM fjk_monitor_alarm WHERE is_read=0")
	return ret


def noticerun():
	lists = noricelist()
	for i in lists:
		noticeid = i[0]
		itemid = i[1]
		reason = i[5]
		level = i[4]
		sendnorice(itemid,level,reason)
		exec_sql("UPDATE fjk_monitor_alarm SET is_read=1,is_notice=1 WHERE id=%d" % noticeid)

	
class FlwNotice(FlwDaemon):
	def _run(self):
		while True:
			noticerun()
			time.sleep(120)
	
if __name__ == '__main__':	
	
	daemon = FlwNotice(loadconfig('DIRS','ROOT') + 'FlwMsmEmailNotice.pid')
	if len(sys.argv) == 2:
		if 'START' == (sys.argv[1]).upper():
			daemon.start()
		elif 'STOP' == (sys.argv[1]).upper():
			daemon.stop()
		elif 'RESTART' == (sys.argv[1]).upper():
			daemon.restart()
		else:
			print "Unknow Command!"
			print "Usage: %s start|stop|restart" % sys.argv[0]
			sys.exit(2)
		sys.exit(0)
	else:
		print "Usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(0)
	
	
	
	