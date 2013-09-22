#!/usr/bin/env python
#encoding=utf-8


import time,os,sys
from FlwUtil import loadconfig

def log_error(errorinfo):
	if(loadconfig('LOG','ERROR') == '0'):
		return

	logdir = loadconfig('DIRS','PY_FLW_LOG') + time.strftime('%Y/%m/%d', time.localtime()) + '/'
	if not os.path.exists(logdir):
		os.system('mkdir -p ' + logdir)

	logfile = logdir + "flwinfo.log"
	f = open(logfile, 'a')
	f.write('ERROR ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(errorinfo) + '\n')
	f.close()


def log_debug(debuginfo):
	if(loadconfig('LOG','DEBUG') == '0'):
		return

	logdir = loadconfig('DIRS','PY_FLW_LOG') + time.strftime('%Y/%m/%d', time.localtime()) + '/'
	if not os.path.exists(logdir):
			os.system('mkdir -p ' + logdir)

	logfile = logdir + "flwdebug.log"
	f = open(logfile, 'a')
	f.write('DEBUG ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(debuginfo) + '\n')
	f.close() 


def log_info(info):
	if(loadconfig('LOG','INFO') == '0'):
			return

	logdir = loadconfig('DIRS','PY_FLW_LOG') + time.strftime('%Y/%m/%d', time.localtime()) + '/'

	if not os.path.exists(logdir):
			os.system('mkdir -p ' + logdir)

	logfile = logdir + "flwnotes.log"
	f = open(logfile, 'a')
	f.write('INFO ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(info) + '\n')
	f.close()