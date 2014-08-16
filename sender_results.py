#!/usr/bin/python
# This script send the results to the TrackMap hidden service
# This script is called at the end of perform_analysis.py and is used via 'torify'

import socket, sys

connect_tuple = ( 'mzvbyzovjazwzch6.onion', 80 )

if len(sys.argv) == 1:
    print "This script sent the result file to us, via hidden service"
    print "Do not run by hand, is called directly by perform_analysis"
    print ""
    print "usage: python %s output-$country.tar.gz" % sys.argv[0]
    quit(-1)

print "I'm going to send the results to the hidden service...please wait a bit"
print "If something goes wrong, please type again the command:"
print "  torify python %s %s" % (sys.argv[0], sys.argv[1])

filename = sys.argv[1]

if len(sys.argv) == 3:
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

with open(filename, 'rb') as fp:
    c = socket.socket()
    c.connect( connect_tuple )

    datacounter = 0
    while True:

        data = fp.read(1024)
        if not data:
            break

        datacounter += len(data)
        check = c.send(data)

        # assert datacounter == check, "your OS is making fun of you, or, Tor is different than expected"
        if len(data) != check:
            print "XXX: have read", len(data), "but sent", check, "?"

    c.close()

print "Done."
