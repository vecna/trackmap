#!/bin/sh -x
# I'm puttint the "-x" because there are some 'sudo'...

sudo aptitude update
sudo aptitude install phantomjs traceroute python-pip gcc python-pip python-dev libgeoip-dev
sudo pip install GeoIP tldextract

# remind: handle 
# phantomjs -h 
# 2014-05-31T10:35:30 [WARNING] phantomjs: cannot connect to X server 
# In this case, your distribution has phantom 1.5 and this is bad
# you've to download
# http://phantomjs.googlecode.com/files/phantomjs-1.8.1-linux-x86_64.tar.bz2
# and put the binary in the execution path (simply replace the origianl phantomjs)

