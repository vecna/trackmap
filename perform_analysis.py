#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# This software is constantly updated in https://github.com/vecna/helpagainsttrack
# Is described and used on http://myshadow.org and has been developed by
# Claudio <vecna at globaleaks dot org> April-Sept 2014, initially for a personal
# research, and after with Tactical Technology Collective http://tacticaltech.org
#



try:
    import os, re, json, sys, random, time, shutil, socket
    import GeoIP
    from optparse import OptionParser
    from subprocess import Popen, PIPE
    from termcolor import colored
    from libtrackmap import sortify, media_file_cleanings
except ImportError:
    print "TrackMap collection system is not correctly installed"
    print "Please, follow the instruction or mail to trackmap at tacticaltech.org"
    print "https://github.com/vecna/helpagainsttrack"
    quit(-1)

ANALYSIS_VERSION = 4
# remind: error.dns is changed in the middle of version 4 because is still not yet used

class TraceStats:

    v4_paths = {}
    three_hundres = 0

    def __init__(self, v4_path=[]):

        assert isinstance(v4_path, list)
        for hopcount, ip in enumerate(v4_path):
            TraceStats.v4_paths.setdefault(hopcount, [ ip ]).append(ip)

    def dump_stats(self, OUTPUTDIR):

        analysis_test = os.path.join(OUTPUTDIR, '_verbotracelogs', 'TraceStats.json')
        with file(analysis_test, 'w+') as f:
            json.dump(TraceStats.v4_paths, f)

    @staticmethod
    def three_hundred_sadness():
        """
        This function is called every time a 20 "*" are returned by a Traceroute.
        Mean that network is down or ICMP are filtered.
        Is called three hunderd because before there was 10 probes for 30 hop
        """
        TraceStats.three_hundres += 1

        if TraceStats.three_hundres >= 10:
            print "\n\n"
            print colored("\tHas been detected ten time a complete Traceroute failure", "red")
            print colored("\tMaybe the network is down, maybe your host is filtering ICMP", "red")
            print colored("\tIn both cases, the test is interrupted.", "red")
            print "\n"
            print colored("\tIf the test has reach more than 10 traceroute, try to restart the command: it will resume", "red")
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


def do_phantomjs(local_phantomjs, url, destfile, media_kind, OUTPUTDIR):
    # information that deserve to be saved for the time
    kindfile = os.path.join(destfile, '__kind')
    with file(kindfile, 'w+') as f:
        f.write(media_kind + "\n")

    def software_execution():

        binary = 'phantomjs' if local_phantomjs else './phantom-1.9.2'

        # is just a blocking function that execute phantomjs
        p = Popen([binary, 'collect_included_url.js',
                   'http://%s' % url, destfile], stdout=PIPE)

        phantomlog = file(os.path.join(OUTPUTDIR, "phantom.log"), "a+")

        write_interruption_line(phantomlog, url, start=True)

        print colored(" + Executing %s on: %s" % (binary, url), "green"),
        while True:
            line = p.stdout.readline()
            if not line:
                break
            phantomlog.write(line)

        write_interruption_line(phantomlog, url, start=False)
        phantomlog.close()

    def validate_phantomjs_output():
        # return Bool or Int <: I feel dirty
        if not os.path.isfile(os.path.join(destfile, '__title')):
            print colored("__title file not generated! ", "red"),
            return False

        urlfile = os.path.join(destfile, '__urls')
        urlfp = file(urlfile, 'r')
        included_url_number = urlfp.readlines()
        urlfp.close()

        if included_url_number < 2:
            print colored("%d included URL from %s!" % included_url_number, "green")
            return False

        return len(included_url_number)

    # -- Here starts the do_phantom logic --
    software_execution()

    included_url_number = validate_phantomjs_output()
    if not included_url_number:
        print colored("Unable to fetch correctly %s, waiting 10 seconds and retry" % url, "red")
        time.sleep(10)
        software_execution()
        second_test = validate_phantomjs_output()
        if second_test:
            print colored("Ok! %d links" % second_test, "green")
            return 'failures'
        else:
            print colored("Failed again! :(", "red")
            return 'second'

    else:
        print colored("fetch %d URLs (%s)" % (included_url_number, media_kind), "green")
        return 'first'



class Traceroute:

    SLOW_TIMEOUT = "1.6"
    FAST_TIMEOUT = "0.6"
    SLOW_PROBES = "5"
    FAST_PROBES = "2"

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
        print colored("%s ..." % self.hostlist, "yellow")
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
            p = Popen(['traceroute', '-n', '-m 20', '-w', Traceroute.SLOW_TIMEOUT,
                       '-q', Traceroute.SLOW_PROBES, '-A', self.v4_target], stdout=PIPE)
        else:
            p = Popen(['traceroute', '-n', '-m 20', '-w', Traceroute.FAST_TIMEOUT,
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

        # TODO put this 20 in a variable passed also to -m above
        if self.iplist.count(None) == 20:
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
    parser.add_option("-v", "--version", action="store_true", dest="version",
                      help="print version, spoiler: %d" % ANALYSIS_VERSION)

    (args, _) = parser.parse_args()

    if args.version:
        print "analysis format version:", ANALYSIS_VERSION
        quit(0)

    if not args.medialist:
        print colored("Usage: %s -c $YOUR_COUNTRY_NAME" % sys.argv[0], "red", 'on_white')
        print colored("Other option are -l (local phantom, instead of the symlink here)", "red", 'on_white')
        print colored("Other option are -o output directory, used to collect test", "red", 'on_white')
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
                socket.setdefaulttimeout(0.5)
                resolved_v4 = socket.gethostbyname(domain)
            except Exception as xxx:
                dns_error[0].setdefault(xxx.strerror, []).append(domain)
                continue

            ip_map.setdefault(resolved_v4, []).append(domain)

            with file(resolution_dns_f, 'w+') as f:
                json.dump(ip_map, f)

    print colored("\nResolved %d unique IPv4 from %d unique domain" % (len(ip_map.keys()), len(included_url_dict.keys()) ), 'green')

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
            print colored("Traceroute fails!", "red")
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
    for case_n, failed_trace in enumerate(trace_stats['fail']):

        hostlist = ip_map[failed_trace]
        t = Traceroute(OUTPUTDIR, failed_trace, hostlist, gi, args.shitty_internet)
        counter += 1
        if not t.do_trace():
            print colored("Failure again.", "red")
            retinfo = "fail"
        else:
            retinfo = "retry"
            del trace_stats['fail'][case_n]
            try:
                t.resolve_target_geoip()
                t.file_dump()
            except Exception:
                retinfo = "anomaly"

        del t
        assert retinfo in [ 'recover', 'success', 'anomaly', 'fail', 'skipped', 'retry' ]
        trace_stats.setdefault(retinfo, []).append(ip_addr)


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

    print colored("%d file added to %s, Starting 'sender_results.py' program\n" % (counter_line, output_name), "green")
    print colored("If submitting results fails please type:", "red")
    print colored(" torify ./sender_results.py %s" % output_name, "green")
    print colored("If this command also fails (and raise a python Exception), please report the error to trackmap at tacticaltech dot org :)", 'red')

    # result sender has hardcoded our hidden service
    p = Popen(['torify', 'python', './sender_results.py', output_name], stdout=PIPE, stderr=PIPE)

    while True:
        line = p.stdout.readline()

        if not line:
            break

        if line:
            print colored("   %s" % line, 'yellow'),


if __name__ == '__main__':

    main()

