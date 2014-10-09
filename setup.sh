#!/bin/bash

# THIS SCRIPT IS FOR SETTING UP A NEW HOST
# It install requirements and then checks out the tool
# from github into a subdirectory of the current directory

REQUIREMENTS=(tor wget traceroute python-pip gcc python-dev libgeoip-dev geoip-database libfontconfig1)
sudo apt-get update
sudo apt-get install -y ${REQUIREMENTS[*]}
sudo pip install GeoIP tldextract termcolor PySocks


traceroute --version
if [ $? != "0"  ]; then echo "Missing traceroute" && exit; fi

UNZIPDIR="helpagainsttrack-master"

if [ -d $UNZIPDIR ] ; then
    mv $UNZIPDIR $UNZIPDIR.old
fi
wget https://github.com/vecna/helpagainsttrack/archive/master.zip
unzip master.zip
cd $UNZIPDIR

if [ -x ./fetch_phantomjs.sh ] ; then
    ./fetch_phantomjs.sh
fi

./perform_analysis.py --version
if [ $? != "0"  ]; then echo "Something goes wrong in the install, please follow the README" && exit; fi

echo "TrackMap collection system: installed correctly"
