#!/usr/bin/env python
#encoding=utf-8

import re,DNS,simplejson,chardet
import urllib2,socket,httplib
import time,sys
from datetime import datetime
from FlwLogLib import *
from FlwPingLib import Ping

def website_get_domain(host,itemconfig):
	try:
		if itemconfig['ip'] != '':
			domain = itemconfig['ip']
		else:			
			domain = host		
	except Exception as e:
		log_error("website_get_domain():" + str(e))
	return domain
	

def website_get_newUrl(url):
	try:
		if url.find("http://") != -1:
			newUrl = url.replace("http://","")
		elif url.find("https://") != -1:
			newUrl = url.replace("https://","")
		else:
			newUrl = url
		return newUrl
	except Exception as e:
		log_error("website_get_newUrl():" + str(e))
		
def website_url_analyze(url,itemconfig):
	try:
		newUrl = website_get_newUrl(url)
		index = newUrl.find("/")
		if index != -1:
			host = newUrl[0:index]
			
			urlsuffix = newUrl.replace(host,"")
		else:
			host = newUrl
			urlsuffix = "/"
			
		port = 80
		spix = host.find(':')		
		if spix != -1:
			port = host[spix:]
			host = host[0:spix]
			port = port.replace(':','')
		domain = website_get_domain(host,itemconfig)
		return domain,host,urlsuffix,port
	except Exception as e:
		log_error("website_url_analyze():" + str(e))
		
def dns_test(domain):
	try:
		domain = website_get_newUrl(domain)
		index = domain.find("/")
		if index != -1:
			domain = domain[0:index]		
		domain = domain.replace('/','')
		spix = domain.find(':')
		if spix != -1:
			domain = domain[0:spix]
		DNS.DiscoverNameServers()
		req = DNS.Request()
		ans = req.req(name = domain , qtype = DNS.Type.ANY)
		return ans.answers
	except Exception as e:
		log_error("dns_test():" + str(e) + str(domain))		
		dnsresult = []
		return dnsresult
		
def get_domain_ip(domain):
	domain = website_get_newUrl(domain)
	index = domain.find("/")
	if index != -1:
		domain = domain[0:index]
	domain = domain.replace('/','')
	
	spix = domain.find(':')
	if spix != -1:
		domain = domain[0:spix]	
	result=[]
	try:
		result=socket.getaddrinfo(domain,None)
	except Exception as e:
		log_error("get_domain_ip:" + str(e) + str(domain))	
	return result
	
def dns_test_three(domain):
	'''
	域名解析IP ,重试3次
	'''
	try:
		isip = re.findall(r'\d+.\d+.\d+.\d+', domain)
		if len(isip) > 0:
			return ['ip']
	except Exception as e:
		log_error("dns_test_three() isip:" + str(e))
	ipresult = []
	try:
		i = 0
		max = 3		
		ipresult = get_domain_ip(domain)		
		while(i < max):
			if len(ipresult) > 0:
				return ipresult			
			time.sleep(0.5)			
			ipresult = get_domain_ip(domain)
			i += 1					
		return ipresult			
	except Exception as e:
		log_error("dns_test_three():" + str(e))		
		return ipresult
		
def website_urlopen_reuslt(url,itemconfig):
	try:
		domain,host,urlsuffix,port = website_url_analyze(url,itemconfig)
		dnsresult = []
		dnsresult = dns_test_three(url)
		if len(dnsresult) <= 0:		
			log_error("dns_test(url):" + str(url))
			result = {"responsetime":0,"status":url + " DNS解析失败!"}
			return str(0),simplejson.dumps(result),str(1),url + " DNS解析失败!"
		
		if Ping(host) == False:
			log_error("dns_test(url):" + str(url))
			result = {"responsetime":0,"status":"网站服务器(" + host + ")不可达!"}
			return str(0),simplejson.dumps(result),str(1),"网站服务器(" + host + ")不可达!"

		header = {"Host":host}
		try:
			if url.find("https://") != -1:#https访问
				conn = httplib.HTTPSConnection(domain,port = int(port),timeout = 30)
			else:#http访问
				conn = httplib.HTTPConnection(domain,port = int(port), timeout = 30)
		except httplib.HTTPException as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.NotConnected as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.InvalidURL as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.UnknownProtocol as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.UnknownTransferEncoding as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.UnimplementedFileMode as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.IncompleteRead as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.CannotSendRequest as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.CannotSendHeader as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.ResponseNotReady as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except httplib.BadStatusLine as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		except Exception as e:
			conn.close()
			result = {"responsetime":0,"status":str(e)}
			return str(0),simplejson.dumps(result),str(1),str(e)
		finally:
			conn.close()

		start = datetime.now()
		conn.request("GET",urlsuffix,headers = header)
		res = conn.getresponse()
		content = res.read()
		status = res.status
		reason = res.reason
		conn.close()
		end = datetime.now()
	except Exception as e:
		log_error("website_urlopen_result():" + str(e))
		result = {"responsetime":0,"status":str(e)}
		return str(0),simplejson.dumps(result),str(1),str(e)
		
	responsetime = (end - start) . microseconds / 1000
	result = {"responsetime":responsetime,"status":str(status)}
	return str(1),simplejson.dumps(result),content,status
	
def website_alive_check(url,itemconfig):
	try:
		isTrue,result,content,status = website_urlopen_reuslt(url,itemconfig)
		if isTrue == '0':
			reason = "Web access fails, the return status:" + status
			return str(1),result,reason,str(1)
		else:
			return str(0),result,status
	except Exception as e:
		log_error("website_alive_check():" + str(e))
		return str(1),result,str(e),str(1)