#!/bin/bash

# THIS SCRIPT IS FOR SETTING UP A NEW HOST
# It install requirements and then checks out the tool
# from github into a subdirectory of the current directory

REQUIREMENTS=(tor git wget torsocks traceroute python-pip gcc python-dev libgeoip-dev geoip-database libfontconfig1)
sudo apt-get update
sudo apt-get install -y ${REQUIREMENTS[*]}
sudo pip install GeoIP tldextract termcolor


traceroute --version
if [ $? != "0"  ]; then echo "Missing traceroute" && exit; fi
git --version
if [ $? != "0"  ]; then echo "Missing git" && exit; fi


if [ ! -d helpagainsttrack ] ; then
    git clone https://github.com/vecna/helpagainsttrack.git
    if [ ! -d helpagainsttrack ] ; then
        echo "git failed! Quitting"
        exit
    fi
    cd helpagainsttrack
else
    ( cd helpagainsttrack ; git pull )
fi

(
    if [ -x ./fetch_phantomjs.sh ] ; then
        ./fetch_phantomjs.sh
    else
        # no fetch_phantomjs.sh in repo, insert its code here
        ARCH=$(uname -m)

        PHANTOMJS_VER=1.9.2
        PHANTOMJS=phantomjs-$PHANTOMJS_VER-linux-$ARCH
        PHANTOMJS_BIN=phantom-$PHANTOMJS_VER
        PHANTOMJS_DIST=$PHANTOMJS.tar.bz2
        PHANTOMJS_URL=https://phantomjs.googlecode.com/files/$PHANTOMJS_DIST

        wget -c $PHANTOMJS_URL
        if [ ! -d $PHANTOMJS ] ; then
            tar xf $PHANTOMJS_DIST
            ln -s $PHANTOMJS/bin/phantomjs $PHANTOMJS_BIN
        fi
     fi
)

./perform_analysis.py --version
if [ $? != "0"  ]; then echo "Something goes wrong in the install, please follow the README" && exit; fi
echo "TrackMap collection system: installed correctly"
echo "Now you can run ./perform_analysis.py $NAME_OF_YOUR_COUNTRY"
