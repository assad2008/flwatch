#!/usr/bin/env python
#encoding=utf-8

import os,sys,time
from FlwUtil import loadconfig
reload(sys)
sys.setdefaultencoding("utf-8")

def website_alarm_content(itemname,itemobject,reason = '请求异常',level = 1):
	itemname = itemname.encode('utf8')
	monitorTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	if int(level) == 1:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 页面访问失败"
		bottomTemp = "故障原因:" +  str(reason)
		subject = "[故障信息]" + str(topTemp)
	elif int(level) == 3:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname)+" 指标异常 "
		bottomTemp = "故障原因:" + str(reason)
		subject = "[提醒信息]" + str(topTemp)
	elif int(level) == 4:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 恢复正常 "
		bottomTemp = ""
		subject = "[恢复信息]" + str(topTemp)
	elif reason == '' or reason == '项目恢复正常':
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 不稳定"
		bottomTemp = "上一次故障原因:不稳定。"
		subject = "[恢复信息]" + str(topTemp)

	middleTemp = "<br />监控类型:网页存活(http/https) <br />\
			所在域/服务器:" + str(itemobject) + " <br />\
			检查时间:" + str(monitorTime) + " <br /> "
	template = topTemp + middleTemp + bottomTemp
	return template,subject
	
def ping_alarm_content(itemname,itemobject,level):
	itemname = itemname.encode('utf8')
	monitorTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	if int(level) == 1:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 连接失败 "
		bottomTemp = "故障原因:数据包全部丢弃 "
		subject = "[故障信息]" + str(topTemp)
	elif int(level) == 4:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 恢复正常"
		bottomTemp = "上一次故障原因:数据包全部丢弃  "
		subject = "[恢复信息]" + str(topTemp)
		
	middleTemp = "<br />监控类型:ping <br />\
			所在域/服务器:" + str(itemobject) + " <br />\
			检查时间:" + str(monitorTime) + " <br /> "
	template = topTemp + middleTemp + bottomTemp
	return template,subject
	
def custom_alarm_content(itemname, itemobject, reason = '请求异常',level = 1):
	itemname = itemname.encode('utf8')
	monitorTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	if int(level) == 1:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 连接失败"
		bottomTemp = "故障原因:" + str(reason) + " "
		subject = "[故障信息]" + str(topTemp)
	elif int(level) == 2:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 指标异常 "
		bottomTemp = "故障原因:" + str(reason) + " "
		subject = "[提醒信息]" + str(topTemp)
	elif int(level) == 3:
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 恢复正常"
		bottomTemp = " "
		subject = "[恢复信息]" + str(topTemp)
	elif reason == '' or reason == '项目恢复正常' :
		topTemp = "监控系统监控到您的监控项目:" + str(itemname) + " 不稳定"
		bottomTemp = "上一次故障原因:不稳定。"
		subject = "[恢复信息]" + str(topTemp)
	middleTemp = "<br />监控类型:服务器指标 <br />\
			所在域/服务器:" + str(itemobject) + " <br />\
			检查时间:" + str(monitorTime) + " <br /> "
	template = topTemp + middleTemp + bottomTemp
	return template,subject
