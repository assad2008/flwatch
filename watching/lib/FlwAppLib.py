#!/usr/bin/python
#encoding=utf-8

import os,sys
from FlwUtil import loadconfig
from FlwLogLib import *
import zlib
import StringIO
import gzip

def pack(string):
	output = StringIO.StringIO()
	output.write(string)
	return gzip.GzipFile(fileobj = output)
	
def unpack(string):
	output = StringIO.StringIO()
	output.write(string)
	return gzip.open(output)
	
def str2asc(string):
    data = []
    lenth = len(string)
    for i in range(lenth):
        data.append(ord(string[i]))
    return data
	
def asc2str(string):
    return ''.join([chr(i) for i in string])
	

def DE(string, cryptkeys = loadconfig('CRYPTKEY','CRYPTKEY')):
    s = str2asc(string)
    data = []
    for i in s:
        data.append(i ^ int(cryptkeys))
    string = asc2str(data)
    return string

def dopdata(data):
    result = DE(zlib.compress(data))
    if result:
        return result
    else:
        return False
		
def dordata(data):
    try:
      result = zlib.decompress(DE(data),16 + zlib.MAX_WBITS)
      return result
    except Exception as e:
      print e
      return None

def dorrdata(data):
	dedata = DE(data)
	decom_obj = zlib.decompressobj()
	str_obj1 = decom_obj.decompress(dedata)
	str_obj1 += decom_obj.flush()
	return str_obj1

def sendpost(url , data):
	import requests
	import simplejson
	postdata = dopdata(data)
	try:
		ret = requests.post(url,postdata,timeout = 5)
	except Exception as e:
		log_error("sendpost():" + str(e))
		return 9999
	if ret.status_code == 200:
		rdata = ret.content
		try:
			ddata = dorrdata(rdata[7:])
		except Exception as e:
			log_error("sendpost():" + str(e))
			ddata = None

		if ddata != None:
			data = simplejson.loads(ddata)
			return data
		else:
			return None
	else:
		return ret.status_code