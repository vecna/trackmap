#!/bin/bash

ARCH=$(uname -m)
# i686 or x86_64 supported only

PHANTOMJS_VER=1.9.8
PHANTOMJS=phantomjs-$PHANTOMJS_VER-linux-$ARCH
PHANTOMJS_BIN=phantom-$PHANTOMJS_VER
PHANTOMJS_DIST=$PHANTOMJS.tar.bz2
PHANTOMJS_URL=https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOMJS_DIST


# phantomjs-1.9.8-linux-x86_64.tar.bz2


wget -c $PHANTOMJS_URL
if [ ! -d $PHANTOMJS ] ; then
    tar xf $PHANTOMJS.tar.bz2
    ln -s $PHANTOMJS/bin/phantomjs $PHANTOMJS_BIN
fi
