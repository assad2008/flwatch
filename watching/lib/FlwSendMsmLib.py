#!/usr/bin/python
#encoding=utf-8

import os,sys
from FlwUtil import loadconfig
from FlwLogLib import *

def sendMsg(phonenuber , text):
	import requests
	requestsurl = 'http://sdk2.entinfo.cn/z_send.aspx'
	payload = {'sn' : loadconfig('MSMID','SN'),'pwd' : loadconfig('MSMID','SENDER'), 'mobile' : phonenuber, 'content' : text.decode('utf8').encode('gbk')}
	ret = requests.get(requestsurl,params = payload ,timeout = 2 )
	if ret.status_code == 200:
		if ret.text == '1':
			return True
		else:
			log_error("sendMsg(): " + str('Send MSM error') + ' err code: ' + str(ret.text))
			return ret.text
	else:
		return False