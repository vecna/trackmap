#!/usr/bin/python

from subprocess import Popen, PIPE
import os, re, pickle, sys
import GeoIP
import tldextract

OUTPUTDIR = 'output'


def do_phantomjs(url, destfile):

    p = Popen(['phantomjs', 'collect_included_url.js',
               '%s' % url, destfile], stdout=PIPE)

    phantomlog = file(os.path.join(OUTPUTDIR, "phantom.log"), "a+")

    print " + Executing phantomjs on", url,
    while True:
        line = p.stdout.readline()
        if not line:
            break
        phantomlog.write(line)

    urlfile = os.path.join(destfile, '__urls')
    with file(urlfile, 'r') as f:
        print "acquired", len(f.readlines()),"included URLs"

    return urlfile



def get_unique_urls(urldumpsf):
    urls = {}
    with file(urldumpsf) as f:
        for url_request in f.readlines():
            if url_request.startswith('http://'):
                urls[ url_request[7:].split('/')[0] ] = True
            elif url_request.startswith('https://'):
                urls[ url_request[8:].split('/')[0] ] = True
            elif url_request.startswith('data:'):
                continue
            else:
                raise AssertionError("missing http:// or https:// in [%s]" % url_request)

    return urls.keys()


def do_trace(dumpfile, host):

    ip_file = "%s_ip.pickle" % dumpfile
    country_file = "%s_countries.pickle" % dumpfile

    if os.path.isfile(ip_file) and os.path.isfile(country_file):
        print "%s already managed, skipping" % host
        return

    iplist = []
    # p = Popen(['traceroute', host], stdout=PIPE)

    #tmpfile = file("/tmp/traceoutput.log", "a+")

    ff = file("/tmp/xxx", 'r')
    while True:
        # line = p.stdout.readline()
        line = ff.readline()
        if not line:
            break
        #tmpfile.write(line);

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

    #tmpfile.close()

    with file("%s_ip.pickle" % dumpfile, 'w+') as f:
        pickle.dump(iplist, f)

    with file("%s_countries.pickle" % dumpfile, 'w+') as f:
        gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
        country_travel_path = {}
        counter = 0
        for ip in iplist:

            if isinstance(ip, list):
                # to reduce complexity, multiple resolved hosts provide just the first IP addr
                ip = ip[0]

            # gi.country_code_by_addr(ip)
            country = gi.country_name_by_addr(ip)
            country_travel_path.update({counter:country})
            counter += 1

        pickle.dump(country_travel_path, f)


def iter_over_urls(unique_urls, medianame):

    basedestdir = os.path.join(OUTPUTDIR, medianame)
    try:
        if not os.path.isdir(basedestdir):
            os.mkdir(basedestdir)
    except OSError as error:
        print "Error in creating %s: %s" % (basedestdir, error)

    for url in unique_urls:
        analyzedurl = os.path.join(basedestdir, url)
        print "going deep with %s for [%s]" % (url, medianame)
        do_trace(analyzedurl, url)


def sortify():

    urldict = {}
    for urldir in os.listdir(OUTPUTDIR):

        urlfile = os.path.join(OUTPUTDIR, urldir, '__urls')
        related_urls = get_unique_urls(urlfile)

        for url in related_urls:

            if urldict.has_key(url):
                continue

            domain = tldextract.extract(url)
            urldict.update({url : domain })

    return urldict


if __name__ == '__main__':

    if not os.path.isdir(OUTPUTDIR):
        try:
            os.mkdir(OUTPUTDIR)
        except OSError as error:
            print "unable to create %s: %s" % (OUTPUTDIR, error)

    # 1st download/check available media list / ask your country
    # TODO

    # 2nd download media list
    # TODO

    # 3rd work over the media list
    # TODO do not require sys.argv[1]

    if len(sys.argv) != 2:
        print "Expected one of the file in media_lists/"
        print "hopefully the name of your country"
        quit(-1)

    with file(sys.argv[1]) as f:

        media_entries = f.readlines()

        # TODO Status integrity check on the media diretory
        for media in media_entries:

            media = media[:-1]

            assert media.startswith('http://'), "Invalid URL %s (http ?!) " % media
            cleanurl = media[7:].replace('/', '_')

            dirtyoptions = cleanurl.find("?")
            if dirtyoptions:
                cleanurl = cleanurl[:dirtyoptions]

            if cleanurl[-1] == '/':
                cleanurl = cleanurl[:-1]

            urldir = os.path.join(OUTPUTDIR, cleanurl)
            if not os.path.isdir(urldir):
                print "+ Creating directory", urldir
                os.mkdir(urldir)

                do_phantomjs(media, urldir)

        # take every directory in 'output/' and works on the content
        included_url_dict = sortify()

        import pdb; pdb.set_trace()
        # rewind to 0 in order to process the second step
        f.seek(0)

        media_entries = f.readlines()

        for media in media_entries:
            media = media[:-1]

            urldumpsf = os.path.join(OUTPUTDIR, media, '__urls')
            assert os.path.isfile(urldumpsf), "do not exists %s" % urldumpsf

            unique_urls = get_unique_urls(urldumpsf)
            print "%s has %d unique url included" % (media, len(unique_urls) )

            iter_over_urls(unique_urls, media)

