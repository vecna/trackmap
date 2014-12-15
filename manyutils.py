
import os
import json
import datetime
import GeoIP
import operator

from tldextract import TLDExtract
from termcolor import colored

INFOFILES = [ 'phantom.log', '_traceroutes', 'unique_id', 'used_media.json',
              '_verbotracelogs', 'domain.infos', 'country', 'information',
              'errors.dns', 
              'reverse.dns', 
              'reverse.status.json',
              'reverse.errors.json',
              'resolution.dns', 
              'resolution.status.json',
              'resolution.errors.json',
              'first.json', 'second.json', 'third.json',
              'phantom.results.json', 'trace.results.json' ]

PERMITTED_SECTIONS = [ 'global', 'national', 'local', 'blog', 'removed' ]


def get_unique_urls(source_urldir, urldumpsf):
    urls = {}
    with file(urldumpsf) as f:
        for url_request in f.readlines():
            if url_request.startswith('http://'):
                urls[ url_request[7:].split('/')[0] ] = True
            elif url_request.startswith('https://'):
                urls[ url_request[8:].split('/')[0] ] = True
            elif url_request.startswith('data:'):
                continue
            elif url_request.startswith('about:blank'):
                continue
            else:
                print colored("%% Unexpected URL schema '%s' from '%s'" % ( url_request, source_urldir ), 'red')
                continue

    return urls.keys()

def sortify(outputdir):

    urldict = {}
    skipped = 0

    for urldir in os.listdir(outputdir):

        if urldir in INFOFILES:
            continue

        try:
            urlfile = os.path.join(outputdir, urldir, '__urls')
            related_urls = get_unique_urls(urldir, urlfile)
        except IOError or OSError as einfo:
            print "Unable to read", urldir, einfo, "skipping"
            continue

        TLDio = TLDExtract(cache_file='mozilla_tld_file.dat')
        for dirty_url in related_urls:
            # dirty_url because may contain ":"

            if dirty_url.split(':') != -1:
                url = dirty_url.split(':')[0]
            else:
                url = dirty_url

            if urldict.has_key(url):
                skipped +=1
                continue

            dnsplit= TLDio(url)
            urldict.update({url : {
                    'domain' : dnsplit.domain,
                    'tld' : dnsplit.suffix,
                    'subdomain' : dnsplit.subdomain }
                })

        # note:
        # https://raw.github.com/mozilla/gecko-dev/master/netwerk/dns/effective_tld_names.dat
        # tldextract is based on this file, and cloudfront.net is readed as TLD. but is fine
        # I've only to sum domain + TLD in order to identify the "included entity"
    return urldict


def url_cleaner(line):
    # TODO remove - included in includedHost

    # cleanurl is used to create the dir, media to phantomjs
    if line.startswith('http://'):
        cleanurl = line[7:]
    elif line.startswith('https://'):
        cleanurl = line[8:]
        print "https will be converted in http =>", line
    else:
        raise Exception("Invalid protocol in: %s" % line)

    while cleanurl[-1] == '/':
        cleanurl = cleanurl[:-1]

    dirtyoptions = cleanurl.find("?")
    if dirtyoptions != -1:
        cleanurl = cleanurl[:dirtyoptions]

    cleanurl = cleanurl.split('/')[0]
    return cleanurl


def load_global_file(GLOBAL_MEDIA_FILE):

    global_media_dict = {}
    counter = 0

    with file(GLOBAL_MEDIA_FILE, 'r') as f:
        for line in f.readlines():

            line = line[:-1]

            if len(line) > 1 and line[0] == '#':
                continue

            # everything after a 0x20 need to be cut off
            line = line.split(' ')[0]

            if len(line) < 3:
                continue

            cleanurl = url_cleaner(line)
            counter += 1
            global_media_dict.update({ cleanurl : 'global' })

    return global_media_dict, counter


GLOBAL_MEDIA_FILE = 'special_media/global'

def media_file_cleanings(linelist, globalfile=GLOBAL_MEDIA_FILE):
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
                global_section, counter_section = load_global_file(globalfile)
                retdict.update(global_section)
                current_section = candidate_section
                continue

            if current_section:
                # print "Section", current_section, "has got # entries", counter_section
                counter_section = 0

            current_section = candidate_section
            continue

        cleanurl = url_cleaner(line)
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

