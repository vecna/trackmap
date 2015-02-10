#!/bin/bash

# THIS SCRIPT IS FOR SETTING UP A NEW HOST
# It install requirements and then checks out the tool
# from github into a subdirectory of the current directory

REQUIREMENTS=(wget unzip traceroute python-pip libfontconfig1 python-termcolor python-requests phantomjs)
sudo apt-get update
sudo apt-get install -y ${REQUIREMENTS[*]}
sudo pip install tldextract PySocks


traceroute --version
if [ $? != "0"  ]; then echo "Missing traceroute" && exit; fi

UNZIPDIR="trackmap-master"

if [ -d $UNZIPDIR ] ; then
    mv $UNZIPDIR $UNZIPDIR.old
fi
wget https://github.com/vecna/trackmap/archive/master.zip
unzip master.zip
cd $UNZIPDIR

./perform_analysis.py --version
if [ $? != "0"  ]; then echo "\n\nSomething goes wrong in the install, please report the issue to trackmap<at>tacticaltech.org\n" && exit; fi

echo "TrackMap collection system: installed correctly"
