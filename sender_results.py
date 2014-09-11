#!/usr/bin/python
# This script send the results to the TrackMap hidden service
# This script is called at the end of perform_analysis.py and is used via 'torify'

import socket
import sys
import os
import time
import random


connect_tuple = ( 'mzvbyzovjazwzch6.onion', 80 )

def get_help():
    return "  torify %s %s" % (sys.argv[0], sys.argv[1])

if len(sys.argv) == 1:
    print "This script sent the result file to us, via hidden service"
    print "Do not run by hand, is called directly by perform_analysis"
    print ""
    print "usage: python %s results-$country.tar.gz" % sys.argv[0]
    quit(-1)


print "I'm going to send the results to the hidden service...please wait a bit\n"

filename = sys.argv[1]

if len(sys.argv) == 3:
    # this is intended if I'm debugging, putting some extra useless argument
    connect_tuple = ( '127.0.0.1', 32001 )

try:
    if not filename.endswith('.tar.gz'):
        raise Exception("Not .tar.gz suffix found")
    if len(filename) > 28:
        raise Exception("Expected not more than 28 byte here")
    if filename.find('/') != -1:
        raise Exception("put a shah not a slash")
    if filename.find('%') != -1:
        raise Exception("Encoding is the root of evil")
    if filename.find('\\') != -1:
        raise Exception("Other kind of encoding")
except Exception as info:
    print info
    quit(-1)

total_sent = 0

statinfo = os.stat(filename)

with open(filename, 'rb') as fp:
    c = socket.socket()
    c.connect( connect_tuple )

    anxiety_handler = 0
    # anxiety is the counter to show a progress percentage, in order to do not make
    # the user press ^C

    datacounter = 0
    while True:

        data = fp.read(1024)
        if not data:
            break

        total_sent += c.send(data)

        if random.randint(1, 20) == 13:
            print "%f%%\t%s\t%d\tof %d bytes sent" % (
                ( 100 * (float(total_sent) / statinfo.st_size)), time.ctime(),
                total_sent, statinfo.st_size
            )

    c.close()


print "\n\tData collected has been sent, Thank You! :)\n"


