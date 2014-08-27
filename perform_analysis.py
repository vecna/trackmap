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
    from subprocess import Popen, PIPE
    from termcolor import colored
    from libtrackmap import sortify, media_file_cleanings
except ImportError:
    print "TrackMap collection system is not correctly installed"
    print "Please, follow the instruction or mail to trackmap at tacticaltech.org"
    print "https://github.com/vecna/helpagainsttrack"
    quit(-1)

ANALYSIS_VERSION = 2
OUTPUTDIR = 'output'

def do_wget(fdestname):

    if os.path.isfile('index.html'):
        raise Exception("Why you've an index.html file here ? report this error please")

    p = Popen(['wget', 'http://json.whatisyourip.org/'], stdout=PIPE, stderr=PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break

    pathdest = os.path.join(OUTPUTDIR, fdestname)
    if os.path.isfile('index.html'):
        shutil.move('index.html', pathdest)
    else:
        with file(pathdest, 'w+') as fp:
            fp.write("Error :\\")



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


def do_phantomjs(local_phantomjs, url, destfile, media_kind):
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
        print colored("Unable to fetch correctly %s, waiting 30 seconds and retry" % url, "red")
        time.sleep(30)
        software_execution()
        second_test = validate_phantomjs_output()
        if second_test:
            print colored("Ok! %d links" % second_test, "green")
        else:
            print colored("Failed again! :(", "red")

    else:
        print colored("fetch %d URLs (%s)" % (included_url_number, media_kind), "green")


def do_trace(hostlist, ipv4):

    def software_execution(timeout):
        # commonly timeout is '0.5' but can be increase to '2.1'

        iplist = []
        asterisks_total = 0
        p = Popen(['traceroute', '-n', '-w', timeout, '-q', '10', '-A', ipv4], stdout=PIPE)

        traceoutf = os.path.join(OUTPUTDIR, '_verbotracelogs', ipv4)
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
            asterisks_total += asterisks

            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
            if not ip:
                iplist.append(None)
                continue
            iplist.append(ip)

        logfile.close()
        return asterisks_total, iplist

    def validate_traceroute_output(asterisk_amount, tracelines, tolerance):
        # what I wanna spot is traceroute can give a better results
        if len(tracelines) == 30:
            # we've got an host that do not return answers
            while True:

                # if this happen, are 300 *'s
                if not len(tracelines):
                    return False

                if not tracelines[-1]:
                    asterisk_amount -= 10
                    tracelines.pop()
                else:
                    break

        medium_failures = asterisk_amount / len(tracelines)

        if medium_failures > 3 and not tolerance:
            return False
        if medium_failures > 6 and tolerance:
            return False

        return True


    # -- Here starts the do_trace logic --

    host_check = hostlist[0]

    check_ip_link = os.path.join(OUTPUTDIR, '_traceroutes', "%s_ip.json" % host_check)
    check_country_link = os.path.join(OUTPUTDIR, '_traceroutes', "%s_countries.json" % host_check)

    if os.path.islink(check_ip_link) and os.path.islink(check_country_link):
        print colored ("%s already traced (%d hosts): skipping" %
                       (ipv4, len(hostlist) ), "green")
        return True
    else:
        print ipv4,

    totalsterisks, iplist = software_execution("0.5")

    if not validate_traceroute_output(totalsterisks, iplist, tolerance=False):
        print colored("Traceroute got %d *'s: waiting 10 seconds and retry slower" % totalsterisks, "red"),
        time.sleep(10)
        secondtotalrisks, iplist = software_execution("2.1")
        if validate_traceroute_output(secondtotalrisks, iplist, tolerance=True):
            print colored("\n\tOk! tracerouted with a more reliable output (%d)" % secondtotalrisks, "green"),
        else:
            print colored("\n\tFailed again! (%d *'s)" % secondtotalrisks, "red")
            return False

    # resolve Geo info for all the IP involved
    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    country_travel_path = {}
    counter = 0
    print len(iplist), "HOP through",
    for ip in iplist:

        # if is an "* * * * *" I'll record as None and here is stripped
        if not ip:
            continue

        # is always as list ['x.x.x.x'] sometime more than 1
        if isinstance(ip, list):
            ip = ip[0]

        code = gi.country_code_by_addr(ip)
        if not code:
            print colored(code, "red"),
        else:
            print colored(code, "green"),

        country = gi.country_name_by_addr(ip)
        country_travel_path.update({counter:country})
        counter += 1

    print "Done"

    # dump in the IPv4 file and then make symlink
    ip_list_file = os.path.join(OUTPUTDIR, '_traceroutes', "%s_ip.json" % ipv4)
    country_list_file = os.path.join(OUTPUTDIR, '_traceroutes', "%s_countries.json" % ipv4)

    with file(ip_list_file, 'w+') as f:
        json.dump(iplist, f)

    with file(check_country_link, 'w+') as f:
        json.dump(country_travel_path, f)

    for host in hostlist:

        ip_host_link = os.path.join(OUTPUTDIR, '_traceroutes', "%s.ip" % host)
        country_host_link = os.path.join(OUTPUTDIR, '_traceroutes', "%s.countries" % host)

        try:
            os.symlink( ip_list_file, ip_host_link )
            os.symlink( country_list_file, country_host_link )
        except Exception as xxx:
            print colored("Failure in symlink %s to %s: %s" % (
                ipv4, host, xxx
            ))
            continue

    return True


def main():
    if not os.path.isdir(OUTPUTDIR):
        try:
            os.mkdir(OUTPUTDIR)
        except OSError as error:
            print "unable to create %s: %s" % (OUTPUTDIR, error)

    if len(sys.argv) < 2:
        print colored("Usage: %s $YOUR_COUNTRY_NAME <lp>" % sys.argv[0], "red", 'on_white')
        print ""
        print " 'lp' as 3rd argument is needed if you want use your own /usr/bin/phantomjs"
        print " (if you follow README.md, this is not needed because you downloaded phantomjs 1.9.2)"
        print " ",colored("By default, this software is looking for symlink 'phantom-1.9.2'", "green", "on_white")
        if os.path.islink('phantom-1.9.2'):
            print " ",colored("phantom-1.9.2 is a link, as expected.", "green", "on_white")
        else:
            print " ",colored("The phantom-1.9.2 link is missing!", "red", "on_white")
        print "Look in the verified_media/ for a list of countries."
        quit(-1)

    # check if the user is running phantom as installed on the system (also vagrant make this)
    # of if is using
    if len(sys.argv) == 3 and sys.argv[2] == 'lp':
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

    # country check
    proposed_country = sys.argv[1]
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

    print colored(" ࿓  Importing media list:", 'blue', 'on_white', attrs=['underline'])
    media_entries = media_file_cleanings(unclean_lines)
    cfp.close()

    print colored(" ࿓  Checking your network source.", 'blue', 'on_white', attrs=['underline'])
    do_wget('first.json')

    print colored(" ࿓  Starting media crawling:", 'blue', 'on_white', attrs=['underline'])
    # here start iteration over the media!
    for cleanurl, media_kind in media_entries.iteritems():

        urldir = os.path.join(OUTPUTDIR, cleanurl)
        title_check = os.path.join(urldir, '__title')

        if os.path.isdir(urldir) and os.path.isfile(title_check):
            print "-", urldir, "already present: skipped"
            continue

        if os.path.isdir(urldir):
            # being here means that is empty or incomplete
            shutil.rmtree(urldir)

        print "+ Creating directory", urldir
        os.mkdir(urldir)

        do_phantomjs(local_phantomjs, cleanurl, urldir, media_kind)

    # take every directory in 'output/', get the included URL and dump in a dict
    included_url_dict = sortify(OUTPUTDIR)
    assert included_url_dict, "No url included after phantom scraping and collection !?"
    with file(os.path.join(OUTPUTDIR, 'domain.infos'), 'w+') as f:
        json.dump(included_url_dict, f)

    # generate DNS resolution map. for every host resolve an IP, for every IP resolve again DNS
    print colored(" ࿓  DNS resolution and reverse of %d domains" % len(included_url_dict), 'blue', 'on_white', attrs=['underline'])
    # when a "+" is printed, mean that a new IP/reverse has been added,
    # when a "*" is printed, mean that an older IP/reverse has a new associate
    # when a "-" is printed, has been an error!
    dns_error = []

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

            try:
                socket.setdefaulttimeout(0.5)
                resolved_v4 = socket.gethostbyname(domain)
            except Exception as xxx:
                dns_error.append([domain, xxx.strerror])
                continue

            ip_map.setdefault(resolved_v4, []).append(domain)

        with file(resolution_dns_f, 'w+') as f:
            json.dump(ip_map, f)

    print colored("\nResolved %d unique IPv4 from %d unique domain" % (len(ip_map.keys()), len(included_url_dict.keys()) ), 'green')

    if len(dns_error) == len(included_url_dict.keys()):
        print colored("It appears that you can't access the internet. Please fix that and restart the test.", 'red')
        quit(-1)

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

            try:
                socket.setdefaulttimeout(0.9)
                resolved_set = socket.gethostbyaddr(ipv4)
                resolved_name = resolved_set[0]
            except Exception as xxx:
                dns_error.append([ipv4, xxx.strerror])
                continue

            true_domain_map.setdefault(resolved_name, []).append(ipv4)

        with file(reverse_dns_f, 'w+') as f:
            json.dump(true_domain_map, f)

    print colored("\nReversed %d unique FQDN" % len(true_domain_map.keys() ), 'green')

    if len(dns_error):
        print colored("Saving %d errors in 'errors.dns'" % len(dns_error))
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
    do_wget('second.json')

    # starting traceroute to all the collected IP
    print colored(" ࿓  Running traceroute to %d IP address (from %d hosts)" % (
        len(ip_map.keys()),
        len(included_url_dict.keys())),
                  'blue', 'on_white', attrs=['underline'])

    counter = 1
    failure = 0
    for ip_addr, hostlist in ip_map.iteritems():

        progress_string = "%d/%d" % (counter, len(ip_map.keys()))
        print colored("%s%s" % (progress_string, (10 - len(progress_string)) * " " ), "cyan" ),

        if not do_trace(hostlist, ip_addr):
            failure += 1
        counter += 1

    if failure:
        print colored("Registered %d failures" % failure, "red")

    # putting the unique number into
    with file( os.path.join(OUTPUTDIR, "unique_id"), "w+") as f:
        f.write("%d%d%d" % (random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff)) )

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


    print colored("%d file added to %s, Starting 'result_sender.py'\n" % (counter_line, output_name), "green")
    print colored("If submitting results fails please type:", "red")
    print colored(" torify python ./sender_results.py %s" % output_name, "green")
    print colored("If this command also fails (and raise a python Exception), please report the error to trackmap at tacticaltech dot org :)", 'red')

    # result sender has hardcoded our hidden service
    p = Popen(['torify', 'python', './sender_results.py', output_name], stdout=PIPE, stderr=PIPE)

    while True:
        line = p.stdout.readline()
        exx = p.stderr.readline()

        if not line and not exx:
            break

        if exx.find('failed to find the symbol') != -1:
            continue
        if exx.find('libtorsocks') != -1:
            continue

        if line:
            print colored("   %s" % line, 'yellow')
        if exx:
            print colored(exx, 'red')


if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print "TrackMap collection tool version: %d" % ANALYSIS_VERSION
        quit(0)

    main()

