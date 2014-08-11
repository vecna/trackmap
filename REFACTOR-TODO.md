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
{"ip":"8.8.8.8","country_code":"US","country_name":"United States","region_code":"","region_name":"","city":"","zipcode":"","latitude":38,"longitude":-97,"metro_code":"","area_code":""}

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


  * can I map all the CDN technology, and this helps when path likes finish in the local country


