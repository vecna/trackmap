#!/usr/bin/python
# This script send the results to the TrackMap hidden service
# This script is called at the end of perform_analysis.py and is used via 'torify'

import requests, sys

# test HS - need to be put our official one
# url = 'http://xdwjkgpdku6gvh5e.onion:12345/'
url = 'http://lo:3232/upload'

if len(sys.argv) == 1:
    print "This script sent the result file to us, via hidden service"
    print "Do not run by hand, is called directly by perform_analysis"
    print ""
    print "usage: %s output-$country.tar.gz" % sys.argv[0]
    quit(-1)

print "I'm going to send the results to the hidden service...please wait a bit"
print "If something goes wrong, please type again the command:"
print "  %s %s" % (sys.argv[0], sys.argv[1])

filename = sys.argv[1]

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

files = { 'myfile' : open(filename, 'rb') }
# proxy = { 'http':'http://127.0.0.1:9050' }
# r = requests.post(url, files=files, proxies=proxy)
# is used via torify because this proxy approach is not working :(
r = requests.post(url, files=files)
print "Done."
