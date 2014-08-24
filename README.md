# TrackMap project

The TrackMap project is research by [Claudio ࿓  vecna](https://twitter.com/sniffjoke), develped with [Tactical Tech](http://www.tacticaltech.org), as part of the [MyShadow](http://myshadow.org) project.

*When you access the national media from your country, your internet connection is being tracked by multiple third parties. And this happens constantly*. That's what we aim to illustrate.

Our aim is to show where our data travels when we visit our favorite news websites through a visualization. We are currently looking for people to collaborate with in various countries in the world which would make this project possible. 


## This code 

This repository contains the script and the data source needed to generate our needed data.

The collection of data needs to happen in a distributed way, _which means that the script needs to run from each of the selected countries_. This is important because the network and the trackers behave differently based on the provenience country of the user. 

### For every country we need two kinds of supporters:

If you're a **Media expert/Aware citizen**:

  * we need a reliable media list for every country, take a look at the directory [unverified media list](https://github.com/vecna/helpagainsttrack/tree/master/unverified_media_list) if your country is present: we need someone with local experience to review the media list (add the missing media, check if the current sites are still active and separate the national from the local media).

If you're a **Linux user**:

  * you can run the script *perform\_analysis.py* on your own (it will automatically send the results to our hidden service). 

If you're a **Linux user** with a constantly running box and few times:

  * You can run the **Vagrant script** explained  below to create a virtual machine _under our control_, where we can perform the tests (less effort for you, and we will eventually send you an email asking you to start your box when the tests get updated).

## Install the test script

The test script can only be run under debian/ubuntu, and **RUN THIS TESTS VIA Tor IS POINTLESS**: because the important data are obtained via traceroute, and works in a lower level than Tor (also works in UDP, that cannot be anonymized).

### Automated installation

Before you run this, ensure that you are running as a user that can `sudo` to root. 

Create a directory to store the project files and change directory there:

    mkdir trackmap
    cd trackmap
    
fetch the setup script:

    wget -c https://raw.githubusercontent.com/vecna/helpagainsttrack/master/setup.sh
    
and run this script with bash:

    bash setup.sh
    
This script uses `sudo` to execute some commands, so it will ask for your password when it executes. The project
scripts are installed in a subdirectory called *helpagainsttrack*.

### Manual installation

Install some base requirements (run with sudo):

    sudo apt-get update
    sudo apt-get install tor git wget torsocks -y
    sudo apt-get install traceroute python-pip gcc python-dev libgeoip-dev -y
    sudo apt-get install geoip-database libfontconfig1 -y
    sudo pip install GeoIP tldextract termcolor 

Create one directory for store the project files:

    mkdir trackmap
    cd trackmap

    wget https://github.com/vecna/helpagainsttrack/archive/master.zip
    unzip master.zip
    cd helpagainsttrack-master

**PhantomJS** has to be downloaded because distribution repositories had old versions. We need >= 1.9.0 (*sha244 checksum at the end the file*). You can skip this step if you are in Debian Sid (is a 1.9.0 version), but in other distribution older versions are given.

If you have a 32 bit system:

    wget https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-i686.tar.bz2 
    tar jxf phantomjs-1.9.2-linux-i686.tar.bz2 
    ln -s phantomjs-1.9.2-linux-i686/bin/phantomjs phantom-1.9.2
    
if you have a 64 bit system:

    wget https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-x86_64.tar.bz2
    tar jxf phantomjs-1.9.2-linux-x86_64.tar.bz2
    ln -s phantomjs-1.9.2-linux-x86_64/bin/phantomjs phantom-1.9.2

## Run the test script

Change directory to the directory where you installed the test script and run:

    ./perform_analysis.py NAME_OF_YOUR_COUNTRY

If you have not installed phantom 1.9.2 on the path specified above, but are using your distribution's phantomjs, add 
the option **lp** (local phantom):

    ./perform_analysis.py NAME_OF_YOUR_COUNTRY lp

To see a list of countries, look in the *verified_media* folder.

If your country is not on the list, it means that nobody has reviewed the media list (a boring but necessary step) for you
country. You can take a look at the unclean lists in the *unverified_media_list* folder and if your country is listed 
there you can review the provided list before using it with the test tool.

## Long term project support 

Please read [Vagrant usage description](https://github.com/vecna/helpagainsttrack/tree/master/Vagrant)

## Docker image (do not use yet - experimental)

A [Docker](https://www.docker.com/) image has been created for this tool, using the Dockerfile provided in the test 
tool directory. If you wish to use this, you can run the test tool using:

    docker run -t -i pvanheus/helpagainsttrack NAME_OF_YOUR_COUNTRY
    
## The operation performed by the script (perform\_analysis.py)

  * an HTTP connection (using phantomjs) to every news media under analysis
  * Collect all the URL included as third party (trackers, ADS, social)
  * Collect &lt;object&gt; elements to compare flash injections
  * Perform traceroute for every included URL 
  * GeoIP conversion from every IP included.
  * send the results to our hidden service (**mzvbyzovjazwzch6.onion**)

This shows all the nations capable of knowing which users are visiting the (selected) news media.

## Why care about these results ?

This has been done by the NSA, which intercepts the advertising network of the Angry Birds
game. Angry Birds was the most deployed game, but was still an option for citizens. News media, however, are accessed by the majority of populations around the world and by tracking which websites users access, third parties can gain a unique insight into the types of interests people have, their ideas, beliefs and concerns. In other words, by tracking news media, third parties can map out the interests of individuals and groups and potentially target them. The aim of this project is to expose how the ADS and tracking business works based on third party injections.


### Theoretical elements

In this (very first version) of the TrackMap project we want answer to the following questions:

  * "Is the online advertising business a potential asset to intelligence agencies ?"
  * "Are users aware of the extent to which their data and browsing habits are exposed on a daily basis?"
  * "Are privacy activists aware of their network path and of its implications ?"
  * "Is online advertising and tracking a good business model for online media ?" (In this case, media is a website which constantly publishes updates on relevant events and their consultancy is therefore not just an option for users, but also a **need** for users).

Due to limited resources from our side, our research might face the following limitations:

  * The GeoIP is only partially reliable, because IP classes can change organizations and therefore nations.
  * The GeoIP resolution, from an IP address to a Country, might return a continent (for example, some classes are assigned to Europe, without more precision about the physical location).
  * We're performing traceroute without checking if the resource included is in https (this happens very seldomly, and in these cases we consider the data stored in the recipient country but not exposed in-transit interception and manipulation)
  * Some service providers use CDN and this means that in order to interact with them, this might be resolved as part o
f the same country of the user, also if the content is obviously stored by a foreign country. (very rare, anyway)
  * We cannot know if a service has some Cloud Provider as a backend
  * We cannot automatize the seeking of company information over every tracking agent

Further improvements are in progress.


## Countermeasure

**As far as I know, those technologies lack on security/privacy audit**, but ideally they are a good start:

  * NoScript (FireFox)
  * SafeScript (Chrome)
  * Disconnect
  * Ghostery 
  * AdBlock+

### A little dream

The tracking elements are well documented in the websites. 
If you read site A, B, C and D, the tracking agent present in A, B and D know almost 75% of information about you.

The distributed nature of the Internet will always make the development of sites like "C" possible: a site without a tracking agent. 
Sadly, due to the online adverising business, mixing between social and ADV, SEO and infrastructural needs, the creation of independent and trackless sites is extremely rare.

When someone shares a link, this link often contains some identifier used to recognize users connected by other means (eg: sharing a link via chat or via mail: the tracker does not know how you got that link, but can now link you and the users who have shared the link).

This is one of the scary aspects of tracking: this business model does not just track you, but your entire network, and escaping it is quite difficult.

**A dream about it: do not bring anymore users on websites. When you see information that deserves to be shared, create a partial, temporary and static copy of the information and only share that copy.**

**There is no need to trigger your recipients devices with some network activity that leads to tracks and exposure.**

**Such activity is used against you and your network of friends, and to develop a technical solution is quite easy**


## Various notes

a brief presentation related on Italian media is here: [Online users tracking: effect, responsibility and countermeasures](http://vecna.github.io)

### SHA checksums

sha224 cksum of phantomjs-1.9.2 i686

    4b6156fcc49dddbe375ffb8895a0003a4930aa7772f9a41908ac611d

sha224 cksum of phantomjs-1.9.2 x86\_64

    2937cea726e7fe4dd600f36e7c5f0cca358593e96808dc71b6feb166 

