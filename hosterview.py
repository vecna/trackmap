#!/usr/bin/python
# -*- coding: utf-8 -*-
# utility to check media list and/or single service

import sys
import socket
import os
import shutil
import re
import GeoIP
import pprint

from libtrackmap import media_file_cleanings, PERMITTED_SECTIONS
from perform_analysis import do_phantomjs
from termcolor import colored
from subprocess import Popen, PIPE

# remind: I've tried to use this RankApi service
#
# key = "-Q8XZ1mKzMEMQbTsSKnK5H3W6hXKVNl_vxhLyY9TiWgZZjbgijrXTqYIY3SGGbts"
# resp = requests.get('http://www.rankapi.net/api/v1/pagerank.json?key=%s&url=%s' % (key, url) )
# rankinfo = resp.json()
# print counter, "\t", url, "---", rankinfo['url']
# if ranked.has_key(rankinfo['rank']):
#     ranked[rankinfo['rank']].append(url)
# else:
#     ranked.update({ rankinfo['rank'] : [ url ] })



if __name__ == '__main__':

    if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print "Host overview - debug utility for TrackMap "
        print "%s [Geo|phantom|DNS] [ media_list [section] | host ]" % sys.argv[0]
        print "\tGeo: traceroute + GeoIP"
        print "\tphantom: HTTP included url and unique URL count"
        print "\tDNS: resolve + reverse"
        quit(-1)

    command = sys.argv[1]

    if command not in [ 'DNS', 'phantom', 'Geo' ]:
        print "Error unexpected command:", command
        quit(-1)

    # understand the third argument
    target = sys.argv[2]
    if os.path.isfile(target):
        print "Found file", target, "using as media list"
        # reading media list, cleaning media list and copy media list
        cfp = file(target, 'r')
        unclean_lines = cfp.readlines()

        print colored(" ࿓  Importing media list:", 'blue', 'on_white', attrs=['underline'])
        media_entries = media_file_cleanings(unclean_lines)
        cfp.close()
    else:
        print "Not found file", target, "assuming as single host"
        media_entries = { target : 'hand' }

    if not os.path.isdir('_hostseer'):
        os.mkdir('_hostseer')

    def check_section(kind):

        if kind and len(sys.argv) == 4:
            assert sys.argv[3] in PERMITTED_SECTIONS, PERMITTED_SECTIONS
            return kind != sys.argv[3]


    if command == 'phantom':

        for media, kind in media_entries.iteritems():

            if check_section(kind):
                    continue

            urldir = os.path.join('_hostseer', media)
            if os.path.isdir(urldir):
                print "Removing", urldir,
                shutil.rmtree(urldir)

            print "+ Creating directory", urldir
            os.mkdir(urldir)

            do_phantomjs(False, media, urldir, kind, '_hostseer')

    if command == 'Geo':

        for media, kind in media_entries.iteritems():

            if check_section(kind):
                continue

            try:
                resolved_ip = socket.gethostbyname(media)
            except Exception:
                print colored("Failure in DNS resolution! %s" % media, "red")
                continue

            gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
            p = Popen(['traceroute', '-n', '-w', '1.0', '-q', '1', '-A', resolved_ip], stdout=PIPE)

            print colored("Target: %s %s" % (media, resolved_ip), "green")
            while True:
                line = p.stdout.readline()
                if not line:
                    break

                # this prevent the IP match show below
                if line.startswith('traceroute to'):
                    continue

                ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
                if not ip:
                    continue
                ip = ip[0]
                c_code = gi.country_code_by_addr(ip),
                country = gi.country_name_by_addr(ip)

                try:
                    reverse_name = socket.gethostbyaddr(ip)
                    reverse_name = reverse_name[0]
                except Exception:
                    reverse_name = ip

                line = line[:-1]
                print colored(" %s\t [%s] %s %s" % (c_code[0], line, reverse_name, country), 'blue', 'on_white')

    if command == 'DNS':

        ip_map = {}
        for media, kind in media_entries.iteritems():

            if check_section(kind):
                continue

            try:
                resolved_v4 = socket.gethostbyname(media)
            except Exception as xxx:
                print media, "broken", xxx
                continue

            ip_map.setdefault(resolved_v4, []).append(media)

        pprint.pprint(ip_map)
        print "Press enter..."
        sys.stdin.read(1)

        reverse_map = {}
        for v4, hostlist in ip_map.iteritems():

            try:
                socket.setdefaulttimeout(1.5)
                reverse_name = socket.gethostbyaddr(v4)[0]
            except Exception as xxx:
                print xxx, "“", v4,"“ ", pprint.pprint(hostlist)
                continue

            reverse_map.update({ v4 : reverse_name })

        pprint.pprint(reverse_map)

