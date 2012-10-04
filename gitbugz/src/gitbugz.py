#!/usr/bin/python

import zmq
import thread
import Queue
import sys
import ConfigParser
import logging
from gitbugzutils import editCases

#import argparse

configpath = sys.argv[1]

site = ''
username = ''
password = ''
repopath = ''
reponame = ''
gitweburl = ''
serverport = ''
output = ''

q = Queue.Queue(10)

socket = ''

def read_config():

    global configpath
    global site
    global username
    global password
    global repopath
    global reponame
    global serverport
    global gitweburl
    global output

    config = ConfigParser.ConfigParser()
    config.read(configpath)#'defaults.cfg')
    site = config.get('fogbugz', 'site')
    username = config.get('fogbugz', 'username')
    password = config.get('fogbugz', 'password')
    repopath = config.get('git', 'repopath')
    reponame = config.get('git', 'reponame')
    serverport = str(config.getint('zmq', 'port'))
    gitweburl = config.get('gitweb', 'url')
    output = config.get('log', 'standard')
    logging.basicConfig(filename=output, level=logging.DEBUG)

class WorkUnit:
    site = ''
    username = ''
    password = ''
    oldrev = ''
    newrev = ''
    repopath = ''
    reponame = ''
    refname = ''
    gitweburl = ''
    def __init__(self, site, username, password, oldrev, newrev, repopath, reponame, refname, gitweburl):
        self.site = site
        self.username = username
        self.password = password
        self.oldrev = oldrev
        self.newrev = newrev
        self.repopath = repopath
        self.reponame = reponame
        self.refname = refname
        self.gitweburl = gitweburl

def initial_program_setup():
    global socket
    global serverport
    global q

    read_config()

    context = zmq.Context()

    logging.info('Starting Gitbugz processing server, opening socket')
    socket = context.socket(zmq.PULL) #REP)
    bindaddress = "tcp://*:" + serverport
    logging.info('Listen address: ' + bindaddress)
    socket.bind(bindaddress)

    def worker():
        while True:
            try:
                logging.info('Worker thread waiting for queue item')
                item = q.get()
                if item is not None:
                    try:
#                       os.system(item)
                        editCases(item.site, item.username, item.password, item.oldrev, item.newrev, item.repopath, item.reponame, item.refname, gitweburl)
                    except: # catch *all* exceptions
                        logging.exception('An error occured when processing editCases')
                q.task_done()
                logging.info('Worker thread completed queue item')
            except:
                logging.exception('An error occured when fetching queue item')

    thread.start_new_thread( worker, () )

def program_cleanup():
    global socket
    socket.close(1000)

def reload_program_config():
    read_config()

def do_main_program():
    global socket
    global site
    global username
    global password
    global repopath
    global reponame
    global gitweburl
    global q
    while True:
        logging.info('Gitbugz processing server, waiting for updates...')
        message = socket.recv()
        if message:
            logging.info('Received work: ' + message)
            s = message.split(",")
            oldrev = s[0]
            newrev = s[1]
            refname = s[2]
            launch = site + " \"" + username + "\" \"" + password + "\" " + oldrev + " " + newrev + " " + repopath + reponame + " " + refname + " " + gitweburl
#            launch = "/opt/fogbugzgit/fogbugz-case-edit.py " + site + " \"" + username + "\" \"" + password + "\" " + oldrev + " " + newrev + " " + repopath + " " + refname
#            logging.info('Dispatching: ' + launch + '\n')
            logging.info('Spawning: ' + launch)
            wu = WorkUnit(site, username, password, oldrev, newrev, repopath, reponame, refname, gitweburl)
            q.put(wu , False)

initial_program_setup()
do_main_program()
program_cleanup()

#doProcess()

"""
class MyDaemon(Daemon):
	def run(self):
		while True:
			doProcess()

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/daemon-example.pid', '/dev/null', stdout='/var/log/MyDaemon.log', stderr='/var/log/MyDaemonErr.log')
	if len(sys.argv) >= 2:
		if 'start' == sys.argv[1]:
                        print "Starting daemon"

                        parser=argparse.ArgumentParser(description='Fogbugz receivefor server.')

                        parser.add_argument('command', help='the daemon command')
                        parser.add_argument('site', help='the site name on fogbugz example for example.fogbugz.com')
                        parser.add_argument('username', help='the username to use when logging in to fogbugz')
                        parser.add_argument('password', help='the password to use when logging in to fogbugz')
                        parser.add_argument('serverport', type=int, help='the server socket port')
                        parser.add_argument('repopath', help='the path to the git repo')
                        parser.add_argument('reponame', help='the name of the git repo')
                        parser.add_argument('gitweburl', help='the url to  gitweb site')

                        args=parser.parse_args()

                        command = args.command
                        site = args.site
                        username = args.username
                        password = args.password
                        repopath = args.repopath
                        reponame = args.reponame
                        gitweburl = args.gitweburl
                        serverport = args.serverport

			daemon.start()
		elif 'stop' == sys.argv[1]:
                        print "Stopping daemon"
			daemon.stop()
		elif 'restart' == sys.argv[1]:
                        print "Restarting daemon"
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)

"""

