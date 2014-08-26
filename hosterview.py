#!/usr/bin/python
# -*- coding: utf-8 -*-
# utility to check media list and/or single service

import sys
import socket
import os
import json
import shutil
import re
import GeoIP

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

def ip(media_entries):

    ip_map = {}
    for media_host, kind in media_entries.iteritems():
        if kind == 'global':
            continue

        try:
            resolved_v4 = socket.gethostbyname(media_host)
        except Exception as xxx:
            print media_host, "broken", xxx
            continue

        if ip_map.has_key(resolved_v4):
            ip_map[resolved_v4].append(media_host)
            continue

        ip_map.update({resolved_v4 : [ media_host ] })

    unique = 0
    for ipv4, hostlist in ip_map.iteritems():
        if len(hostlist) == 1:
            unique += 1
        else:
            print ipv4, "=", len(hostlist)
            for med in hostlist:
                print med, media_entries[med]
            print "\n"

    print "unique", unique

    with file("myresolved", 'w+') as f:
        json.dump(ip_map, f)


def rank(media_entries):

    counter = 0
    for url, kind in media_entries.iteritems():

        if kind != 'blog':
            continue
        import random

        if counter == 49:
            print "FORCE BREAK"
            break

        counter += 1
    with file("myranked", 'w+') as f:
        json.dump(ranked, f)


if __name__ == '__main__':

    permitted_cmd = ['dns', 'phantom', 'analyze' ]

    if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print "Host overview - debug utility for TrackMap "
        print "%s [DNS|phantom] [ media_list [section] | host ]" % sys.argv[0]
        print "\tDNS: traceroute + GeoIP + resolve + reverse"
        print "\tphantom: HTTP included url and unique URL count"
        quit(-1)

    command = sys.argv[1]

    if command not in ['DNS', 'phantom' ]:
        print "Error, expected '%s' be in %s " % (command, permitted_cmd)
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

    if not os.path.isdir('hostseer'):
        os.mkdir('hostseer')

    def check_section(kind):

        if kind and len(sys.argv) == 4:
            assert sys.argv[3] in PERMITTED_SECTIONS, PERMITTED_SECTIONS
            return kind != sys.argv[3]


    if command == 'phantom':

        for media, kind in media_entries.iteritems():

            if check_section(kind):
                    continue

            urldir = os.path.join('hostseer', media)
            if os.path.isdir(urldir):
                print "Removing", urldir,
                shutil.rmtree(urldir)

            print "+ Creating directory", urldir
            os.mkdir(urldir)

            do_phantomjs(False, media, urldir, kind)

    if command == 'DNS':

        for media, kind in media_entries.iteritems():

            if check_section(kind):
                continue

            try:
                resolved_ip = socket.gethostbyname(media)
            except Exception:
                print colored("Failure in DNS resolution!", "red")
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

