#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This code is a refactor in progress
#
# This software is constantly updated in
# https://github.com/vecna/helpagainsttrack
#
# Is described and used on http://myshadow.org and has been developed by
# Claudio <vecna at globaleaks dot org> April-Sept 2014,
# initially for a personal research, and after with
# Tactical Technology Collective http://tacticaltech.org

try:
    import os
    import re
    import json
    import sys
    import random
    import time
    import shutil
    import socket
    import socks
    import threading

    from datetime import datetime, timedelta
    from optparse import OptionParser
    from subprocess import Popen, PIPE
    from termcolor import colored
    from libtrackmap import sortify, media_file_cleanings
    from tldextract import TLDExtract
    from hashlib import sha1

except ImportError:
    print "TrackMap collection system is not correctly installed"
    print "Follow the README below or mail to trackmap<@>tacticaltech.org"
    print "https://github.com/vecna/helpagainsttrack"
    quit(-1)


class AnalysisLogic:

    GLOBAL_MEDIA_FILE = 'special_media/global'
    outputdir = 'Mout'

    def __init__(self, host_file, options):

        self.host_file = host_file
        self.options = options

    # TODO objectify
    def load_global_file(self):

        global_media_dict = {}
        counter = 0

        with file(AnalysisLogic.GLOBAL_MEDIA_FILE, 'r') as f:
            for line in f.readlines():

                line = line[:-1]

                if len(line) > 1 and line[0] == '#':
                    continue

                # everything after a 0x20 need to be cut off
                line = line.split(' ')[0]
                if len(line) < 3:
                    continue
                counter += 1
                global_media_dict.update({ line : 'global' })

        return global_media_dict, counter

    # TODO objectify
    def media_file_cleanings(self, linelist):
        """
        From the format
        [global]
        http://url
        # comment
        [othersec]
        http://otherweb

        return { 'url': 'global', 'otherweb': 'othersec' }
        """
        retdict = {}
        current_section = None
        counter_section = 0

        assert isinstance(linelist, list)
        for line in linelist:

            line = line[:-1]

            if len(line) > 1 and line[0] == '#':
                continue

            # everything after a 0x20 need to be cut off
            line = line.split(' ')[0]

            if len(line) < 3:
                continue

            if line.startswith('[') and line.find(']') != -1:
                candidate_section = line[1:-1]

                if not candidate_section in PERMITTED_SECTIONS:
                    print "The section in", line, "is invalid: do not match with", PERMITTED_SECTIONS
                    quit(-1)

                # if we had 'global' section: is special!
                if candidate_section == 'global':
                    global_section, counter_section = self.load_global_file()
                    retdict.update(global_section)
                    current_section = candidate_section
                    continue

                if current_section:
                    # print "Section", current_section, "has got # entries", counter_section
                    counter_section = 0

                current_section = candidate_section
                continue

            cleanurl = line
            if current_section not in [ 'national', 'local', 'blog' ]:
                print "detected URL", cleanurl, "without a section!"
                quit(-1)

            if retdict.has_key(cleanurl):
                print "Note:", cleanurl, "is duplicated"

            retdict.update({ cleanurl: current_section })
            counter_section += 1

        # the last section is printed here
        if current_section:
            # print "Section", current_section, "has got # entries", counter_section
            pass # this is because is commented the line above

        return retdict

    def do_analysis(self):

        cfp = file('verified_media/test', 'r')
        unclean_lines = cfp.readlines()

        print colored(" ࿓  Importing media list:", 'blue', 'on_white', attrs=['underline'])
        media_entries = self.media_file_cleanings(unclean_lines)
        cfp.close()


        for cleanurl, media_kind in media_entries.iteritems():

            loadav = os.getloadavg()
            if loadav[0] > 5:
                print "Load average", loadav, "sleeping!"
                time.sleep(30)
            else:
                print "Load average", loadav, "common three seconds sleep"
                time.sleep(3)

            x = MyThread()
            x.setup(cleanurl, media_kind, False)
            x.start()

            # phantom_stats.setdefault(crawl.retinfo, []).append(cleanurl)

        print "End"
        quit(0)



class MyThread (threading.Thread):

    def setup(self, CU, MK, LP):
        """
        :param CU: is Unclean Url but, amen
        :param MK:
        :param LP:
        :return:
        """

        self.local_phantomjs = LP
        self.cleanurl = CU
        self.media_kind = MK

    def run (self):

        crawl = Phantom(self.cleanurl, self.media_kind, self.local_phantomjs)

        if crawl.exists:
            crawl.load(Phantom.saved_attrs)
            print "Resumed: %s" % crawl
            return

        crawl.software_execution()
        crawl.inclusion_analysis()
        crawl.title_and_cookies()
        crawl.dump(Phantom.saved_attrs)
        print "Completed: %s" % crawl

        print "Thread:", threading.active_count()









hiddenservice_tuple = ('mzvbyzovjazwzch6.onion', 80)

ANALYSIS_VERSION = 4


class TraceStats:

    v4_paths = {}
    three_hundres = 0

    def __init__(self, v4_path=None):

        if not v4_path:
            v4_path = []

        assert isinstance(v4_path, list)
        for hopcount, ip in enumerate(v4_path):
            TraceStats.v4_paths.setdefault(hopcount, [ip]).append(ip)

    def dump_stats(self, OUTPUTDIR):

        analysis_test = os.path.join(OUTPUTDIR, '_verbotracelogs', 'TraceStats.json')
        with file(analysis_test, 'w+') as f:
            json.dump(TraceStats.v4_paths, f)

    @staticmethod
    def three_hundred_sadness():
        """
        This function is called every time a 20 "*" are returned by a Traceroute.
        Mean that network is down or ICMP are filtered.
        Is called three hundred because before there was 10 probes for 30 hop
        """
        TraceStats.three_hundres += 1

        if TraceStats.three_hundres >= 10:
            print "\n\n"
            print colored("\tHas been detected ten time a complete Traceroute failure", "red")
            print colored("\tMaybe the network is down, maybe your host is filtering ICMP", "red")
            print colored("\tIn both cases, the test is interrupted.", "red")
            print "\n"
            print colored("\tIf the test has reach more than 10 traceroute, then:", "red")
            print colored("\tAdd the option -i to perform a slow and sure test", "red")
            print "\n\n"
            quit(-1)


def do_wget(pathdest):

    if os.path.isfile('index.html'):
        raise Exception("Why you've an index.html file here ? report this error please")

    p = Popen(['wget', '--timeout', '10', '--tries', '3', 'http://json.whatisyourip.org/'], stdout=PIPE, stderr=PIPE)
    while True:
        line = p.stderr.readline()
        if not line:
            break
        print line,

    if os.path.isfile('index.html'):
        shutil.move('index.html', pathdest)
    else:
        with file(pathdest, 'w+') as fp:
            fp.write("Error :\\")
        print colored("Error in get location IP address in %s" % pathdest, 'red')


class TrackMapBase:

    def dump(self, dump_keys):

        # assert not self.exists, "you've to call redo()"
        assert not os.path.isfile(self.jsonfile), "file exists and no redo()"
        # TODO lock remove ?

        dump_dict = {}
        for k in dump_keys:
            dump_dict.update({
                k : getattr(self, k)
            })
        with file(self.jsonfile, 'w+') as jfp:
            json.dump(dump_dict, jfp)

        sx = os.stat(self.jsonfile)
        self.log("dump() %s %d bytes" %
                 (self.jsonfile, sx.st_size ) )

    def load(self, expected_keys):

        assert self.exists, "file do not exist nor check'd"
        with file(self.jsonfile, 'r') as jfp:
            imported_json = json.load(jfp)

        assert isinstance(imported_json, dict)
        assert len(imported_json.keys()) == len(expected_keys)
        for k, v in imported_json.iteritems():
            setattr(self, k, v)
            if isinstance(v, list):
                self.log(" Loaded %s (%d) elements" % (k, len(v)) )

    def log(self, msg):
        self.msg_collection.append(msg)

    def flush(self, recap_string):

        print colored(recap_string, 'blue', 'on_white')
        for msg in self.msg_collection:
            print "  ", msg
        self.msg_collection = []

    def __init__(self):
        """
        This is the concept, every element in this analysis,
        there are a jsonfile where dump or load stuff.

        the JSONfile is always expressed as 'directory/file.json'
        """
        self.msg_collection = []


    def redo(self):

        if not self.exists:
            self.log("Called redo when the file is new ?")

        # I expect no failure here
        os.unlink(self.jsonfile)
        self.exists = False

    def check_status(self):

        assert self.jsonfile, "missing of jsonfile"

        if os.path.isfile(self.jsonfile):
            self.exists = True
        else:
            self.exists = False

            # and create needed dir
            dirseq = '/'.join(self.jsonfile.split('/')[:-1])
            try:
                os.makedirs(dirseq)
            except OSError as OEx:
                pass

            # TODO create lock file?



class wwwURL(TrackMapBase):

    @classmethod
    def _segment_TLD(cls, host, dict_to_fill):

        TLDio = TLDExtract(cache_file='mozilla_tld_file.dat')

        dnsplit= TLDio(host)
        dict_to_fill['domain'] = dnsplit.domain
        dict_to_fill['tld'] = dnsplit.suffix
        dict_to_fill['subdomain'] = dnsplit.subdomain

    saved_attrs = ['url', 'hosts_segment', 'company', 'ipv4', 'reverse']

    def __repr__(self):
        x = "%s => %s = %s <= %s" % (self.url, self.hosts_segment,
                self.ipv4, self.reverse)
        return x

    def __init__(self, url):

        TrackMapBase.__init__(self)
        self.log('wwwURL %s' % url)

        self.url = url
        self.hash = sha1(url).hexdigest()[:6]

        self.host = None
        self._url_cleaner() # self.host is defined here

        self.hosts_segment = {
            'domain' : None,
            'tld' : None,
            'subdomain' : None,
        }
        # self.hosts_segment is populated here:
        wwwURL._segment_TLD(self.host, self.hosts_segment)

        self.company = None

        # TODO with CDN analysis
        self.reverse_segment = None
        self.reverse_company = None

    def double_dns(self, shitty_internet):
        import pprint

        tmp = DNS(shitty_internet)
        self.ipv4 = tmp.get_resolve(self.host)
        if self.ipv4:
            self.reverse = tmp.get_reverse(self.ipv4)
        else:
            self.reverse = None

        # pprint.pprint(DNS.host_resolved)
        # pprint.pprint(DNS.ip_reversed)


    def assign_jsonfile(self, phantom_dir):

        self.jsonfile = os.path.join(
            phantom_dir, "%s.%s" % (self.host, self.hash))

    def _url_cleaner(self):

        if self.url.startswith('http://'):
            cleanurl = self.url[7:]
        elif self.url.startswith('https://'):
            self.log(colored("Ignored https in %s" % self.url, 'red'))
            cleanurl = self.url[8:]
        else:
            self.log(colored("Error/Invalid protocol in: %s" % self.url, 'red'))
            return False

        while cleanurl[-1] == '/':
            cleanurl = cleanurl[:-1]

        dirtyoptions = cleanurl.find("?")
        if dirtyoptions != -1:
            cleanurl = cleanurl[:dirtyoptions]

        self.host = cleanurl.split('/')[0]
        return True



#    def __repr__(self):
#        reprurl = ("%sݐ" % self.url[:20]) if len(self.url) > 20 else self.url
#        return "%s %s" % (self.media_kind[0].upper(), reprurl)




class Phantom(TrackMapBase):
    """
    Logical flow:

     * take one media as argument,
       * every media is a Media object
    * every Phantom obj has a directory, called $K_$Media_$HASH
    Inside this directory, for every included url + media url:
      * $host.$hash -> with wwwURL dump
    * every Phantom obj has $K_$Media_$HASH/_PHANTOM.json
    """
    saved_attrs = ['title', 'ahref_links', 'inclusion_results']

    def __init__(self, media_url, media_kind, local_phantomjs):

        TrackMapBase.__init__(self)

        self.binary = 'phantomjs' if local_phantomjs else './phantom-1.9.2'
        self.starting_time = datetime.utcnow()

        self.media = wwwURL(media_url)
        self.media.double_dns(True)

        self.media_kind = media_kind
        self.urls_analysis = None

        self.dump_directory = os.path.join(
            AnalysisLogic.outputdir,
            '%s_%s_%s' % (media_kind[0].upper(), self.media.host, self.media.hash) )

        self.jsonfile = os.path.join(self.dump_directory,
                                     '_PHANTOM.json')
        self.check_status()

        # Media has a dedicated file, setting up here
        self.media.assign_jsonfile(self.dump_directory)

        self.tmp_directory = "/dev/shm/phantom-%s" % self.media.hash
        # self._clean_dir(self.tmp_directory)

    def __repr__(self):
        x = "[%s] %s" % ( self.media_kind,
                          self.media.hosts_segment)
        if hasattr(self, 'inclusion_results'):
            x = "%s = %s" % (x, self.inclusion_results)
        return x

    def _clean_dir(self, shm):

        if os.path.isdir(shm):
            shutil.rmtree(shm)
        os.mkdir(shm)

    def title_and_cookies(self):
        """
        Todo: cookies, local storage, ahref_, title, meta ?
        """
        self.ahref_links = "skip"

        title_file = os.path.join(self.tmp_directory, '__title')
        if os.path.isfile(title_file):
            self.title = file(title_file).readline()
        else:
            self.title = ""

    def inclusion_analysis(self):
        """
        Read in the shm directory and fill the urls_analysis dict
        """
        self.inclusion_results =  {
            'same_host' : 0,
            'same_domain' : 0,
            'external': 0,
            'total' : 0,
        }
        included = file(os.path.join(self.tmp_directory, '__urls'), 'r').readlines()
        self.included_obj = []
        for url_string in included:
            if not self.url_validate(url_string[:-1]):
                continue
            resource = wwwURL(url_string)
            resource.assign_jsonfile(self.dump_directory)
            resource.check_status()

            if resource.exists:
                resource.load(wwwURL.saved_attrs)
                continue

            resource.double_dns(False)
            self.included_obj.append(resource)

            resource.dump(wwwURL.saved_attrs)

            if self.media.hosts_segment['subdomain'] == resource.hosts_segment['subdomain']:
                self.inclusion_results['same_host'] += 1
            elif self.media.hosts_segment['domain'] == resource.hosts_segment['domain']:
                self.inclusion_results['same_domain'] += 1
            else:
                self.inclusion_results['external'] += 1



    def url_validate(self, included_url):
        if included_url.startswith('data:'):
            return None
        if included_url.startswith('about:blank'):
            return None
        if included_url.startswith('http://') or included_url.startswith('https://'):
            return included_url

        self.log(colored("Unexpected included URL format: %s" % included_url, 'red'))
        return None




    def write_interruption_line(fp, content, start=True):
        interruption_line = 78
        if len(content) % 2:
            content = "%s " % content

        interruption_line = (interruption_line / 2) - len(content) - 2

        if start:
            fp.write("/%s %s %s\\\n" % (
                (interruption_line * "-"), content, (interruption_line * "-")
            ))
        else:
            fp.write("\%s %s %s/\n\n" % (
                (interruption_line * "-"), content, (interruption_line * "-")
            ))

    def software_execution(self):

        print "software execution"

        # is just a blocking function that execute phantomjs
        p = Popen([self.binary,
                   '--local-storage-path=%s/localstorage' % self.tmp_directory,
                   '--cookies-file=%s/cookies' % self.tmp_directory,
                   'collect_included_url.js',
                   self.media.url, self.tmp_directory], stdout=PIPE)

        self.log(colored("Executing phantomjs on %s" % self, 'green'))

        # phantomlog = file(os.path.join(OUTPUTDIR, "phantom.log"), "a+")
        # write_interruption_line(phantomlog, url, start=True)

        # if not os.path.isfile(os.path.join(destfile, '__title')):
        #     print colored("__title file not generated! ", "red"),
        #     return False

        # print colored(" + Executing %s on: %s" % (binary, url), "green"),
        while True:
            line = p.stdout.readline()
            if not line:
                break
            print colored(line, 'green'),
        #     phantomlog.write(line)

        # write_interruption_line(phantomlog, url, start=False)
        # phantomlog.close()

    def validate_phantomjs_output(self):

        urlfile = os.path.join(self.dump_directory, '__urls')
        urlfp = file(urlfile, 'r')
        included_url= urlfp.readlines()
        urlfp.close()

        print "included", len(included_url)


class DNS:

    # host : ip
    host_resolved = {}

    # ip : reverse
    ip_reversed = {}

    def __init__(self, shitty_internet):

        self.resolve_timeout = 0.5
        self.reverse_timeout = 1.2

        if shitty_internet:
            self.resolve_timeout *= 1.8
            self.reverse_timeout *= 1.8

    def get_resolve(self, host):
        """
        May return None
        """
        timeout = self.resolve_timeout
        current_resolved = {
            'retry': 0,
            'resolved' : None,
            'error': None
        }

        if DNS.host_resolved.has_key(host):
            current_resolved = DNS.host_resolved[host]
            if current_resolved['resolved']:
                return current_resolved['resolved']
            if current_resolved['retry'] == False:
                print "only here False"
                return None
            if current_resolved['retry']:
                timeout *= current_resolved['retry']

            if timeout > 4:
                current_resolved['retry'] = False
                DNS.host_resolved.update({
                    host : current_resolved
                })
                return None

        try:
            socket.setdefaulttimeout(timeout)
            resolved_v4 = socket.gethostbyname(host)
            current_resolved['resolved'] = resolved_v4
            DNS.host_resolved.update({
                host : current_resolved
            })
            return resolved_v4
        except Exception as xxx:
            current_resolved['error'] = xxx
            current_resolved['retry'] += 1.1
            DNS.host_resolved.update({
                host : current_resolved
            })
            return None

    def get_reverse(self, ipv4):

        timeout = self.reverse_timeout
        current_reverse = {
            'retry': 0,
            'reverse_set' : None,
            'error': None
        }

        if DNS.ip_reversed.has_key(ipv4):
            current_reverse = DNS.ip_reversed[ipv4]
            if current_reverse['reverse_set']:
                # note, is a set composed by three element
                return current_reverse['reverse_set'][0]
            if current_reverse['retry'] == False:
                return None
            if current_reverse['retry']:
                timeout *= current_reverse['retry']

            if timeout > 4:
                current_reverse['retry'] = False
                DNS.ip_reversed.update({
                    ipv4 : current_reverse
                })
                return None

        try:
            socket.setdefaulttimeout(timeout)
            reversed_set = socket.gethostbyaddr(ipv4)
            current_reverse['reverse_set'] = reversed_set
            DNS.ip_reversed.update({
                ipv4 : current_reverse
            })
            # note, is a set, return only the first element
            return reversed_set[0]
        except Exception as xxx:
            current_reverse['error'] = xxx
            current_reverse['retry'] += 1.3
            DNS.ip_reversed.update({
                ipv4 : current_reverse
            })
            return None


    # TODO CND check


class Traceroute:

    SLOW_TIMEOUT = "2.6"
    FAST_TIMEOUT = "1.6"
    SLOW_PROBES = "5"
    FAST_PROBES = "2"
    HOP_COUNT = "20"

    def __init__(self, OUTPUTDIR, ip_addr, hostlist, geoif, shitty):

        self._odir = os.path.join(OUTPUTDIR, '_traceroutes')
        self._vdir = os.path.join(OUTPUTDIR, '_verbotracelogs')

        self.v4_target = ip_addr
        self.hostlist = hostlist

        self.ipv4_trace_file =  os.path.join(self._odir, "%s_ip.json" % self.v4_target)
        self.cc_trace_file = os.path.join(self._odir, "%s_countries.json" % self.v4_target)

        self.ips_links = []
        self.countries_links = []

        self.geoif = geoif
        self.shitty_internet = shitty

        for _host in self.hostlist:
            self.ips_links.append(os.path.join(self._odir, "%s_ip.json" % _host))
            self.countries_links.append(os.path.join(self._odir, "%s_countries.json" % _host))


    def already_traced(self):

        if os.path.isfile(self.ipv4_trace_file) and os.path.isfile(self.cc_trace_file):
            return True
        else:
            return False

    def resolve_target_geoip(self):

        # sometime here you find multicast or shit
        dest_country = self.geoif.country_name_by_addr(self.v4_target)
        dest_code = self.geoif.country_code_by_addr(self.v4_target)
        self.destination_geoinfo = [ dest_country, dest_code ]


    def file_dump(self):

        with file(self.ipv4_trace_file, 'w+') as f:
            json.dump(self.iplist, f)

        with file(self.cc_trace_file, 'w+') as f:
            aggregate_country_info = [
                self.country_travel_path,
                self.destination_geoinfo
            ]
            json.dump(aggregate_country_info, f)

        for ip_link in self.ips_links:
            # dest has the path, souece has not
            os.symlink("%s_ip.json" % self.v4_target, ip_link)

        for cc_link in self.countries_links:
            # ipv4_traced_hop_f, named_link_addr_f )
            os.symlink("%s_countries.json" % self.v4_target, cc_link)


    def do_trace(self):
        """
        Return True of False if the trace has gone successful or not
        """
        print colored("%s ⏎ " % self.hostlist, "yellow")
        self._software_execution()

        if not self.validate_traceroute_output():
            return False

        # resolve Geo info for all the IP involved
        self.country_travel_path = {}
        counter = 0
        print "\t", len(self.iplist), "HOP through",
        for ip in self.iplist:

            # if is an "* * * * *" I'll record as None and here is stripped
            if not ip:
                continue

            # is always as list ['x.x.x.x'] sometime more than 1
            if isinstance(ip, list):
                ip = ip[0]

            code = self.geoif.country_code_by_addr(ip)
            if not code:
                print colored(code, "red"),
            else:
                print colored(code, "green"),

            country = self.geoif.country_name_by_addr(ip)
            self.country_travel_path.update({counter:country})
            counter += 1

        print ""
        # These statistic can help future optimization!
        TraceStats(self.iplist)
        return True


    def _software_execution(self):

        # these two are the "return value"
        self.iplist = []
        self.asterisks_total = 0

        if self.shitty_internet:
            p = Popen(['traceroute', '-n', '-m', Traceroute.HOP_COUNT, '-w',
                       Traceroute.SLOW_TIMEOUT,
                       '-q', Traceroute.SLOW_PROBES, '-A', self.v4_target], stdout=PIPE)
        else:
            p = Popen(['traceroute', '-n', '-m', Traceroute.HOP_COUNT, '-w',
                       Traceroute.FAST_TIMEOUT,
                       '-q', Traceroute.FAST_PROBES, '-A', self.v4_target], stdout=PIPE)

        traceoutf = os.path.join(self._vdir, self.v4_target)
        if os.path.isfile(traceoutf):
            os.unlink(traceoutf)

        logfile = file(traceoutf, "w+")

        while True:
            line = p.stdout.readline()
            if not line:
                break
            logfile.write(line)

            # this prevent the IP match show below
            if line.startswith('traceroute to'):
                continue
            # traceroute to casellante.winstonsmith.org (109.168.101.146), 30 hops ...
            # 1  172.16.1.1 (172.16.1.1)  2.870 ms  2.868 ms  3.762 ms
            # 2  * * *

            asterisks = line.count("*")
            # not yet handled if traceroute cripple
            self.asterisks_total += asterisks

            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
            if not ip:
                self.iplist.append(None)
                continue
            self.iplist.append(ip)

        logfile.close()


    def validate_traceroute_output(self):

        complete_failure = int(Traceroute.HOP_COUNT)

        if self.iplist.count(None) == complete_failure:
            TraceStats.three_hundred_sadness()
            return False

        return True




#------------------------------------------------
# Here start TrackMap supporter script
#------------------------------------------------
def main():

    parser = OptionParser()

    parser.add_option("-c", "--country-name", type="string",
                      help="the country from which you want run the test", dest="medialist")
    parser.add_option("-o", "--output-dir", type="string", default=None,
                      help="directory to store results", dest="user_outputdir")
    parser.add_option("-l", "--local-phantom", action="store_true",
                      help="use local phantomjs instead of the downloaded one", dest="lp")
    parser.add_option("-d", "--disable-sending", action="store_true",
                      help="disable the result sending at the end of the test", dest="disable_send")
    parser.add_option("-i", "--instable-internet", action="store_true",
                      help="If your internet is instable, please enable this option", dest="shitty_internet")
    parser.add_option("-s", "--send", type="string", dest="targz_output",
                      help="do not perform test, submit a previously collected result.")
    parser.add_option("-v", "--version", action="store_true", dest="version",
                      help="print version, spoiler: %d" % ANALYSIS_VERSION)

    (args, _) = parser.parse_args()

    if args.version:
        print "analysis format version:", ANALYSIS_VERSION
        quit(0)

    if args.targz_output:
        if args.disable_send:
            print colored("You can't use -s (--send) and -d (--disable-sending) options together")
            quit(-1)

        if not os.path.isfile(args.targz_output):
            print colored("Invalid file: %s" % args.targz_output)
            quit(-1)

        print colored(" ࿓  Sending previous results...", 'blue', 'on_white', attrs=['underline'])
        send_results(args.targz_output, hiddenservice_tuple)
        quit(0)

    if not args.medialist:
        print colored("Usage: %s -c $YOUR_COUNTRY_NAME" % sys.argv[0], "red", 'on_white')
        print colored("\t-l (local phantom, instead of the symlink here)", "red", 'on_white')
        print colored("\t-o output directory, used to collect test results", "red", 'on_white')
        print ""
        print " -l option is needed if you want use your own /usr/bin/phantomjs"
        print " (if you follow README.md, this is not needed because you downloaded phantomjs 1.9.2)"
        print " ",colored("By default, this software is looking for symlink 'phantom-1.9.2'", "green", "on_white")
        if os.path.islink('phantom-1.9.2'):
            print " ",colored("phantom-1.9.2 is a link, as expected.", "green", "on_white")
        else:
            print " ",colored("The phantom-1.9.2 link is missing!", "red", "on_white")
        print "Look in the verified_media/ for a list of countries."
        print "TrackMap collection tool version: %d" % ANALYSIS_VERSION
        quit(-1)

    # check if the user is running phantom as installed on the system (also vagrant make this)
    # of if is using
    if args.lp:
        local_phantomjs = True

        print colored("You're using your local installed phantomjs. A version >= than 1.9.0 is needed.", 'blue', 'on_white')
        print colored("I'm not going to compare the string. Be aware: this is your version:", 'red')

        phantom_version = Popen(['phantomjs', '-v'], stdout=PIPE).stdout.readline()
        print colored(phantom_version, 'blue', 'on_white')
    else:
        if not os.path.islink('phantom-1.9.2'):
            print colored("Missing phantom-1.9.2. A symbolic link named phantom-1.9.2 was expected, but not found. Please consult README.md and make sure you've followed the installation procedure exactly.", 'red', 'on_white')
            quit(-1)

        local_phantomjs = False

    if not args.disable_send:
        tor_test = ("127.0.0.1", 9050)
        c = socket.socket()
        try:
            c.connect( tor_test )
            c.close()
        except Exception as xxx:
            print colored("Unable to connect to %s, Tor is needed to send results" % str(tor_test), "red")
            print colored(xxx, "red")
            print colored("You can disable result sending with the option -d", "yellow")
            quit(-1)
        del c

    # country check
    proposed_country = args.medialist
    country_f = os.path.join('verified_media', proposed_country.lower())
    if not os.path.isfile(country_f):
        print colored("Invalid country! not found %s in directory 'verified_media/' " % proposed_country, 'red')
        print "Available countries are:"
        for existing_c in os.listdir('verified_media'):
            if existing_c in ['README.md', 'test']:
                continue
            print "\t", existing_c
        print colored("You can propose your own country media list following these instructions:", 'blue', 'on_white')
        print colored("https://github.com/vecna/helpagainsttrack/blob/master/unverified_media_list/README.md", 'blue', 'on_white')
        quit(-1)

    # check if the output directory is not the default and/or if need to be created
    if args.user_outputdir:
        OUTPUTDIR = args.user_outputdir
    else:
        OUTPUTDIR = 'output/'

    if not os.path.isdir(OUTPUTDIR):
        try:
            os.mkdir(OUTPUTDIR)
        except OSError as error:
            print "unable to create %s: %s" % (OUTPUTDIR, error)


    # ask free information to the script runner
    info_f = os.path.join(OUTPUTDIR, 'information')
    if os.path.isfile(info_f):
        f = open(info_f, 'r')
        information = json.load(f)
        f.close()
        print colored("Recovered information of previous collection:", 'green')
        print " name:", information['name']
        print " contact:", information['contact']
        print " ISP:", information['ISP']
        print " city:", information['city']
    else:
        information = {}
        print colored("Optionally, provide the information requested below, or press Enter to skip:", 'green')

        def question(description):
            print colored(description, 'white', 'on_blue')
            answer = sys.stdin.readline()
            answer = answer.strip('\n')
            return None if not len(answer) else answer

        information['name'] = question('Your name:')
        information['contact'] = question('Mail or jabber contact:')
        information['ISP'] = question('Which ISP is providing your link:')
        information['city'] = question('From which city you\'re running this script:')
        information['version'] = ANALYSIS_VERSION

        with file(info_f, 'w+') as f:
            json.dump(information, f)


    # writing in a file which country you're using!
    with file(os.path.join(OUTPUTDIR, 'country'), 'w+') as f:
        f.write(proposed_country.lower())

    # reading media list, cleaning media list and copy media list
    cfp = file(country_f, 'r')
    unclean_lines = cfp.readlines()

    with file(os.path.join(OUTPUTDIR, 'used_media_list'), 'w+') as f:
        f.writelines(unclean_lines)

    # reconding an unique number is always useful, also if I've not yet in mind an usage right now.
    with file( os.path.join(OUTPUTDIR, "unique_id"), "w+") as f:
        f.write("%d%d%d" % (random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff)) )

    print colored(" ࿓  Importing media list:", 'blue', 'on_white', attrs=['underline'])
    media_entries = media_file_cleanings(unclean_lines)
    cfp.close()

    print colored(" ࿓  Checking your network source.", 'blue', 'on_white', attrs=['underline'])
    do_wget( os.path.join(OUTPUTDIR, 'first.json'))

    print colored(" ࿓  Starting media crawling:", 'blue', 'on_white', attrs=['underline'])
    # here start iteration over the media!
    phantom_stats = {}
    for cleanurl, media_kind in media_entries.iteritems():

        urldir = os.path.join(OUTPUTDIR, cleanurl)
        title_check = os.path.join(urldir, '__title')

        if os.path.isdir(urldir) and os.path.isfile(title_check):
            print "-", urldir, "already present: skipped"
            phantom_stats.setdefault('resumed', []).append(cleanurl)
            continue

        if os.path.isdir(urldir):
            # being here means that is empty or incomplete
            shutil.rmtree(urldir)

        print "+ Creating directory", urldir
        os.mkdir(urldir)

        retinfo = do_phantomjs(local_phantomjs, cleanurl, urldir, media_kind, OUTPUTDIR)
        assert retinfo in [ 'first', 'second', 'failures' ]
        phantom_stats.setdefault(retinfo, []).append(cleanurl)

    # take every directory in 'output/', get the included URL and dump in a dict
    included_url_dict = sortify(OUTPUTDIR)
    assert included_url_dict, "No url included after phantom scraping and collection !?"
    with file(os.path.join(OUTPUTDIR, 'domain.infos'), 'w+') as f:
        json.dump(included_url_dict, f)

    # generate DNS resolution map. for every host resolve an IP, for every IP resolve again DNS
    print colored(" ࿓  DNS resolution and reverse of %d domains..." % len(included_url_dict), 'blue', 'on_white', attrs=['underline'])

    # new format contain:
    # first dict: resolution error
    # second dict: reverse error
    dns_error = [{}, {}]

    # now, until there is not refactor based on classes,
    # the resolution of the previously failed DN will not happen
    resolution_dns_f = os.path.join(OUTPUTDIR, 'resolution.dns')
    if os.path.isfile(resolution_dns_f):
        fp = file(resolution_dns_f, 'r')
        ip_map = json.load(fp)
        fp.close()
    else:
        ip_map = {}
        counter = 0
        percentage_bound = len(included_url_dict.keys()) / 10.0

        if not int(percentage_bound):
            percentage_bound = 1.0

        for domain in included_url_dict.keys():
            counter += 1
            if not counter % int(percentage_bound):
                print "%d\t%d%%\t%s" % (counter, (counter * (10 / percentage_bound) ), time.ctime())
            # other random possibility based on birthday paradox to show counters...
            if random.randint(0, int(percentage_bound * 10 )) == counter:
                print "%d\t%d%%\t%s" % (counter, (counter * (10 / percentage_bound) ), time.ctime())

            try:

                if args.shitty_internet:
                    socket.setdefaulttimeout(1.1)
                else:
                    socket.setdefaulttimeout(0.5)

                resolved_v4 = socket.gethostbyname(domain)
            except Exception as xxx:
                dns_error[0].setdefault(xxx.strerror, []).append(domain)
                continue

            ip_map.setdefault(resolved_v4, []).append(domain)

            with file(resolution_dns_f, 'w+') as f:
                json.dump(ip_map, f)

    print colored("\nResolved %d unique IPv4 from %d unique domain" % (len(ip_map.keys()), len(included_url_dict.keys())), 'green')

    if not len(ip_map.keys()):
        print colored("It appears that you can't access the internet. Please fix that and restart the test.", 'red')
        quit(-1)

    print colored("\nReversing DNS for %d unique IP address..." % len(ip_map.keys() ), 'green')
    reverse_dns_f = os.path.join(OUTPUTDIR, 'reverse.dns')
    if os.path.isfile(reverse_dns_f):
        fp = file(reverse_dns_f, 'r')
        true_domain_map = json.load(fp)
        fp.close()
    else:
        true_domain_map = {}
        counter = 0
        percentage_bound = len(ip_map.keys()) / 10.0

        if not int(percentage_bound):
            percentage_bound = 1.0

        for ipv4 in ip_map.keys():
            counter += 1

            if not (counter % int(percentage_bound) ):
                print "%d\t%d%%\t%s" % (counter, (counter * (10 / percentage_bound) ), time.ctime())
            # other random possibility based on birthday paradox to show counters...
            if random.randint(0, int(percentage_bound * 10 )) == counter:
                print "%d\t%d%%\t%s" % (counter, (counter * (10 / percentage_bound) ), time.ctime())

            try:

                if args.shitty_internet:
                    socket.setdefaulttimeout(1.9)
                else:
                    socket.setdefaulttimeout(0.9)

                resolved_set = socket.gethostbyaddr(ipv4)
                resolved_name = resolved_set[0]
            except Exception as xxx:
                dns_error[1].setdefault(xxx.strerror, []).append(ipv4)
                continue

            true_domain_map.setdefault(resolved_name, []).append(ipv4)

        with file(reverse_dns_f, 'w+') as f:
            json.dump(true_domain_map, f)

    print colored("\nReversed %d unique FQDN" % len(true_domain_map.keys() ), 'green')

    print colored("Saving DNS errors in 'errors.dns'")
    with file(os.path.join(OUTPUTDIR, 'errors.dns'), 'w+') as f:
        json.dump(dns_error, f)

    # traceroutes contains all the output of traceroute in JSON format, separated
    # for logs. this output is not in the media directory, because some host like
    # google are included multiple times.
    trace_output = os.path.join(OUTPUTDIR, '_traceroutes')
    if not os.path.isdir(trace_output):
        os.mkdir(trace_output)

    # _verbotracelogs instead contain the detailed log of traceroute,
    # they would be useful in the future because AS number is not yet used
    # as information in the backend, but, who knows...
    verbotracelogs = os.path.join(OUTPUTDIR, '_verbotracelogs')
    if not os.path.isdir(verbotracelogs):
        os.mkdir(verbotracelogs)

    # saving again information about network location
    do_wget( os.path.join(OUTPUTDIR, 'second.json') )

    # starting traceroute to all the collected IP
    print colored(" ࿓  Running traceroute to %d IP address (from %d hosts)" % (
        len(ip_map.keys()), len(included_url_dict.keys())), 'blue', 'on_white', attrs=['underline'])

    counter = 1
    trace_stats = {}
    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    for ip_addr, hostlist in ip_map.iteritems():

        progress_string = "%d/%d" % (counter, len(ip_map.keys()))
        print colored("%s%s" % (progress_string, (10 - len(progress_string)) * " " ), "cyan" ),

        t = Traceroute(OUTPUTDIR, ip_addr, hostlist, gi, args.shitty_internet)

        counter += 1

        if t.already_traced():
            print colored ("%s already traced (%d hosts): skipping" % (ip_addr, len(hostlist) ), "green")
            retinfo = "recover"
        elif not t.do_trace():
            retinfo = "fail"
            print colored("Traceroute fails! (%d/10)" % TraceStats.three_hundres, "red")
        else:
            retinfo = "success"
            try:
                t.resolve_target_geoip()
                t.file_dump()
            except Exception:
                retinfo = "anomaly"

        del t
        assert retinfo in [ 'recover', 'success', 'anomaly', 'fail'  ]
        trace_stats.setdefault(retinfo, []).append(ip_addr)

    # Traceroute class need to be enhanced with some kind of:
    #  *  failure measurement and GUESSING WHY
    #  *  retry after a while
    #  *  estimation of shared path - optimization and stabler collection
    if trace_stats.has_key('fail') and len(trace_stats['fail']):
        print colored(" ࿓  Testing again the failed traceroute to %d IP address" %
                len(trace_stats['fail']))
    else:
        # just here to skip a KeyError below
        trace_stats.update({'fail': []})

    counter = 1
    fail_list_copy = list(trace_stats['fail'])
    # a list is done because inside of the loop is changed the
    # content of trace_stats['fail']
    for case_n, failed_trace in enumerate(fail_list_copy):

        hostlist = ip_map[failed_trace]
        t = Traceroute(OUTPUTDIR, failed_trace, hostlist, gi, args.shitty_internet)
        counter += 1
        if not t.do_trace():
            print colored("Failure again.", "red")
            retinfo = "fail"
        else:
            retinfo = "retry"
            trace_stats['fail'].remove(failed_trace)
            try:
                t.resolve_target_geoip()
                t.file_dump()
            except Exception:
                retinfo = "anomaly"

        del t
        assert retinfo in [ 'recover', 'success', 'anomaly', 'fail', 'retry' ]
        trace_stats.setdefault(retinfo, []).append(failed_trace)


    TraceStats([]).dump_stats(OUTPUTDIR)

    if trace_stats.values().count(False):
        print colored("Registered %d failures" % trace_stats.values().count(False), "red")

    ptsj = os.path.join(OUTPUTDIR, '_phantom.trace.stats.json')
    if os.path.isfile(ptsj):
        os.unlink(ptsj)
    with file(ptsj, 'w+') as fp:
        json.dump([ phantom_stats, trace_stats ], fp)

    # saving again*again information about network location
    do_wget(os.path.join(OUTPUTDIR, 'third.json'))

    output_name = 'results-%s.tar.gz' % proposed_country.lower()
    print colored(" ࿓  Analysis done! compressing the output in %s" % output_name, "blue", 'on_white', attrs=['underline'])

    if os.path.isfile(output_name):
        os.unlink(output_name)

    tar = Popen(['tar', '-z', '-c', '-v', '-f', output_name, OUTPUTDIR], stdout=PIPE)

    counter_line = 0
    while True:
        line = tar.stdout.readline()
        counter_line += 1
        if not line:
            break

    if args.disable_send:
        print colored("%d file added to %s" % (counter_line, output_name), "green")
        print colored("Sending disable, test complete.", "yellow"),
        print colored("亷 亸", 'blue', 'on_white')
        quit(0)

    print colored("%d file added to %s, Starting to submit results via Tor network\n" % (counter_line, output_name), "green")
    print colored("If submitting results fails please run:", "red")
    print colored("./perform_analysis.py -s %s" % output_name, "yellow")
    send_results(output_name, hiddenservice_tuple)


def send_results(targz, connect_tuple):

    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    s = socks.socksocket()
    s.connect(connect_tuple)

    try:
        if not targz.endswith('.tar.gz'):
            raise Exception("Not .tar.gz suffix found")
        if len(targz) > 28:
            raise Exception("Expected not more than 28 byte here")
        if targz.find('/') != -1:
            raise Exception("put a shah not a slash")
        if targz.find('%') != -1:
            raise Exception("Encoding is the root of evil")
        if targz.find('\\') != -1:
            raise Exception("Other kind of encoding")
    except Exception as info:
        print info
        quit(-1)

    total_sent = 0

    statinfo = os.stat(targz)

    with open(targz, 'rb') as fp:

        while True:

            data = fp.read(1024)
            if not data:
                break

            total_sent += s.send(data)

            if random.randint(1, 200) == 13:
                print colored("%f%%\t%s\t%d\tof %d bytes sent" % (
                    ( 100 * (float(total_sent) / statinfo.st_size)), time.ctime(),
                    total_sent, statinfo.st_size
                ), 'yellow')

        s.close()

    if total_sent == statinfo.st_size:
        print colored("\n\tData collected has been sent, Thank You! :)\n", 'green')
        quit(0)
    else:
        print colored("\n\tLink broken! please, run the ./perform_analysis.py script:\n", 'red')
        print colored("\twith the option '-s %s'" % targz, 'red')
        quit(-1)



#!/usr/bin/python
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

    x = AnalysisLogic('verified_media/test', None)
    x.do_analysis()

    quit()

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

