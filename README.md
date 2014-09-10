# TrackMap project

The TrackMap project is research by [Claudio ࿓  vecna](https://twitter.com/sniffjoke), develped with [Tactical Tech](http://www.tacticaltech.org), as part of the [MyShadow](http://myshadow.org) project.

*When you access the national media from your country, your Internet connection is being tracked by multiple third parties. And this happens constantly*. That's what we aim to illustrate.

Our aim is to show where our data travels when we visit our favorite news websites through a visualization. We are currently looking for people to collaborate with in various countries in the world which would make this project possible. 

## You, your country and the code 

This repository contains the script and the data source needed to generate our needed data.

The collection of data needs to happen in a distributed way, _which means that the script needs to run from each of the selected countries_. This is important because the network and the trackers behave differently based on the provenience country of the user. 

### Is it your country analyzed in TrackMap ?

If the answer is **NO**: two reasons are possible:

  * No one has review or created the **media list**, check in [this directory](https://github.com/vecna/helpagainsttrack/tree/master/verified_media) and look at the expected format on the bottom of the page. An unverified media list [can be present here](https://github.com/vecna/helpagainsttrack/tree/master/unverified_media_list), if is not, sent to us an email at **trackmap** at **tacticaltech** dot **org** (because we have some not refined list usable as starter) of provide to us list from your own.

  * No one has yet runs the script from your country: In this case, read the sections below

If the answer is **YES**: perfect, this mean that someone has already run the script: you can still help, because different ISP and different Geographical locations in a country brings different results, having multiple feedback can be useful for further analysis and comparison.

### How you can help ? 

If you're a **Media aware citizen**, we need a reliable media list for every country. In the chapter above is explained what is important, use git to help us or open an issue.

If you're a **Linux user** you can help running the script and collecting result from your country. Is needed a distributed effort, because the Internet is perceived differenty from different location. You can run the script explained below, and it will automatically send the results to our hidden service.

### Use the test script

The procedure reported use an apt-get based system (Debian/Ubuntu etc), and a couple of experimental option (Vagrant and Docker)
**RUN THIS TESTS VIA Tor IS POINTLESS**: because the important data are obtained via traceroute, and works in a lower level than Tor (also works in UDP, that cannot be anonymised), so if you don't feel safe, just don't contribute. anyway no personal information are collected, your computer is just used to see "how your ISP connects citizen like you"

Tor is used when the script has completed the collection, because we anonymize the users interacting with us.

### Ubuntu automation 

only tested in Ubuntu (may work in other distribution, but is untested)
Create a directory to store the project files and change directory there:

    mkdir trackmap
    cd trackmap
    wget -c https://raw.githubusercontent.com/vecna/helpagainsttrack/master/setup.sh
    bash setup.sh
    
This script uses `sudo` to execute some commands, so it will ask for your password when it executes. The project
scripts are installed in a subdirectory called *helpagainsttrack*.

If you read "OK" at the end, go to the section [Run the test script](https://github.com/vecna/helpagainsttrack#run-the-test-script)

### Installation

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
    ./fetch_phantomjs.sh

## Run the test script

Change directory to the directory where you installed the test script and run:

    ./perform_analysis.py -c NAME_OF_YOUR_COUNTRY

If you have not installed phantom 1.9.2 on the path specified above, but are using your distribution's phantomjs, add 
the option **-l** (local phantom):

    ./perform_analysis.py -c NAME_OF_YOUR_COUNTRY -l

To see a list of countries, just tape something random, the script show the available countries (or check [here](https://github.com/vecna/helpagainsttrack/tree/master/verified_media) )

### Clean the data

When you've completed the collection, and the script report:

    Data collected has been sent, Thank You! :)

you can safely delete the directory **trackmap** created at the beginning

### (Some yours) Information requested

When the script start asks for four (**they are optional, but useful**) Information that **will never be released**: 

  * Your name: is not important, but if we already known you or meet you in the future, we can say **thankyou** :)
  * Your city: this maybe relevant because results from city very far among, reports different results.
  * Your contact: an email or jabber, but is a free text. Put also a GPG fingerprint if you like, can be useful if eventually we've to contact you in the future. very likely, to run again the test.
  * Your ISP: if you know it, can be useful, because in the same country different ISP return lightly different results.

### Step details, timing and resources

Few Bandwidth/CPU/disk resources are needed. Is not possible make a precise estimation, because the executed operations  depends directly from the amount of media website under analysis, anyhow, based on the past experience:

  * A list with around 200 media site starts for (200 + 50) times a "one time browser". It use 5-10 seconds each. more or less expend 300 Kb for each website ( ~75 megabyte used in download ).
  * For every media fetch, 7 to 20 hosts are discovered to be included. the script need process them in such ways:
    * every host is resolved in an IPv4 address, this help to minimize duplicated result (happen quite often that different hosts has the same IP address). Depends on the first point, but commonly are between 1400 - 1700 unique hosts. This operation require 40 to 90 minutes.
    * For every resolved IPv4, perform a reverse DNS resolution. This operation is slower than the previous one, require at lest 60 to 120 minutes.
  * Then, for every unique IPv4 address, start a traceroute. it use at least four hours (up to 8), expend not so much bandwidth.
  * **The script require more or less 12 hours to be completed, and at the end send to us 20-30 megabytes of data**

**You can interrupt the script execution with control+C**, and when the command is given again, **it resume the previous execution**. To start a new collection, remove the 'output' directory. 

**Is very likely have a stable network**. If you can avoid WI-FI (or be physically near the access point), it is better.

### The operation performed by the script

  * an HTTP connection (using phantomjs) to every news media under analysis
  * Collect all the URL included as third party (trackers, ADS, social)
  * Dump &lt;object&gt; elements ( Can be used for future analysis. analyzing this code, we can point out [who are the worst tracker ;) ](http://rt.com/usa/175116-white-house-website-canvas-fingerprinting/) this analysis is not yet done.)
  * Perform traceroute for every included URL 
  * GeoIP conversion from every IP included.
  * send the results to our hidden service (**mzvbyzovjazwzch6.onion**)

This shows all the nations capable of knowing which users are visiting the (selected) news media.


### Long term project support (experimental)

If you're a **Linux user** with a constantly running box and few times:

  * You can run the **Vagrant script** explained  below to create a virtual machine _under our control_, where we can perform the tests (less effort for you, and we will eventually send you an email asking you to start your box when the tests get updated).

Please read [Vagrant usage description](https://github.com/vecna/helpagainsttrack/tree/master/Vagrant)

### Docker image (experimental)

A [Docker](https://www.docker.com/) image has been created for this tool, using the Dockerfile provided in the test 
tool directory. If you wish to use this, you can run the test tool using:

    docker run -t -i pvanheus/helpagainsttrack -c NAME_OF_YOUR_COUNTRY
    
## Technopolitical goal

We know **online business model is mostly based on tracking**, who is producing content is just pushing hard in order to get more visibility, clicks and provide advertising. 
If you don't want that a specific organization get money from your interaction because you don't like it, or you don't want be tracked by that company, your only option is the 'opt out'.
But what are the options ? this is one of the first goals of TrackMap: make you aware of the amount of tracking involved in your daily navigation. We've addressed the media, because they represent something touching all the active citizens in a country.

But why bother if Google, NewYorkTimes or others track your behavior and interests ? It's pointless to be scared by those organizations, after all, they have done nothing bad against users.
But sadly, these data are extremely valuable for market and political strategies, and those companies has been targeted by Intelligence Agencies for those reason. So it's easier to understand what we want show:
tracking is not something performed by Internet Companies only, but something used actively as Nation assets.
And Nations are easier to be perceived as troublesome, instead of an abstract Internet Company. Or not? What if the main medias of a country are leaking (and are they aware ?) the citizen interest to a political enemy ?

With TrackMap we show the invisible links between a news reader from a nation and all the nation that can eventually snoop on their behavior. on a foreign network, you have no rights.

**Is this paranoia ?**

No ;) This has been done by the NSA, which intercepts the advertising network of the Angry Birds game. Angry Birds was the most deployed game, but was still an option for citizens. News media, however, are accessed by the majority of populations around the world and by tracking which websites users access, third parties can gain a unique insight into the types of interests people have, their ideas, beliefs and concerns. In other words, by tracking news media, third parties can map out the interests of individuals and groups and potentially target them. The aim of this project is to expose how the ADS and tracking business works based on third party injections.


### Theoretical elements

In this (very first version) of the TrackMap project we want answer to the following questions:

  * "Is the online advertising business a potential asset to intelligence agencies ?"
  * "Are users aware of the extent to which their data and browsing habits are exposed on a daily basis?"
  * "Are privacy activists aware of their network path and of its implications ?"
  * "Is online advertising and tracking a good business model for online media ?" (In this case, media is a website which constantly publishes updates on relevant events and their consultancy is therefore not just an option for users, but also a **need** for users).

Due to limited resources from our side, our research might face the following limitations:


  * The GeoIP resolution, from an IP address to a Country, might return a continent (for example, some classes are assigned to Europe, without more precision about the physical location).
  * We're performing traceroute without checking if the resource included is in https/http2 (this happens very seldom, and in these cases we consider the data stored in the recipient country but not exposed in-transit interception and manipulation)
  * Some service providers use Content Delivery Network and this means that in order to interact with them, this might be resolved as part of the same country of the user, also if the content is obviously stored by a foreign country.
  * We cannot know if a service has some Cloud Provider as a backend
  * We cannot automatize the seeking of company information over every tracking agent
  * GeoIP applied to traceroute may return unexpected or doubtful results. A technical progress can be used by interpolating GeoIP + Autonomous System + TLD/domain analysis. GeoIP for sure show: if an IP address is in a country or if an IP address is assigned to a company based on a certain country. 

For example:

      traceroute to www.zerocalcare.it (144.76.179.61), 30 hops max, 60 byte packets
       1  172.16.1.1 [*]  6.556 ms
       2  151.6.151.72 [AS1267]  13.176 ms
       3  151.6.92.105 [AS1267]  15.431 ms
       4  151.6.0.80 [AS1267]  16.456 ms
       5  151.6.2.50 [AS1267]  19.675 ms
       6  80.81.192.164 [AS6695]  33.343 ms
       7  213.239.245.6 [AS24940]  42.645 ms
       8  213.239.245.217 [AS24940]  40.540 ms
       9  213.239.245.170 [AS24940]  66.506 ms
      10  213.239.248.196 [AS24940]  49.232 ms
      11  144.76.158.83 [AS24940]  59.938 ms
 
**11 HOP passing thru None IT IT IT IT DE DE DE DE DE DE**

This is quite easy: the first IP is a private IP address (None), after there are some Italian (my ISP) and then the connection reach a provider in Germany, where the target host is placed. If we take a look hostnames:

      traceroute to www.zerocalcare.it (144.76.179.61), 30 hops max, 60 byte packets
       1  172.16.1.1 (172.16.1.1)  7.504 ms
       2  151.6.151.72 (151.6.151.72)  13.879 ms
       3  151.6.92.105 (151.6.92.105)  20.831 ms
       4  MIOT-RP01-MIOT-T02.wind.it (151.6.0.82)  31.363 ms
       5  MICL-N01-MICA-T02-po02.wind.it (151.6.2.50)  38.390 ms
       6  decix-gw.hetzner.de (80.81.192.164)  36.001 ms
       7  core1.hetzner.de (213.239.245.6)  39.237 ms
       8  core22.hetzner.de (213.239.245.178)  45.404 ms
       9  juniper2.rz20.hetzner.de (213.239.245.158)  46.696 ms
      10  hos-tr6.ex3k3.rz20.hetzner.de (213.239.233.170)  61.476
      11  83.158.76.144-scoundr.el (144.76.158.83)  55.756 ms

Between the hops 5 (from wind.it, my ISP) and 7 (the first gateway of the server I'm contacting) the connection pass throu **decix-gw.hetzner.de**, [DE-CIX](http://en.wikipedia.org/wiki/DE-CIX) is a business to business carrier, that is providing a direct connection between the two ISPs. I don't know if the IP 80.81.192.164 of DE-CIX is phisically in Italy, in Germany, or in some other place: GeoIP resolve them as "DE" because is assigned to the Germanic company DE-CIX.

In other situation, the API returned by TrackMap (*they will be documented, but at the moment the service is not yet released*) return a more unexpected result like:

    {
        "company": "Twitter", 
        "country_chain": [
            null, 
            "South Africa", 
            "South Africa", 
            "South Africa", 
            "South Africa", 
            "South Africa", 
            "South Africa", 
            "United Kingdom", 
            "United States", 
            "United States", 
            "United States", 
            "United States", 
            "United Kingdom"
        ], 
        "host": "platform.twitter.com", 
        "id": "980429ab-5b71-4fd0-8aa7-7eaef4150f84", 
        "is_intended_media": false, 
        "media_id": "005962d0", 
        "media_url": "www.dieburger.com"
    }

This is the GeoIP resolution of a traceroute from the South Africa ISP **Mweb** to the host platform.twitter.com (hosted by a [CND](http://en.wikipedia.org/wiki/Content_delivery_network) managed by edgecastcdn.net )

It's unexpected, maybe, because can sounds weird from South Africa go in UK, in US and then comeback to UK. but this is due to GeoIP resolution, not to an actual continental travel.
This is an extraction of the traceroute collected:

     8  176.67.177.146 [AS10474] 195.777 ms
     9  4.69.166.129 [AS3356] 176.582 ms
    10  4.69.166.17 [AS3356]  215.669 ms

The hop at position 8 is the last one in South Africa:

    $ host 176.67.177.146
    146.177.67.176.in-addr.arpa domain name pointer be-4-778-thd-p-2.mweb.co.za.

The hop in position 9 is localized as UK, and probably is assigned to an England section of the carrier provider:

    $ host 4.69.166.129
    129.166.69.4.in-addr.arpa domain name pointer vl-3501-ve-115.csw1.London1.Level3.net.

But in fact, [Level3](http://en.wikipedia.org/wiki/Level3) is an USA based carrier, and a CDN role is to be near as possible from the client requesting the content, so is very likely possible that connection never reach USA directly. Still, in TrackMap, the connection will be show to reach both UK and USA, because both intelligence agency or lawful enforment (or unlawful interception) can snitch on this connection.

    $ host 4.69.166.17
    17.166.69.4.in-addr.arpa domain name pointer ae-229-3605.edge4.London1.Level3.net.

Just to be complete, the third hop, position 10, is still resolved as London gateway in Level3 carrier, but is recognized as US by GeoIP.


## Countermeasure

**As far as I know, those technologies lack on security/privacy audit**, but ideally they are a good start:

  * [NoScript](http://en.wikipedia.org/wiki/Noscript) (FireFox)
  * SafeScript (Chrome)
  * [Disconnect](https://disconnect.me/)
  * Ghostery 
  * AdBlock+

### A little dream

The tracking elements are well documented in the websites. 
If you read site A, B, C and D, the tracking agent present in A, B and D know almost 75% of information about you.

The distributed nature of the Internet will always make the development of sites like "C" possible: a site without a tracking agent. 
Sadly, due to the online advertising business, mixing between social and ADV, SEO and infrastructural needs, the creation of independent and trackless sites is extremely rare.

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

### Our PGP key

    pub   3200R/0x94E7EF47 2014-08-05 [expires: 2015-08-30]
          Key fingerprint = ABC2 7639 5EE3 3245 A0A1  3973 40E2 6C25 94E7 EF47
    uid                    TrackMap project <trackmap@tacticaltech.org>
    sub   3200R/0x504DEBDF 2014-08-05 [expires: 2015-08-30]

You can retrieve this key via keyserver, of using the [git copy of the Projects key](https://raw.githubusercontent.com/vecna/helpagainsttrack/master/trackmap_ABC276395EE33245A0A1397340E26C2594E7EF47.asc)


