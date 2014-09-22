## Some ideas to refactor

### Classes

phantomjs and traceroute

check how OONIprobe works, if can be helpful for the long term and integration.

### Logic

Resolv for every inclueded host
Reverse for every resolved IPv4
if match a CDN => mark as such => consider a table CDN/Country

### External

    * curl -v http://freegeoip.net/json/8.8.8.8
    * Hostname was NOT found in DNS cache
    *   Trying 192.151.154.154...
    * Connected to freegeoip.net (192.151.154.154) port 80 (#0)
    > GET /json/8.8.8.8 HTTP/1.1
    > User-Agent: curl/7.35.0
    > Host: freegeoip.net
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < Access-Control-Allow-Origin: *
    < Content-Type: application/json
    < Date: Sat, 09 Aug 2014 02:53:09 GMT
    < Content-Length: 186
    < 
    {"ip":"8.8.8.8","country_code":"US","country_name":"UnitedStates","region_code":"","region_name":"","city":"","zipcode":"","latitude":38,"longitude":-97,"metro_code":"","area_code":""}

## DNS

    >>> import socket
    >>> socket.gethostbyname('static.ak.facebook.com')
    '213.254.17.176'
    >>> socket.gethostbyaddr('213.254.17.176')
    ('a213-254-17-176.deploy.akamaitechnologies.com', [], ['213.254.17.176'])
    >>> socket.gethostbyaddr('8.8.8.8')
    ('google-public-dns-a.google.com', [], ['8.8.8.8'])
    >>> socket.gethostbyname('t1.gstatic.com')
    '74.125.232.148'
    >>> socket.gethostbyaddr('74.125.232.146')
    ('mil02s05-in-f18.1e100.net', [], ['74.125.232.146'])


So, the question is: can I map all the CDN technology, and this helps when tracedpaths finish in the local country ?

## source IP and topology

    http http://json.whatisyourip.org/


## mozilla_tld_file.dat

Has been retrivered from (they are the same):

and this is used by tldextract

http://mxr.mozilla.org/mozilla-central/source/netwerk/dns/effective_tld_names.dat?raw=1
https://raw.github.com/mozilla/gecko-dev/master/netwerk/dns/effective_tld_names.dat


## Traceroute and GeoIP:

1) remove GeoIP from client execution,
2) rely on fiorix: qq@qq:~/go/src/github.com/fiorix/freegeoip$ ./freegeoip 


## MaxMind

http://dev.maxmind.com/geoip/legacy/geolite/

ASN + GeoIP city + GeoIP Country

Version 2 late 2014: http://dev.maxmind.com/geoip/geoip2/geolite2/
how used MaxMind db: http://stackoverflow.com/questions/tagged/geoip ?


# True TODO

  * class + UT + dump/load for Media
    * enhance with (stuff from lcamtuf)[https://sites.google.com/a/chromium.org/dev/Home/chromium-security/client-identification-mechanisms]
    * TLDextract seriously
  * class + UT + dump/load for PhantomJS, enhance the fucking collection and behavior emulation.
  * class + UT + dump/load for Hosts
  * tcptraceroute option
  * version check
  * maxmind integration and not more GeoIP
  * I/O messagging left only in the called
  * multithread


