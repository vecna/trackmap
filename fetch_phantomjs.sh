#!/bin/bash

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
