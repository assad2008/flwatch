#!/usr/bin/env python
#encoding=utf-8

import time
import os,sys
import commands
from threading import Lock
from Queue import Queue


def loadconfig(item,key):
	import ConfigParser
	cf = ConfigParser.ConfigParser()
	inipath = '/fljiankong/watching/conf/config.ini'
	cf.read(inipath)
	try:
		return cf.get(item,key)
	except:
		return None

def get_cur_info():
	'''
	返回当前函数所在文件名，函数行及行号
	'''
	try:
		raise Exception
	except:
		f = sys.exc_info()[2].tb_frame.f_back
	return (f.f_code.co_filename,f.f_code.co_name, f.f_lineno)

def write_log(type, data ,curinfo = get_cur_info()):
	if int(loadconfig('LOG',type.upper())) == 0 :
		return 
	logdir = loadconfig('DIRS','PY_FLW_LOG') + time.strftime('%Y_%m', time.localtime()) + '/'
	
	if not os.path.exists(logdir):
		os.system('mkdir -p ' + logdir)
	
	log_file = logdir + time.strftime('%Y_%m_%d', time.localtime()) + '_sysinfo.log.'+type
	f = open(log_file, 'a')
	f.write(type + ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(data) + ' filename:'+curinfo[0]+',funcname:'+curinfo[1]+',line:'+str(curinfo[2])+'\n')
	f.close()
	
def write_Thread_log(type,subtype,data):
	if int(loadconfig('LOG',type.upper())) == 0 :
		return 
	
	logdir = loadconfig('DIRS','PY_FLW_LOG') + time.strftime('%Y_%m', time.localtime()) + '/Thread/'
	
	if not os.path.exists(logdir):
		os.system('mkdir -p ' + logdir)
	
	log_file = logdir + time.strftime('%Y_%m_%d', time.localtime()) + '_' + type+ '_' + subtype + '_debug.log'
	f = open(log_file, 'a')
	f.write(type + ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(data) + '\n')
	f.close()
	
def checkip(address):
	parts = address.split(".")
	if len(parts) != 4:
		return False
	for item in parts:
		try:
			if not 0 <= int(item) <= 255:
				return False
		except:
			return False
	return True