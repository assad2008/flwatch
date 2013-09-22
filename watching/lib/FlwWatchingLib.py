#!/usr/bin/python
#encoding=utf-8

import sys,os,signal,simplejson,Queue,time
from FlwLogLib import *
from FlwAppLib import *
from FlwMysqlLib import *
from FlwWebsiteLib import website_alive_check
from FlwPingLib import ping_alive_check,Ping
from FlwUtil import checkip,loadconfig

repeatnums = int(loadconfig('MONITORREPEAT','nums'))
repeattimesleep = int(loadconfig('MONITORREPEAT','timesleep'))

def get_timestamp():
	return int(time.time())
	
def watching_item_inQueue(iteminfo):
	qitem = Queue.Queue()
	for info in iteminfo:
		qitem.put(info)
	return qitem
	

def watching_item_outQueue(qitem):
	try:	
		if qitem.qsize() != 0:
			itemlist = qitem.get(block = False)
		else:
			itemlist = None
		return itemlist
	except Exception as e:
		return None
		

def get_watch_lists():
	times = int(time.time())
	ret = exce_select('fjk_monitors',"is_stop = 0 AND status = 1")
	return ret

def get_app_onwer_phone(app_id):
	appinfo = exce_select('jk_appphone',"app_id = '%d'" % int(app_id))
	phone = appinfo and appinfo[2] or None
	return phone
	
def watching_app(witem):
	itemid = witem[0]
	url = witem[8] or None
	baowen = witem[9] 
	if url == None:
		return
	baowen = simplejson.loads(baowen)
	postcontent = simplejson.dumps(baowen)
	conmand = baowen.get('command')
	status = False
	reason = ''
	for i in range(0,repeatnums):
		try:
			ret = sendpost(url,postcontent)
			if ret == 9999:
				reason = 'request fail'
				status = False
			elif ret == None:
				reason = 'json text read fail'
				status = False
			else:
				try:
					returncommand = ret.get('command') or None
				except:
					reason = ret
					returncommand = None
				if  returncommand == conmand:
					return True
				else:
					reason = ret
					status = False
			time.sleep(repeattimesleep)
		except:
			continue
	return status,reason

def watching_website(witem):
	item_id = witem[0]
	url = witem[8] or None
	itemconfig = {}
	itemconfig['ip'] = ''
	status = False
	reason = ''
	for i in range (0,repeatnums):
		try:
			if status == False:
				ret = website_alive_check(url,itemconfig)
				if ret[0] == '0':
					if ret[2] in (200,301,302):
						return True
					else:
						reason = ret[2]
						status = False
						break
				else:
					reason = 'request fail'
					status = False
			time.sleep(repeattimesleep)
		except:
			continue
	return status,reason
	
def watching_ping(witem):
	from urlparse import urlparse
	url = witem[8] or None
	status = False
	if checkip(url):
		for i in range(0,repeatnums):
			try:
				ret = ping_alive_check(url)
				if ret[0] == '0':
					return True
				else:
					status = False 
				time.sleep(repeattimesleep)
			except:
				continue
	else:
		parsed_uri = urlparse( url )
		domain = parsed_uri.netloc
		for i in range(0,repeatnums):
			try:
				ret = ping_alive_check(domain.split(':')[0])
				if ret[0] == '0':
					return True
				else:
					status = False
			except:
				continue
			time.sleep(repeattimesleep)
	return status
	
def do_watching_app(item):
	item_id = item[0]
	log_debug(item_id)
	timestamp = get_timestamp()
	if item[13] > timestamp:
		return
	try:
		ret = watching_app(item)
	except Exception as e:
		log_error('do_watching_app ' + str(e))
		return
	nextchecktime = timestamp + item[4]
	fault_time = item[18]
	try:
		if ret == True:
			if fault_time > 0:
				exec_sql("UPDATE fjk_monitors SET fault_time=0,next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
				exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,3,'项目恢复正常',timestamp))
			else:
				exec_sql("UPDATE fjk_monitors SET next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
		else:
			reason = ret[1]
			exec_sql("UPDATE fjk_monitors SET alar_num=alar_num+1,fault_time=%d,next_check_time=%d WHERE itemid=%d" % (timestamp,nextchecktime,item_id))
			exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,1,reason,timestamp))
	except Exception as e:
		log_error('do_watching_app sql' + str(e))
	
def do_watching_http(item):
	item_id = item[0]
	timestamp = get_timestamp()
	if item[13] > timestamp:
		return
	try:
		ret = watching_website(item)
	except Exception as e:
		log_error('do_watching_http ' + str(e))
		return
	nextchecktime = timestamp + item[4]
	fault_time = item[18]
	try:
		if ret == True:
			if fault_time > 0:
				exec_sql("UPDATE fjk_monitors SET fault_time=0,next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
				exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,4,'项目恢复正常',timestamp))
			else:
				exec_sql("UPDATE fjk_monitors SET next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
		else:
			reason = ret[1]
			exec_sql("UPDATE fjk_monitors SET alar_num=alar_num+1,fault_time=%d,next_check_time=%d WHERE itemid=%d" % (timestamp,nextchecktime,item_id))
			exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,1,reason,timestamp))
	except Exception as e:
		log_error('do_watching_http sql' + str(e))
	
def do_watching_ping(item):
	item_id = item[0]
	timestamp = get_timestamp()
	if item[13] > timestamp:
		return
	try:
		ret = watching_ping(item)
	except Exception as e:
		log_error('do_watching_ping ' + str(e))
		return
	nextchecktime = timestamp + item[4]
	fault_time = item[18]
	try:
		if ret == True:
			if fault_time > 0:
				exec_sql("UPDATE fjk_monitors SET fault_time=0,next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
				exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,4,'项目恢复正常',timestamp))
			else:
				exec_sql("UPDATE fjk_monitors SET next_check_time=%d WHERE itemid=%d" % (nextchecktime,item_id))
		else:
			reason = 'time out'
			exec_sql("UPDATE fjk_monitors SET alar_num=alar_num+1,fault_time=%d,next_check_time=%d WHERE itemid=%d" % (timestamp,nextchecktime,item_id))
			exec_sql("INSERT INTO fjk_monitor_alarm (itemid,mon_name,alarm_time,alarm_level,reason,fault_time) VALUES (%d,'%s',%d,%d,'%s',%d)" % (item_id,item[1],timestamp,1,reason,timestamp))
	except Exception as e:
		log_error('do_watching_ping sql' + str(e))