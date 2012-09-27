#!/usr/bin/python

#python gitbugpush.py 6626e004a53072894a4952f8029c98cf9e2c7a1b HEAD refs/master

import zmq
import argparse
import ConfigParser

serverport = ''

def read_config():
    global serverport
    config = ConfigParser.ConfigParser()
    config.read('defaults.cfg')
    serverport = str(config.getint('zmq', 'port'))

parser=argparse.ArgumentParser(description='Gitbugz push to Gitbugz server.')

#parser.add_argument('serverport', type=int, help='the server socket port')
parser.add_argument('startrev', help='the first git commit (exclusive)')
parser.add_argument('endrev', help='the last git commit (inclusive)')
parser.add_argument('refname', help='the ref-name in git')

args=parser.parse_args()

oldrev = args.startrev
newrev = args.endrev
refname = args.refname

read_config()

context = zmq.Context()

print "Connecting to Gitbugz processing server..."
socket = context.socket(zmq.PUSH) #REQ)
connectaddress = "tcp://localhost:" + serverport
socket.connect (connectaddress)

# Wait up to one second. If the server does not pick up our message (or is offline) this update will not be applied to fogbugz
socket.LINGER = 1000

print "Sending request..."

send_message = oldrev + "," + newrev + "," + refname

try:
    socket.send(send_message, zmq.NOBLOCK)
    print "Changes queued for fogbugz updates"
except zmq.ZMQError:
    print "Gitbugz process not running"

socket.close()
