#!/usr/bin/python
# This script run only at the start of the 'Supporter' virtual box
# is intended to traceroute 8.8.8.8 and figure out from which country
# you're making running this box.


# TODO NEED TO INCLUDE THE CONTENT OF perform_analysis

from subprocess import Popen, PIPE
import re, sys
import GeoIP

if len(sys.argv) == 2:
    target_host = sys.argv[1]
else:
    target_host = 'venere.inet.it' 

p = Popen(['traceroute', '-n', '-w', '0.5', '-q', '10', '-A', target_host], stdout=PIPE)

tmpfile = file('venere.log', "w+")

iplist = []
while True:
    line = p.stdout.readline()
    if not line:
        break
    print line,
    tmpfile.write(line)

    # this prevent the IP match show below
    if line.startswith('traceroute to'):
        continue
    # traceroute to casellante.winstonsmith.org (109.168.101.146), 30 hops ...
    # 1  172.16.1.1 (172.16.1.1)  2.870 ms  2.868 ms  3.762 ms
    # 2  * * *

    ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
    if not ip:
        continue
    iplist.append(ip)

tmpfile.close()

gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
country_travel_path = {}
counter = 0

print len(iplist), "HOP passing thru",
for ip in iplist:

    # is always as list ['x.x.x.x'] sometime more than 1
    if isinstance(ip, list):
        ip = ip[0]

    print gi.country_code_by_addr(ip),
    country = gi.country_name_by_addr(ip)
    country_travel_path.update({counter:country})
    counter += 1

print "."
