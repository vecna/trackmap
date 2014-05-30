#!/bin/sh -x
# I'm puttint the "-x" because there are some 'sudo'...

sudo aptitude update
sudo aptitude install phantomjs traceroute python-pip gcc python-pip python-dev libgeoip-dev
sudo pip install GeoIP tldextract
