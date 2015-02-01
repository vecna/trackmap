#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# This software is constantly updated in
# https://github.com/vecna/trackmap
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
    import fcntl
    import requests
    import time
    import shutil
    import socket
    import threading
    import subprocess
    from optparse import OptionParser
    from termcolor import colored
    from manyutils import sortify, media_file_cleanings
    from datetime import datetime
except ImportError as det:
    print "TrackMap collection system is not correctly installed", det
    print "Follow the README below or mail to trackmap<@>tacticaltech.org"
    print "https://github.com/vecna/trackmap"
    quit(-1)


hiddenservice_tuple = ('mzvbyzovjazwzch6.onion', 80)
server_tuple = ('213.108.108.94', 32001)

ANALYSIS_VERSION = 6
A_RANDOM_NUMBER = random.randint(1, 0xfffff)

class TraceStats:

    failures = 0

    @staticmethod
    def three_hundred_sadness():
        """
        This function is called every time enough "*" are spot in
        a traceroute output, this should mean a complete
        ICMP filtered network. when happen tenth time, quit the sw.

        is called three_hundred_sadness because by default, 30 hop,
        10 probes, makes 300 "*" :)
        """
        TraceStats.failures += 1

        if TraceStats.failures >= 10:
            print "\n\n"
            print colored("\tHas been detected ten time a complete Traceroute failure", "red")
            print colored("\tMaybe the network is down, maybe your host is filtering ICMP", "red")
            print colored("\tIn both cases, the test is interrupted.", "red")
            print "\n"
            print colored("\tIf the test has reach more than 10 traceroute, then:", "red")
            print colored("\tAdd the option -i to perform a slow and sure test", "red")
            print "\n\n"
            quit(-1)


def get_client_info(pathdest):

    client_ip = requests.get('http://json.whatisyourip.org/')

    with file(pathdest, 'w+') as fp:
        json.dump(client_ip.json(), fp)



def get_local_phantom_v():
    return subprocess.Popen(['phantomjs', '-v'],
                            stdout=subprocess.PIPE).stdout.readline()

def I_want_thread_to_zero(max_sec):

    max_seconds_await = max_sec
    while threading.active_count():
        time.sleep(1)
        max_seconds_await -= 1
        if not max_seconds_await:
            print colored("Some thread (%d) still alive, amen!" % threading.active_count())
            break


class PhantomCrawl(threading.Thread):

    status = {}
    media_amount = 0
    media_done = 0
    media_running = 0
    status_file = None

    @classmethod
    def load_status_disk(cls):
        if not os.path.isfile(PhantomCrawl.status_file):
            return

        with file(PhantomCrawl.status_file, 'r') as fp:
            print "Loading previous Phantom backlog..",
            PhantomCrawl.status = json.load(fp)
            print len(PhantomCrawl.status.keys()), "Loaded!"


    def __init__(self, lp, url, urldir, media_kind, id, OUTPUTDIR):
        self.lp = lp
        self.url = url
        self.urldir = urldir
        self.media_kind = media_kind
        self.outputdir = OUTPUTDIR
        self.id = id

        threading.Thread.__init__(self)

        load_avg, _, __ = os.getloadavg()
        time.sleep(2.5)

        if load_avg > 3:
            print colored(
                    "Load average peek reach (%f) with %d thread, slow down" % 
                    (load_avg, threading.active_count() ), 'red' )
            time.sleep(50)

    def run(self):

        PhantomCrawl.media_running += 1
        PhantomCrawl.status.update({
            self.id: {
                'start' : str(datetime.now()),
                'from' : self.media_kind,
                'end' : None,
                'status' : None,
            }
        })

        retinfo = do_phantomjs(self.lp, self.url, self.urldir, self.media_kind)

        PhantomCrawl.status[self.id]['end'] = str(datetime.now())
        PhantomCrawl.status[self.id]['status'] = retinfo
        PhantomCrawl.media_done += 1
        PhantomCrawl.media_running -= 1

        PhantomCrawl.sync_status_disk()
        return retinfo

    @classmethod
    def sync_status_disk(cls, mandatory=False):
        try:
            with file(PhantomCrawl.status_file, 'w+') as fp:
                json.dump(PhantomCrawl.status, fp)
        except RuntimeError:
            if not mandatory:
                return

            time.sleep(0.1)
            print colored("Mandatory sync required: <recursion>", 'red', 'on_yellow')
            PhantomCrawl.sync_status_disk(mandatory)


class DNSresolve(threading.Thread):
    """
    sloppy redundancy at the moment, better class design at the next refactor
    """

    status = {}
    errors = {}
    ip_map = {}

    host_amount = 0
    host_done = 0
    status_file = None
    resolution_file = None
    errors_file = None
    resolve_errors = 0

    _percentage_bound = 0
    def percentage_fancy(self):

        if not DNSresolve._percentage_bound:
            DNSresolve._percentage_bound = DNSresolve.host_amount / 10.0
            if not int(DNSresolve._percentage_bound):
                DNSresolve._percentage_bound = 1.0

        if not DNSresolve.host_done:
            return

        sync_on_disk = False
        if not DNSresolve.host_done % int(DNSresolve._percentage_bound):
            print "%d\t%d%%\t%s\tT%d" % (DNSresolve.host_done,
                                    (DNSresolve.host_done * (10 / DNSresolve._percentage_bound) ),
                                    time.ctime(), threading.active_count())
            sync_on_disk = True

        # other random possibility based on birthday paradox to show counters...
        if random.randint(0, int(DNSresolve._percentage_bound * 10 )) == DNSresolve.host_done:
            print "%d\t%d%%\t%s\tT%d" % (DNSresolve.host_done,
                                    (DNSresolve.host_done * (10 / DNSresolve._percentage_bound) ),
                                    time.ctime(), threading.active_count())
            sync_on_disk = True


        if sync_on_disk:
            DNSresolve.save_status(mandatory=False)

    @classmethod
    def load_status_disk(cls):
        if not os.path.isfile(DNSresolve.status_file):
            return

        with file(DNSresolve.status_file, 'r') as fp:
            print "Loading previous DNSresolve backlog..",
            DNSresolve.status = json.load(fp)
            print len(DNSresolve.status.keys()), "Loaded!"

        with file(DNSresolve.resolution_file, 'r') as fp:
            print "Loading IP map too..",
            DNSresolve.ip_map = json.load(fp)
            print len(DNSresolve.ip_map.keys()), "Loaded!"


    def __init__(self, host, shitty_internet):

        threading.Thread.__init__(self)

        load_avg, _, __ = os.getloadavg()

        # 20% of the time put a delay of 0.3
        if random.randint(0, 10) < 2:
            time.sleep(0.3)

        self.host = host
        self.timeout = 4.0 if shitty_internet else 2.0

        if load_avg > 3:
            time.sleep(10)

    def run(self):

        DNSresolve.status.update({
            self.host : None
        })
        try:
            socket.setdefaulttimeout(self.timeout)

            resolved_v4 = socket.gethostbyname(self.host)
            DNSresolve.ip_map.setdefault(resolved_v4, []).append(self.host)
            DNSresolve.status[self.host] = resolved_v4
        except Exception as xxx:
            DNSresolve.resolve_errors += 1
            DNSresolve.errors.update({ self.host : xxx.strerror })

        DNSresolve.host_done += 1
        self.percentage_fancy()

    @classmethod
    def save_status(cls, mandatory=False):

        if mandatory:
            with file(DNSresolve.errors_file, 'w+') as fp:
                json.dump(DNSresolve.errors, fp)

        try:
            with file(DNSresolve.status_file, 'w+') as fp:
                json.dump(DNSresolve.status, fp)
            with file(DNSresolve.resolution_file, 'w+') as fp:
                json.dump(DNSresolve.ip_map, fp)

        except RuntimeError:
            if mandatory:
                time.sleep(0.1)
                print colored("Mandatory sync required: <recursion>", 'red', 'on_yellow')
                DNSresolve.save_status(mandatory)



class DNSreverse(threading.Thread):
    """
    sloppy redundancy at the moment, better class design at the next refactor,
    the shit below has at leat 115% in common with the class above.
    """
    status = {}
    errors = {}
    fqdn_map = {}

    ip_amount = 0
    ip_done = 0
    status_file = None
    reverse_file = None
    errors_file = None
    reverse_errors = 0

    _percentage_bound = 0
    def percentage_fancy(self):

        if not DNSreverse._percentage_bound:
            DNSreverse._percentage_bound = DNSreverse.ip_amount / 10.0
            if not int(DNSreverse._percentage_bound):
                DNSreverse._percentage_bound = 1.0

        if not DNSreverse.ip_done:
            return

        sync_on_disk = False
        if not DNSreverse.ip_done % int(DNSreverse._percentage_bound):
            print "%d\t%d%%\t%s\tT%d" % (DNSreverse.ip_done,
                                    (DNSreverse.ip_done * (10 / DNSreverse._percentage_bound) ),
                                    time.ctime(), threading.active_count())
            sync_on_disk = True

        # other random possibility based on birthday paradox to show counters...
        if random.randint(0, int(DNSreverse._percentage_bound * 10 )) == DNSreverse.ip_done:
            print "%d\t%d%%\t%s\tT%d" % (DNSreverse.ip_done,
                                    (DNSreverse.ip_done * (10 / DNSreverse._percentage_bound) ),
                                    time.ctime(), threading.active_count())
            sync_on_disk = True

        if sync_on_disk:
            DNSreverse.save_status(mandatory=False)

    @classmethod
    def load_status_disk(cls):

        if not os.path.isfile(DNSreverse.status_file):
            return

        with file(DNSreverse.status_file, 'r') as fp:
            print "Loading previous DNSreverse backlog..",
            DNSreverse.status = json.load(fp)
            print len(DNSreverse.status.keys()), "Loaded!"

        with file(DNSreverse.reverse_file, 'r') as fp:
            print "Loading FQDN map too..",
            DNSreverse.fqdn_map = json.load(fp)
            print len(DNSreverse.fqdn_map.keys()), "Loaded!"


    def __init__(self, ip, shitty_internet):

        threading.Thread.__init__(self)

        load_avg, _, __ = os.getloadavg()

        # 20% of the time put a delay of 0.3
        if random.randint(0, 10) < 2:
            time.sleep(0.3)

        self.ip = ip
        self.timeout = 5.0 if shitty_internet else 3.0

        if load_avg > 3:
            time.sleep(10)

    def run(self):

        DNSreverse.status.update({
            self.ip: None
        })
        try:
            socket.setdefaulttimeout(self.timeout)

            resolved_set = socket.gethostbyaddr(self.ip)
            resolved_name = resolved_set[0]
            DNSreverse.fqdn_map.setdefault(resolved_name, []).append(self.ip)
            DNSreverse.status[self.ip] = resolved_name
        except Exception as xxx:
            DNSreverse.reverse_errors += 1
            DNSreverse.errors.update({ self.ip : xxx.strerror })

        DNSreverse.ip_done += 1
        self.percentage_fancy()

    @classmethod
    def save_status(cls, mandatory=False):

        if mandatory:
            with file(DNSreverse.errors_file, 'w+') as fp:
                json.dump(DNSreverse.errors, fp)

        try:
            with file(DNSreverse.status_file, 'w+') as fp:
                json.dump(DNSreverse.status, fp)
            with file(DNSreverse.reverse_file, 'w+') as fp:
                json.dump(DNSreverse.fqdn_map, fp)

        except RuntimeError:
            if mandatory:
                time.sleep(0.1)
                print colored("Mandatory sync required: <recursion>", 'red', 'on_yellow')
                DNSreverse.save_status(mandatory)



def do_phantomjs(local_phantomjs, url, destfile, media_kind):
    # information that deserve to be saved for the time
    kindfile = os.path.join(destfile, '__kind')
    with file(kindfile, 'w+') as f:
        f.write(media_kind + "\n")

    def software_execution():
        binary = 'phantomjs' if local_phantomjs else './phantom-1.9.8'

        p = subprocess.Popen(['nohup', binary,
                   '--local-storage-path=%s/localstorage' % destfile,
                   '--cookies-file=%s/cookies' % destfile,
                   'collect_included_url.js',
                   '%s' % url, destfile ],
                             env={'HOME': destfile },
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        # read and waste this ONLY line to stdout:
        # "nohup: ignoring input and appending output to ‘nohup.out’"
        p.stdout.readline()

        print colored("+ %03d..%03d/%03d\tExecuting %s on: %s (%s)" %
                ( PhantomCrawl.media_running,
                  PhantomCrawl.media_done,
                  PhantomCrawl.media_amount,
                  binary, url,
                  media_kind), "green")

        # wait up to 90 seconds, and then kill the process if is not done
        wtime = 0
        while wtime<90 and p.returncode == None:
            p.poll();
            time.sleep(1)
            wtime += 1

        # why 90 ? boh. empiric trade-off. other timeout define in phantom is 29 sec
        # it those 90 seconds are not enough to load all the resource, you get killed
        # below, and then you have a second change anyway.

        if p.returncode == None:
            try:
                p.terminate()
            except OSError:
                pass

        try:
            urlfile = os.path.join(destfile, '__urls')
            urlfp = file(urlfile, 'r')
            included_urls = urlfp.readlines()
            urlfp.close()
        except Exception as xxx:
            print colored("%s %s" % (destfile, xxx), 'white', 'on_red')
            return 0

        return len(included_urls)

    # -------------------------------------------------------------------
    # -- Here starts the do_phantom logic + software exec + results check
    first_test = software_execution()
    if not first_test or first_test < 3:

        print colored("Total or partial failure with %s = retry" % url, "magenta")
        time.sleep(5)
        second_test = software_execution()

        # the URL are in append, therefore, second test has always at least 2
        if not second_test or second_test < 3:
            print colored("Failed again! %s :(" % url, "red")
            return 'failures'

        if second_test > first_test:
            print colored("Retry 2nd time has worked (%d > %d)" % (second_test, first_test), 'magenta'),
            print colored("done %s" % url, "yellow")
            return 'second'

        print colored("Other kind of failure F%d S%d (can this happen ?" % (first_test, second_test), 'red')
        return 'failures'

    else:
        print colored("%s => Fetch %d URLs (%s)" % (url, first_test, media_kind), "yellow")
        return 'first'


class Multitrace(threading.Thread):

    amount = 0
    done = 0

    def __init__(self, OUTPUTDIR, ip_addr, hostlist, shitty):

        threading.Thread.__init__(self)

        load_avg, _, __ = os.getloadavg()

        if load_avg > 3:
            print colored("Load AVG %f, delay now." % load_avg, 'red')
            time.sleep(50)

        time.sleep(1)

        Multitrace.done += 1
        self.personal_id = Multitrace.done

        print colored("%02d   %04d/%04d %s ⏎ " % (
            threading.active_count(), self.personal_id, Multitrace.amount,
            hostlist), "yellow")

        self.ip_addr = ip_addr
        self.outputdir = OUTPUTDIR
        self.hostlist = hostlist
        self.shitty = shitty

    def run(self):

        t = Traceroute(self.outputdir, self.ip_addr, self.hostlist, self.shitty)
        check = t.do_trace()

        if check:
            print colored("%02d > %04d/%04d %s" %
                          (threading.active_count(), 
                            self.personal_id, Multitrace.amount,
                              self.ip_addr), 'green'),
        else:
            print colored("%02d ! %04d/%04d %s" %
                          (threading.active_count(),
                            self.personal_id, Multitrace.amount,
                              self.ip_addr), 'red'),

        # in both cases, this contain additional info:
        print t.colored_output


class Traceroute:

    SLOW_TIMEOUT = "2.9"
    FAST_TIMEOUT = "1.9"
    SLOW_PROBES = "7"
    FAST_PROBES = "3"
    HOP_COUNT = "20"

    def __init__(self, OUTPUTDIR, ip_addr, hostlist, shitty):

        self.v4_target = ip_addr
        self.hostlist = hostlist

        self.shitty_internet = shitty

        self._vdir = os.path.join(OUTPUTDIR, '_verbotracelogs')
        self.traceoutf = os.path.join(self._vdir, self.v4_target)

    @classmethod
    def is_already_trace(cls, ip_addr, OUTPUTDIR):
        traceoutf = os.path.join(OUTPUTDIR, '_verbotracelogs', ip_addr)
        return os.path.isfile(traceoutf)

    def do_trace(self):
        """
        Return True of False if the trace has gone successful or not
        """
        self.iplist = []

        try:
            p = subprocess.Popen(['traceroute', '-n', '-m', Traceroute.HOP_COUNT, '-w',
                       Traceroute.SLOW_TIMEOUT, '-q', Traceroute.SLOW_PROBES,
                       '-A', self.v4_target], stdout=subprocess.PIPE)

            logfile = file(self.traceoutf, "w+")

            while True:
                line = p.stdout.readline()
                if not line:
                    break
                logfile.write(line)

                # this prevent the IP match show below
                if line.startswith('traceroute to'):
                    continue

                ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
                if not ip:
                    self.iplist.append(None)
                    continue
                self.iplist.append(ip)

            logfile.close()

            if p.poll():
                self.colored_output = colored("Return code [%s]" % str(p.poll()), 'white', 'on_red')
                return False

        except Exception as aaa:
            self.colored_output = colored("Traceroute exception %s" % aaa, 'white', 'on_red')
            return False

        self.colored_output = ""
        counter = 0
        none = 0
        for ip in self.iplist:

            # if is an "* * * * *" I'll record as None and here is stripped
            if not ip:
                none += 1
                self.colored_output = "%s %s" % (self.colored_output, colored(counter, 'red'))
                continue

            counter += 1
            self.colored_output = "%s %s" % (self.colored_output, colored(counter, 'green'))

        if none == Traceroute.HOP_COUNT:
            TraceStats.three_hundred_sadness()
            self.colored_output = colored("Only asterisk collected!?", 'white', 'on_red')
            return False

        return True

#------------------------------------------------
# Here start TrackMap supporter script
#------------------------------------------------
def main():

    parser = OptionParser()

    parser.add_option("-S", "--special", type="string",
                      help="use a special list for contexualized collections", dest="special")
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
    parser.add_option("-t", "--twitter-handle", type="string", dest="twit",
                      help="put your twitter handler, you'll be mentioned when test is imported.")
    parser.add_option("-v", "--version", action="store_true", dest="version",
                      help="print version, spoiler: %d" % ANALYSIS_VERSION)
    parser.add_option("-T", "--Tor", action="store_true", dest="hiddensubmit",
                      help="submit via hidden service (require Tor running)")
    parser.add_option("-k", "--keep", action="store_true", dest="keep",
                      help="don't remove the results-[country].tar.gz ")

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
        if args.hiddensubmit:
            quit(send_results(args.targz_output, hiddenservice_tuple, tor_proxy=True))
        else:
            quit(send_results(args.targz_output, server_tuple, tor_proxy=False))


    try:
        local_phantom_v = get_local_phantom_v()
    except Exception as xxx:
        print xxx
        local_phantom_v = None

    if not (args.medialist or args.special):
        print colored("Usage: %s -c $YOUR_COUNTRY_NAME" % sys.argv[0], "red", 'on_white')
        print parser.format_help()

        if os.path.islink('phantom-1.9.8'):
            print colored("found phantom-1.9.8 as link, good.", "green", "on_white")
        elif not local_phantom_v:
            print colored("phantomjs missing as link and missing in the system!", "red", "on_white")
            print colored("Please refer to the RADME or asks support to us", 'red', 'on_white')
            print colored("The script can't work in this status!", red)
        else:
            print colored("You have to use the option -l, and your installation is quite uncommon", red)
        print
        print "Look in the verified_media/ for a list of countries."
        print "TrackMap collection tool version: %d" % ANALYSIS_VERSION
        quit(-1)

    # check if the user is running phantom as installed on the system (also vagrant make this)
    # of if is using
    if args.lp and local_phantom_v:
        print colored("You're using your local installed phantomjs. A version >= than 1.9.0 is needed.", 'blue', 'on_white')
        print colored("I'm not going to compare the string. Be aware: this is your version:", 'red')
        print colored(local_phantom_v, 'blue', 'on_white')
        print "If is wrong, just press ^c and use the proper README instruction, or asks support to us"
    elif args.lp:
        print colored("phantomjs missing as link and missing in the system!", "red", "on_white")
        print colored("Please refer to the README or asks support to us", 'red', 'on_white')
        print colored("The script can't work in this status!", red)
        quit(-1)
    elif not os.path.islink('phantom-1.9.8'):
        print colored("Missing phantom-1.9.8. A symbolic link named phantom-1.9.8 was expected, but not found. Please consult README.md and make sure you've followed the installation procedure exactly.", 'red', 'on_white')
        quit(-1)


    if args.hiddensubmit:
        try:
            import socks
        except ImportError:
            print "You are missing 'PySocks' module, needed to proxy over Tor"

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

    def verify_media_country(the_user_input, special):
        # this function left the media file open forever. :(
        if special:
            special_f = os.path.join('special_media', the_user_input)
            if not os.path.isfile(special_f):
                print colored("Invaild special URL source, check in special_media ", 'red')
                quit(-1)

            cfp = file(special_f, 'r')
            unclean_lines = cfp.readlines()

            print colored(" ࿓  Importing special media list:", 'blue', 'on_white', attrs=['underline'])
            media_entries = media_file_cleanings(unclean_lines, permit_flexible_category=True)
            cfp.close()

            return special_f, media_entries

        # if not special, is media list
        country_f = os.path.join('verified_media', the_user_input.lower())
        if not os.path.isfile(country_f):
            print colored("Invalid country! not found %s in directory 'verified_media/' " % proposed_country, 'red')
            print "Available countries are:"
            for existing_c in os.listdir('verified_media'):
                if existing_c in ['README.md', 'test']:
                    continue
                print "\t", existing_c
            print colored("You can propose your own country media list following these instructions:", 'blue', 'on_white')
            print colored("https://github.com/vecna/trackmap/blob/master/unverified_media_list/README.md", 'blue', 'on_white')
            quit(-1)

        cfp = file(country_f, 'r')
        # reading media list, cleaning media list and copy media list
        unclean_lines = cfp.readlines()

        print colored(" ࿓  Importing media list from %s:" % the_user_input.lower(), 'blue', 'on_white', attrs=['underline'])
        media_entries = media_file_cleanings(unclean_lines)
        cfp.close()

        return country_f, media_entries

    # country check
    if args.special:
        proposed_country, media_entries = verify_media_country(args.special, special=True)
    else:
        proposed_country, media_entries = verify_media_country(args.medialist, special=False)

    # add 'id' to the media_entries:
    for i, media_blob in enumerate(media_entries):
        media_entries[i]['id'] = i

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


    if args.twit is None:
        print colored("You can specify your Twitter handle with -t and get mentioned by @trackography_",
                      'blue', 'on_yellow' )

    # ask free information to the script runner
    info_f = os.path.join(OUTPUTDIR, 'information')
    information = {
        'contact' : args.twit,
        'version' : ANALYSIS_VERSION,
        'city' : None,
        'ISP' : None,
        'name' : None,
    }
    with file(info_f, 'w+') as f:
        json.dump(information, f)

    # writing in a file which country you've selected!
    with file(os.path.join(OUTPUTDIR, 'country'), 'w+') as f:
        f.write(proposed_country.lower())

    # reconding an unique number is always useful, also if I've not yet in mind an usage right now.
    with file( os.path.join(OUTPUTDIR, "unique_id"), "w+") as f:
        f.write("%d%d%d" % (random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff)) )

    with file(os.path.join(OUTPUTDIR, 'source_url_configured.json'), 'w+') as f:
        json.dump(media_entries, f)

    print colored(" ࿓  Checking your network source.", 'blue', 'on_white', attrs=['underline'])
    get_client_info(os.path.join(OUTPUTDIR, 'first.json'))

    # Init of class method/vars
    PhantomCrawl.media_amount = len(media_entries)
    PhantomCrawl.status_file = os.path.join(OUTPUTDIR, 'phantom.results.json')
    PhantomCrawl.load_status_disk()

    print colored(" ࿓  Starting media crawling (%d)" % 
            PhantomCrawl.media_amount, 
            'blue', 'on_white', attrs=['underline'])

    # here start iteration over the media!
    skipped = 0
    for media_blob in media_entries:

        if not media_blob['category']:
            print colored("%s is missing category ?" % media_blob['url'], 'red', 'on_white')
            continue

        if PhantomCrawl.status.has_key(media_blob['id']) and PhantomCrawl.status[i]['status']:
            skipped += 1
            PhantomCrawl.media_done += 1
            continue

        urldir = os.path.join(OUTPUTDIR, "%s_%d" %  (media_blob['site'], media_blob['id'] ) )

        if skipped:
            print colored("skipped %d media from interrupted test" % skipped, 'yellow')
            skipped = 0

        if os.path.isdir(urldir):
            # being here means that is empty or incomplete
            shutil.rmtree(urldir)

        os.mkdir(urldir)

        PhantomCrawl(args.lp, media_blob['url'], urldir,
                     media_blob['category'], media_blob['id'], OUTPUTDIR).start()
        # XXX I can think to a return value here ?


    previous_running_test = 0
    while PhantomCrawl.media_running:

        if previous_running_test == PhantomCrawl.media_running:

            I_want_thread_to_zero(70)

            print colored("Media completed %d over %d: phase complete!" %
                          (PhantomCrawl.media_amount, PhantomCrawl.media_done),
                          'magenta', 'on_yellow' )
            break

        previous_running_test = PhantomCrawl.media_running

        print colored("Running %d, completed %d (on %d): sleeping 25s." % \
              (PhantomCrawl.media_running, PhantomCrawl.media_done,
               PhantomCrawl.media_amount), 'green', 'on_white')
        time.sleep(25)


    # finally, enforce a complete sync in the disk. is probably already happen, but for safety:
    PhantomCrawl.sync_status_disk(mandatory=True)

    # take every directory in 'output/', get the included URL and dump in a dict
    included_url_dict = sortify(OUTPUTDIR)
    assert included_url_dict, "No url included after phantom scraping and collection !?"
    with file(os.path.join(OUTPUTDIR, 'domain.infos'), 'w+') as f:
        json.dump(included_url_dict, f)

    # RESOLUTION multi-thread HERE start
    DNSresolve.host_amount = len(included_url_dict.keys())
    DNSresolve.status_file = os.path.join(OUTPUTDIR, 'resolution.status.json')
    DNSresolve.resolution_file = os.path.join(OUTPUTDIR, 'resolution.dns')
    DNSresolve.errors_file = os.path.join(OUTPUTDIR, 'resolution.errors.json')
    DNSresolve.load_status_disk()

    # generate DNS resolution map. for every host resolve an IP, for every IP resolve again DNS
    print colored(" ࿓  DNS resolution of %d domains..." % len(included_url_dict.keys()),
                  'blue', 'on_white', attrs=['underline'])

    for domain in included_url_dict.keys():

        if DNSresolve.status.has_key(domain) and DNSresolve.status[domain]:
            DNSresolve.host_done += 1
            continue

        DNSresolve(domain, args.shitty_internet).start()

    I_want_thread_to_zero(8)

    print colored("\nResolved %d unique IPv4 from %d unique domain (Errors %d)" %
                  (len(DNSresolve.ip_map.keys()), len(included_url_dict.keys()),
                   DNSresolve.resolve_errors
                  ), 'green')
    DNSresolve.save_status(mandatory=True)

    if not len(DNSresolve.ip_map.keys()):
        print colored("It appears that you can't access the internet. Please fix that and restart the test.", 'red')
        quit(-1)


    ### -----------------------------------------------------`###
    ### Reversing multithread start HERE                      ###

    DNSreverse.ip_amount = len(DNSresolve.ip_map.keys())
    DNSreverse.status_file = os.path.join(OUTPUTDIR, 'reverse.status.json')
    DNSreverse.reverse_file = os.path.join(OUTPUTDIR, 'reverse.dns')
    DNSreverse.errors_file = os.path.join(OUTPUTDIR, 'reverse.errors.json')
    DNSreverse.load_status_disk()

    print colored(" ࿓  DNS reverse of %d domains..." % DNSreverse.ip_amount,
                  'blue', 'on_white', attrs=['underline'])

    for ip in DNSresolve.ip_map.keys():

        if DNSreverse.status.has_key(ip) and DNSreverse.status[ip]:
            DNSreverse.ip_done += 1
            continue

        DNSreverse(ip, args.shitty_internet).start()

    I_want_thread_to_zero(12)

    print colored("\nReversed %d unique FQDN from %d IPaddrs (Errors %d)" %
                  ( len(DNSreverse.fqdn_map.keys()), 
                    len(DNSresolve.ip_map.keys()), DNSreverse.reverse_errors),
                   'green')
    DNSreverse.save_status(mandatory=True)


    # ------------------------------------------------------------------------
    # traceroutes contains all the output of traceroute in JSON format, 
    # for logs. this output is not in the media directory, because some 
    # host (think to fbcdn or google) are included multiple times.
    # ------------------------------------------------------------------------
    verbotracelogs = os.path.join(OUTPUTDIR, '_verbotracelogs')
    if not os.path.isdir(verbotracelogs):
        os.mkdir(verbotracelogs)

    # saving again information about network location
    get_client_info(os.path.join(OUTPUTDIR, 'second.json'))

    # Traceroute is not yet multithread

    # starting traceroute to all the collected IP
    print colored(" ࿓  Running traceroute to %d IP address (from %d hosts)" % (
        len(DNSresolve.ip_map.keys()), len(included_url_dict.keys())), 'blue', 'on_white', attrs=['underline'])

    Multitrace.amount = len(DNSresolve.ip_map.keys())
    for ip_addr, hostlist in DNSresolve.ip_map.iteritems():

        assert ip_addr.count('.') == 3, "Invalid IPv4 format %s" % ip_addr

        if Traceroute.is_already_trace(ip_addr, OUTPUTDIR):
            Multitrace.done += 1
            continue

        Multitrace(OUTPUTDIR, ip_addr, hostlist, args.shitty_internet).start()

    I_want_thread_to_zero(80)

    ## ----------- END TRACEROUTE -------------

    # saving again*again information about network location
    get_client_info(os.path.join(OUTPUTDIR, 'third.json'))

    output_name = 'results-%s.tar.gz' % proposed_country.lower()
    print colored(" ࿓  Analysis done! compressing the output in %s" % output_name, "blue", 'on_white', attrs=['underline'])

    if os.path.isfile(output_name):
        os.unlink(output_name)

    tar = subprocess.Popen(['tar', '-z', '-c', '-v', '-f', output_name, OUTPUTDIR],
                           stdout=subprocess.PIPE)

    counter_line = 0
    while True:
        line = tar.stdout.readline()
        counter_line += 1
        if not line:
            break

    if args.disable_send:
        print colored("%d files added to %s" % (counter_line, output_name), "green")
        print colored("Sending disable, test complete.", "yellow"),
        print colored("亷 亸", 'blue', 'on_white')
        os.kill(os.getpid(), 15)
        quit(0)

    print colored("%d file added to %s, Starting to submit results" %
                  (counter_line, output_name), "green")

    if not args.keep:
        print "..removing of", OUTPUTDIR
        shutil.rmtree(OUTPUTDIR)

    print colored("If submitting results fails please run:", "red")
    print colored("./perform_analysis.py -s %s" % output_name, "yellow")

    if args.hiddensubmit:
        ret = send_results(output_name, hiddenservice_tuple, tor_proxy=True)
    else:
        ret = send_results(output_name, server_tuple, tor_proxy=False)
    print ""
    os.kill(os.getpid(), 15)



def send_results(targz, connect_tuple, tor_proxy=False):

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

    if tor_proxy:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        s = socks.socksocket()
        s.connect(connect_tuple)
    else:
        s = socket.socket()
        s.connect(connect_tuple)

    total_sent = 0

    statinfo = os.stat(targz)

    s.send("%.10d" % A_RANDOM_NUMBER)
    s.send("%.14d" % statinfo.st_size)

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
        print "Deleting ", targz, "in...",
        sys.stdout.flush()
        for x in xrange(4):
            time.sleep(1)
            print "%d" % (3 - x),
            sys.stdout.flush()
        os.unlink(targz)
        return 0
    else:
        # TODO probably also if fail once, if we're in the loop mode, have to continue ?
        # no: better that stop once a while :)
        print colored("\n\tLink broken! please, run the ./perform_analysis.py script:\n", 'red')
        print colored("\twith the option '-s %s'" % targz, 'red')
        return -1


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print ""
        print colored("Received ^c, the process will be killed. Test will be resumed if command restart", 'blue', 'on_white')
        print colored(" - Remove output directory - if you want start from screatch -.", 'green', 'on_white')
        print colored("Restarting the test from a different ISP will invalidate the test.", 'red', 'on_white')
        os.kill(os.getpid(), 15)

