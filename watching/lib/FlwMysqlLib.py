#!/usr/bin/env python
#encoding=utf-8

import os,sys,time
import MySQLdb
from FlwUtil import loadconfig
from DBUtils import PooledDB

def msyql_handler():
	host = loadconfig('MYSQL','HOST')
	user = loadconfig('MYSQL','USER')
	passwd = loadconfig('MYSQL','PASSWD') or ''
	db = loadconfig('MYSQL','DB')
	port = int(loadconfig('MYSQL','PORT'))
	size = int(loadconfig('MYSQL','SIZE'))
	pooldb = PooledDB.PooledDB(MySQLdb, maxusage = size, host = host, user = user, passwd = passwd, db = db ,port = port,charset = 'utf8')
	return pooldb.connection()
	
def mysql_phandler():
	MDB = MySQLdb.connect(host = loadconfig('MYSQL','HOST'),user = loadconfig('MYSQL','USER'),
			passwd = loadconfig('MYSQL','PASSWD'),db = loadconfig('MYSQL','DB'),port = int(loadconfig('MYSQL','PORT')),charset = 'utf8')
	return MDB
	
def close_mysql_handler(con, cur):
	cur.close()
	con.close()
	
def exce_select(tablename,condition = None,field = None):
	if tablename[0:6].upper() == 'SELECT':
		sql = tablename
	else:
		if field:
			sql = "SELECT "+field+ " FROM `"+tablename+"`"
		else:
			sql = "SELECT * FROM `"+tablename+"`"
		
		if condition:
			sql = sql + " WHERE " + condition
	try:
		con = msyql_handler()
		cur = con.cursor()
		cur.execute(sql)
		res = cur.fetchall()		
		close_mysql_handler(con, cur)
		return res
	except Exception as e:	
		close_mysql_handler(con, cur)
		con = msyql_handler()
		cur = con.cursor()	
		cur.execute(sql)
		res = cur.fetchall()		
		close_mysql_handler(con, cur)
		return res

def exec_sql(sql_string):
	try:
		con = msyql_handler()
		cur = con.cursor()
		cur.execute(sql_string)
	except Exception as e:
		close_mysql_handler(con, cur)
		con = msyql_handler()
		cur = con.cursor()	
		cur.execute(sql_string)
		close_mysql_handler(con,cur)
		