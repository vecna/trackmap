# TrackMap project

TrackMap project is a research of [Tactical Tech](http://www.tacticaltech.org), part of [MyShadow](http://myshadow.org) project.

Our aim is to show where our data travels when we visit our favorite news websites through a visualization. We are currently looking for people to collaborate with in various countries in the world which would make this project possible.

## This repository

contains the script and the data source needed to collect the data. 
The collection has to happen in a distributed way, so from every country of the 
world the script need to be runned.

Is important this distributed effort, because the network and the trackers behave
differently based on the provenience country of the user. 

For every country we need two kind of supporters for this project:

If you're a **Media experts/Aware citizen**:

  * we need a reliable media list for every country, take a look the directory [unverified media list](https://github.com/vecna/helpagainsttrack/tree/master/unverified_media_list) if your country is present: we need someone with local experience reviews the media list. (put the missing media, checks if the current sites are still active
and separation between national and local)

If you're a **Linux users**:

  * you can run the script *perform\_analysis.py* by your own (it send to our hidden service the results automatically).

If you're a **Linux users** with a constantly running box and few times:

  * You can run the **Vagrant script** below explained to create a virtual machine _under our control_, where we can perform the tests (less effort for you, and we eventually will sent to you an email asking to start you box when the tests get updated).

## Run the test script

Is tested only under debian/ubuntu:

Some base requirements:

    sudo apt-get update
    sudo aptitude remove phantomjs -y
    sudo apt-get install tor git wget -y
    sudo apt-get install traceroute python-pip gcc python-dev libgeoip-dev -y
    sudo apt-get install geoip-database libfontconfig1 -y

Distributions phantomjs has commonly old versions. We need > 1.9.0
Download phantomjs in the most suitable location for you, I suggest in /usr/local/share

    wget https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-i686.tar.bz2 
    tar jxf phantomjs-1.9.2-linux-i686.tar.bz2 
    cd phantomjs-1.9.2-linux-i686/bin
    ln -s `pwd`/phantomjs /usr/bin/phantomjs
    cd ../..

*Note: sha224 cksum of phantomjs-1.9.2* 4b6156fcc49dddbe375ffb8895a0003a4930aa7772f9a41908ac611d

Come back in the directory of the tests, and:

    git clone https://github.com/vecna/helpagainsttrack.git
    sudo pip install GeoIP tldextract termcolor poster

And then finally run:

    cd helpagainsttrack
    ./perform_analysis.py verified_media/NAME_OF_YOUR_COUNTRY


## Vagrant option (a.k.a. less effort, more trust needed)

In this repository exist a **Vagrantfile**, it is configured to setup a virtual
box

    git clone https://github.com/vecna/helpagainsttrack.git
    sudo apt-get install vagrant
    cd helpagainsttrack
    vagrant up


When you type the command **vagrant up** will download the virtual machine image,
perform an upgrade, install the needed packages, copy an SSH public key, run Tor 
and give to you the address of the Tor hidden service pointing to the SSH port of 
the virtual machine.

We're gonna to run only the defined script, but almost in the case of new tests available,
we can just ask to you to type again **vagrant up**.


## The operation performed by the script (perform\_analisys.py)

  * an HTTP connection (using phantomjs) to every news media under analysis
  * Collect all the URL included as third party (trackers, ADS, social)
  * Collect <object> elements to compare flash injections
  * Perform traceroute for every included URL 
  * GeoIP conversion from every IP included.
  * send the results to our hidden service (**XXX TODO we've to write here the definitive one**)

This permit to show, from a news media, all the nations capable to know that a
specific users is visiting.

## Why care about these results ?

This has been done by the NSA, intercepting the advertising network of Angry Birds
game. Angry Birds was the most deployed game, but was still an option for a 
citizen. Be informed is something more descriptive of a person (and of a group)
will, knowledge and belief, therefore one of the thesis of this project, is expose
how the ADS and tracking business, based on third party injections, is a
damaging behavior for the readers of a news site and for the citizen who relay
on that informative website.


## Countermeasure

**Everyone of these need to be review**, until is not performed a privacy assessment
on these technologies. At the moment I'm not aware if assessment like these has been
done.

  * NoScript (FireFox)
  * SafeScript (Chrome)
  * Disconnect
  * Ghostery 
  * AdBlock+

### A little dream

The tracking elements, acting being present in a multiple website, so if you read
site A, B C and D, the tracking agent present in A B and D know almost 75% of you.

The distributed nature of Internet will always make possible a "C" site without
tracking agent, but for business, SEO or infrastructural needs, the creation of 
independent and trackless site is diminishing constantly.

One of the scaring effect of the tracking is into the subject of the tracking. not
only your path around the internet, but also who give to you that link, from where
you've found this information. because if a trackless website point to a tracked 
one, your presence on the trackless is still tracked.

And seldom, when someone share a link, this link contain an unique identifier 
used to recognize users connected by other means (eg: sharing link via chat or
via mail: the tracker do not know in which way, but know you and who as shared
the link are in some way connected)

**So, my little dream, is do not bring anymore users on website. When you see an
information that deserve to be shared, just create a partial temporary and static copy
and share that. There is no needs to trigger in your recipient device some network
activity: those activity are used against you and your recipients**

### Note

a brief presentation related on Italian media is here: [Online users tracking: effect, responsibility and countermeasures](http://vecna.github.io)

