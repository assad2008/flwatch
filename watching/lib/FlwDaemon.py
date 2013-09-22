#!/usr/bin/env python
# encoding=utf-8

import sys,os,time,atexit
reload(sys)
sys.setdefaultencoding("utf-8")
from signal import SIGTERM
from FlwUtil import loadconfig

class FlwDaemon:
	
	def __init__(self, pidfile, stdin = '/dev/null', stdout = '/dev/null', stderr = '/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
		
	def _daemonize(self):
		try: 
			pid = os.fork() 
			if pid > 0:
				sys.exit(0) 
		except OSError, e:
			write_log('ERROR',"fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
		os.setsid()
		os.chdir(loadconfig('DIRS','ROOT')) 
		flwpath = loadconfig('DIRS','ROOT')
		sys.path.append(flwpath)
		os.umask(0)
		
		try: 
			pid = os.fork() 
			if pid > 0:
				sys.exit(0) 
		except OSError, e:
			write_log('ERROR',"fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)

		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)

		#重定向标准输入/输出/错误
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		#注册程序退出时的函数，即删掉pid文件
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)			
		
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			message = "Start error,pidfile %s already exist. Fl Watching Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)

		self._daemonize()
		self._run()
		
	def stop(self):
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Fl Watching Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				write_log('ERROR','Stop error,'+str(err))
				sys.exit(1)
				
	def restart(self):
		self.stop()
		self.start()
		
	def _run(self):
		pass