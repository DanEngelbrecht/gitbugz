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
    global serverport
    global output

    config = ConfigParser.ConfigParser()
    config.read(configpath)#'defaults.cfg')
    site = config.get('fogbugz', 'site')
    username = config.get('fogbugz', 'username')
    password = config.get('fogbugz', 'password')
    repopath = config.get('git', 'repopath')
    serverport = str(config.getint('zmq', 'port'))
    output = config.get('log', 'standard')
    logging.basicConfig(filename=output, level=logging.DEBUG)

class WorkUnit:
    site = ''
    username = ''
    password = ''
    oldrev = ''
    newrev = ''
    repopath = ''
    refname = ''
    def __init__(self, site, username, password, oldrev, newrev, repopath, refname):
        self.site = site
        self.username = username
        self.password = password
        self.oldrev = oldrev
        self.newrev = newrev
        self.repopath = repopath
        self.refname = refname

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
            item = q.get()
#            os.system(item)
            editCases(item.site, item.username, item.password, item.oldrev, item.newrev, item.repopath, item.refname)
            q.task_done()

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
            launch = site + " \"" + username + "\" \"" + password + "\" " + oldrev + " " + newrev + " " + repopath + " " + refname
#            launch = "/opt/fogbugzgit/fogbugz-case-edit.py " + site + " \"" + username + "\" \"" + password + "\" " + oldrev + " " + newrev + " " + repopath + " " + refname
#            logging.info('Dispatching: ' + launch + '\n')
            logging.info('Spawning: ' + launch)
            wu = WorkUnit(site, username, password, oldrev, newrev, repopath, refname)
            q.put(wu , False)

initial_program_setup()
do_main_program()
program_cleanup()
