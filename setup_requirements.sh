#!/bin/sh

echo "executing 'aptitude update'"
sudo aptitude update
echo "installing: phantomjs traceroute and python+GeoIP (requires gcc and pip)"
sudo aptitude install phantomjs traceroute python-pip gcc python-pip python-dev libgeoip-dev geoip-database
echo "installing python module GeoIP and tldextract"
sudo pip install GeoIP tldextract


echo "checking phantomjs installation..."

phantomjs -v
if [ "$?" -ne "0" ]; then
    echo "sadly phantomjs has not been installed or is not working correctly."
    echo "This can be solved easily, just download from these link:"
    echo "https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-i686.tar.bz2"
    echo "https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-x86_64.tar.bz2"
    echo "and put a symlink poiting to /usr/bin/phantomjs"
    echo "asks info to @sniffjoke if doubt arises"
fi
