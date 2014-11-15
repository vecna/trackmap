#!/bin/bash

ARCH=$(uname -m)
# i686 or x86_64 supported only

PHANTOMJS_VER=1.9.2
PHANTOMJS=phantomjs-$PHANTOMJS_VER-linux-$ARCH
PHANTOMJS_BIN=phantom-$PHANTOMJS_VER
PHANTOMJS_DIST=$PHANTOMJS.tar.bz2
PHANTOMJS_URL=https://github.com/vecna/phantomjs-mirror/raw/master/$PHANTOMJS_DIST

wget -c $PHANTOMJS_URL
if [ ! -d $PHANTOMJS ] ; then
    mv $PHANTOMJS_DIST $PHANTOMJS.tar.bz2
    tar xf $PHANTOMJS.tar.bz2
    ln -s $PHANTOMJS/bin/phantomjs $PHANTOMJS_BIN
fi
