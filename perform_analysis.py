#!/usr/bin/python

import os, re, json, sys, random, time
import GeoIP
import tldextract

from subprocess import Popen, PIPE
from termcolor import colored
from libtrackmap import sortify, media_file_cleanings

OUTPUTDIR = 'output'
PERMITTED_SECTIONS = [ 'global', 'national', 'local', 'blog' ]

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


def do_phantomjs(url, destfile, media_kind):
    # information that deserve to be saved for the time
    kindfile = os.path.join(destfile, '__kind')
    with file(kindfile, 'w+') as f:
        f.write(media_kind + "\n")

    def software_execution():

        # is just a blocking function that execute phantomjs
        p = Popen(['phantomjs', 'collect_included_url.js',
                   'http://%s' % url, destfile], stdout=PIPE)

        phantomlog = file(os.path.join(OUTPUTDIR, "phantom.log"), "a+")

        write_interruption_line(phantomlog, url, start=True)

        print colored(" + Executing phantomjs on: %s" % url, "green"),
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
        f = file(urlfile, 'r')
        included_url_number = f.readlines()
        f.close()

        if included_url_number < 2:
            print colored("%d included URL from %s!" % included_url_number, "green")
            return False

        return len(included_url_number)

    # this is the code
    software_execution()

    included_url_number = validate_phantomjs_output()
    if not included_url_number:
        print colored("Unable to fetch correctly %s, waiting 60 seconds and retry" % url, "red")
        time.sleep(60)
        software_execution()
        second_test = validate_phantomjs_output()
        if second_test:
            print colored("Ok! %d links" % second_test, "green")
        else:
            print colored("Failed again! :(", "red")

    else:
        print colored("Correctly fetch %d URLs - %s media" % (included_url_number, media_kind), "green")


def do_trace(dumpprefix, host):

    ip_file = os.path.join(OUTPUTDIR, '_traceroutes', "%s_ip.json" % dumpprefix)
    country_file = os.path.join(OUTPUTDIR, '_traceroutes', "%s_countries.json" % dumpprefix)

    if os.path.isfile(ip_file) and os.path.isfile(country_file):
        print host, "already traced: skipping"
        return
    else:
        print "[T]", host,

    iplist = []
    asterisks_total = 0
    p = Popen(['traceroute', '-n', '-w', '0.5', '-q', '10', '-A', host], stdout=PIPE)

    logfile = file(os.path.join(OUTPUTDIR, '_verbotracelogs', host), "w+")

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
        asterisks_total += asterisks

        ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
        if not ip:
            continue
        iplist.append(ip)

    logfile.close()

    with file(ip_file, 'w+') as f:
        json.dump(iplist, f)

    with file(country_file, 'w+') as f:
        gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
        country_travel_path = {}
        counter = 0

        print len(iplist), "HOP through",
        for ip in iplist:

            # is always as list ['x.x.x.x'] sometime more than 1
            if isinstance(ip, list):
                ip = ip[0]

            print gi.country_code_by_addr(ip),
            country = gi.country_name_by_addr(ip)
            country_travel_path.update({counter:country})
            counter += 1

        json.dump(country_travel_path, f)

    print colored("* = %d" % asterisks_total, 'red')


def main():
    if not os.path.isdir(OUTPUTDIR):
        try:
            os.mkdir(OUTPUTDIR)
        except OSError as error:
            print "unable to create %s: %s" % (OUTPUTDIR, error)

    if len(sys.argv) != 2:
        print "Expected one of the file in verified_media/"
        print "hopefully the name of your country"
        quit(-1)

    # writing in a file which country you're using!
    with file(os.path.join(OUTPUTDIR, 'country'), 'w+') as f:
        f.write(sys.argv[1])

    with file(sys.argv[1]) as f:

        media_entries = media_file_cleanings(f.readlines())

        # TODO Status integrity check on the media directory
        for cleanurl, media_kind in media_entries.iteritems():

            urldir = os.path.join(OUTPUTDIR, cleanurl)
            if not os.path.isdir(urldir):
                print "+ Creating directory", urldir
                os.mkdir(urldir)

                do_phantomjs(cleanurl, urldir, media_kind)
            else:
                print "-", urldir, "Already present: skipped"

        # take every directory in 'output/' and works on the content
        included_url_dict = sortify(OUTPUTDIR)

        assert included_url_dict, "No url included after phantom scraping and collection !?"

        with file(os.path.join(OUTPUTDIR, 'domain.infos'), 'w+') as f:
            json.dump(included_url_dict, f)

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

        print "running traceroute to", len(included_url_dict.keys()), "hosts!"
        counter = 1
        for url, domain_info in included_url_dict.iteritems():
            print colored("%d/%d\t" % (counter, len(included_url_dict.keys()) ), "cyan" ),
            # TODO do_trace verify_trace_output eventually do_trace with more timeoout
            do_trace(url, url)
            counter += 1

        if os.path.isfile('results.tar.gz'):
            print "Finished! and the data is already compressed ? remove results.tar.gz to make a new one"
            quit(0)

        # putting the unique number into
        with file( os.path.join(OUTPUTDIR, "unique_id"), "w+") as f:
            f.write("%d%d%d" % (random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff)) )

        basename_media = os.path.basename(sys.argv[1])
        print "Finished! compressing the data", basename_media

        output_name = 'results-%s.tar.gz' % basename_media
        tar = Popen(['tar', '-z', '-c', '-v', '-f', output_name, OUTPUTDIR], stdout=PIPE)

        counter_line = 0
        while True:
            line = tar.stdout.readline()
            counter_line += 1
            if not line:
                break

        print counter_line
        print "Now please send %s to vecna{AT}globaleaks[DOT]org" % output_name


if __name__ == '__main__':
    main()

