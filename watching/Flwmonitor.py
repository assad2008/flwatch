#!/usr/bin/python
#encoding=utf-8

import os,sys
import time
import multiprocessing
sys.path.append('./lib')
from FlwUtil import loadconfig
from FlwLogLib import *
from FlwDaemon import FlwDaemon
from FlwWatchingLib import *


def watch_select(item_type):
	if item_type == 'app':
		return do_watching_app
	elif item_type == 'http':
		return do_watching_http
	elif item_type == 'ping':
		return do_watching_ping
		

def watching_main():
	while True:
		itemlists = get_watch_lists()
		itemqueue = watching_item_inQueue(itemlists)
		del itemlists
		maxprocess = int(loadconfig('MONITOR','maxprocess'))
		if multiprocessing.cpu_count() < maxprocess:
			maxprocess = multiprocessing.cpu_count()
		flwprocesspool = multiprocessing.Pool(processes = maxprocess)
		while True:
			if itemqueue.qsize() == 0:
				break
			itemlist = watching_item_outQueue(itemqueue)
			if itemlist == None:
				break
			funcname = watch_select(itemlist[3])
			try:
				flwprocesspool.apply_async(funcname,(itemlist, ))
			except Exception as e:
				log_error('watching_main() process failed:'+str(e))	
		flwprocesspool.close()
		flwprocesspool.join()
		time.sleep(1)

class FlwMonitor(FlwDaemon):
	def _run(self):
		watching_main()
		
if __name__ == '__main__':
	daemon = FlwMonitor(loadconfig('DIRS','ROOT') + 'FlwMonitor.pid')
	if len(sys.argv) == 2:
		if sys.argv[1].upper() == 'START':
			daemon.start()
		elif sys.argv[1].upper() == 'STOP':
			daemon.stop()
		elif sys.argv[1].upper() == 'RESTART':
			daemon.stop()
			daemon.start()
		else:
			print "Unknow Command!"
			print "Usage: %s start|stop|restart" % sys.argv[0]
			sys.exit(2)
		sys.exit(0)
	else:
		print "Usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(0)