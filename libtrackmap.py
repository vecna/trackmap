#!/usr/bin/python

import os
import json
import datetime
from tldextract import TLDExtract
from termcolor import colored

INFOFILES = [ 'phantom.log', '_traceroutes', 'unique_id', 'used_media_list',
              '_verbotracelogs', 'domain.infos', 'country', 'information',
              'errors.dns', 'reverse.dns', 'resolution.dns',
              'first.json', 'second.json', 'third.json', '_phantom.trace.stats.json' ]

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
        for url in related_urls:

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
PERMITTED_SECTIONS = [ 'global', 'national', 'local', 'blog' ]

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
                print "Section", current_section, "has got # entries", counter_section
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
        print "Section", current_section, "has got # entries", counter_section

    return retdict


# The class Importer and the subclasses are used to read the results
# collected by perform_analysis.py script

class Importer:
    """
    Class (overloaded below) to load the 'output/' when received
    the validation are here (or the lack of thereof :( =) )
    distraction: https://www.youtube.com/watch?v=6wCgZh-nczY
    """

    def _pathof(self, filename):

        retpath = os.path.join(self.outputdir, filename)
        if not os.path.isfile(retpath):
            raise Exception("file %s not found" % retpath)
        return retpath


    def __init__(self, verified_media_dir, output_dir):
        """
        assertion on top, then init:
            self.country '<str>'
            self.contact_info '<dict>'
            self.unique_id '<int>'
            self.submission_date
        """
        assert os.path.isdir(verified_media_dir), "Invalid dir %s" % verified_media_dir
        assert os.path.isdir(output_dir), "Invalid dir %s" % output_dir

        self.outputdir = output_dir
        self.verified_media_dir = verified_media_dir

        self.country = None
        try:
            with file(self._pathof('country'), 'r') as c_f:
                country_name = c_f.readline()

            assert len(country_name) > 2 and len(country_name) < 30, "weird length"
            valid_country = str(country_name).lower()
            valid_country.strip(".,/;[}'\"\ %$?*\\-")

            our_media_list = os.path.join(verified_media_dir, valid_country)
            assert os.path.isfile(our_media_list), "Invalid country %s" % our_media_list

            self.country = valid_country

        except Exception as xxx:
            print "Country validation failed:", xxx
            raise xxx

        self.contact_info = None
        try:
            with file(self._pathof('information'), 'r') as info_f:
                info = json.load(info_f)

                assert isinstance(info, dict)
                assert info.has_key('city'), "missing city key"
                assert info.has_key('name'), "missing name key"
                assert info.has_key('ISP'), "missing ISP key"
                assert info.has_key('contact'), "missing contact key"
                assert info.has_key('version'), "missing contact key"
                assert len(info.keys()) == 5, "too much keys"

                self.contact_info = info
        except Exception as xxx:
            print "Contact information failed:", xxx
            raise xxx

        self.unique_id = None
        try:
            with file(self._pathof('unique_id'), 'r') as c_f:
                self.unique_id = int(c_f.readline())
        except Exception as xxx:
            print "unique ID retrieve fail:", xxx
            raise xxx

        # this is the date set on the file domain.infos
        self.submission_date = datetime.datetime.fromtimestamp(
                os.path.getctime( self._pathof('domain.infos') )
            )


    def get_cinfo_str(self):
        assert isinstance(self.contact_info, dict)

        cinfo_str = ""
        if self.contact_info['name'] and len(self.contact_info['name']):
            cinfo_str = "%s" % self.contact_info['name']
        if self.contact_info['ISP'] and len(self.contact_info['ISP']):
            cinfo_str = "%s %s" % (cinfo_str, self.contact_info['country'])
        return cinfo_str


    def __repr__(self):
        return "%s %s" % (self.country, self.get_cinfo_str() )


    def _validate_ipfile(self, fname):
        """
        can return an IPv4 in str, or None if was not avail
        """
        retip = None

        try:
            fp = file(self._pathof(fname), 'r')
            maybe_json = fp.readline()
            if maybe_json.startswith('Error'):
                return None

            ip_struct = json.loads(maybe_json)

            assert ip_struct.has_key('ip') and \
                   isinstance(ip_struct['ip'], unicode) and \
                   ip_struct['ip'].count('.') == 3 and \
                   len(ip_struct['ip']) > 6 and \
                   len(ip_struct['ip']) < 16, "Invalid ip key in %s: %s" % \
                                              (fname, ip_struct)

            # I'm not getting the hostname because of validation paranoia
            # will not fit with a DNS lookup that will delay my stuff running
            retip = ip_struct['ip']

        except Exception as xxx:
            print "Failure in retrieve ip from %s: %s" % (fname, xxx)
            raise xxx

        return retip


    def get_tester_ip(self):
        """
        Just to remind the format:
        { "ip":"1XX.X6.1XX.XXX",
          "name":"string",
          "ipnum":-15432432423
        }
        """
        raise Exception("This has not to be implemented here!")

    def get_TLD_map(self):
        pass
    def get_ipv4_map(self):
        pass
    def get_reverse_map(self):
        pass

    def get_details_per_media(self, media_url):
        """
        Return some details (title, objects, blah)
        in future will be expanded with more information about the kind of the
        inclusion, perhaps ?
        """
        try:
            title = file( self._pathof("%s/__title" % media_url) ).readline()
            included_url = get_unique_urls(media_url, self._pathof("%s/__urls" % media_url))
        except Exception as xxx:
            print "Unable to load properly media %s: %s" % (media_url, xxx)
            return None

        try:
            media_type = self.analyzed_media[media_url]
        except KeyError:
            print "Media", media_url,"has been scanned, but is removed from our list: importing as 'removed'"
            media_type = u'removed'

        try:
            title = file( self._pathof("%s/__title" % media_url) ).readline()
            active_object = True
        except Exception:
            active_object = False

        return {
            'title' : title,
            'included_url' : included_url,
            'media_type' : media_type,
            'active_object' : active_object
        }



    def get_included_hosts(self):
        self.domain_data = json.load(file(self._pathof('domain.infos'), 'r'))

        # TODO strongest validation ?
        assert isinstance(self.domain_data, dict)
        # Remind, struct is
        #
        # { "jabar.tribunnews.com":
        #   { "domain": "tribunnews",
        #     "subdomain": "jabar",
        #     "tld": "com"
        #   },
        #   "gp4.googleusercontent.com":
        #   { "domain": "googleusercontent",
        #     "subdomain": "gp4",
        #     "tld": "com"}
        #   }
        # }

        # assertion: need current media list
        assert isinstance(self.analyzed_media, dict) and \
               len(self.analyzed_media.keys()) > 1, "not initialized!"

        # is used 'sortify' function to fill out the domain.infos
        return self.domain_data.keys()


    def get_company(self, host):

        if not hasattr(self, 'disconnect_data'):
            try:
                # TODO check this file part of the git directory
                assert os.path.isfile('imported_disconnect.json')
                self.disconnect_data = json.load(file('imported_disconnect.json', 'r'))
            except Exception as xxx:
                print "Unable to load 'imported_disconnect.json':", xxx
                quit(-1)
            assert isinstance(self.disconnect_data, dict)

        try:
            tldparsed = self.domain_data.get(host)
            full_domain = "%s.%s" % (tldparsed['domain'], tldparsed['tld'])
            if self.disconnect_data.has_key(tldparsed['tld']):
                return self.disconnect_data[tldparsed['tld']]
            elif self.disconnect_data.has_key(full_domain):
                return self.disconnect_data[full_domain]
            else:
                return None
        except Exception:
            return None


    def get_trace_country(self, host):
        raise Exception("Has been implemented differently on version 1 or 3")


    def media_list_acquire(self):
        """
        get the current media list for the country,
        get the used media list in the analysis.
        populate:
            media_list_comparation '<str>'
            analyzed_media '<list>'
        """
        current_media_f = os.path.join(self.verified_media_dir, self.country)
        with file(current_media_f, 'r') as fp:
            current_media = media_file_cleanings(fp.readlines(),
                    os.path.join(self.verified_media_dir, '..', 'special_media', 'global')
            )
        # BUG ? the global media list is shared
        with file(self._pathof('used_media_list'), 'r') as fp:
            self.analyzed_media = media_file_cleanings(fp.readlines(),
                    os.path.join(self.verified_media_dir, '..', 'special_media', 'global')
            )

        now_present =  set(current_media) - set(self.analyzed_media)
        now_deleted =  set(self.analyzed_media) - set(current_media)
        self.media_list_comparation = {
            'now_present' : now_present,
            'now_deleted' : now_deleted
        }



class Import3(Importer):

    def get_success_ratio(self):

        with file(self._pathof("_phantom.trace.stats.json"), 'r') as fp:
            pha_tra_stat = json.load(fp)

        try:
            assert isinstance(pha_tra_stat, list)
            assert len(pha_tra_stat) == 2

            phantom_s = pha_tra_stat[0]
            trace_s = pha_tra_stat[1]

            assert isinstance(phantom_s, dict)
            assert isinstance(trace_s, dict)
        except Exception as xxx:
            print "Unable to load the Phantom/Traceroute stats: %s" % xxx
            raise xxx

        # collect the results of the large dict returning just three numbers
        self.phantom_stats = {}
        keys = [ 'first', 'second', 'failures']
        for k in keys:
            if phantom_s.has_key(k):
                self.phantom_stats[k] = len(phantom_s[k])
            else:
                self.phantom_stats[k] = 0

        # collect the number of True and False = the number of successful trace
        self.trace_stats = {
            'success' : trace_s.values().count(True),
            'failures' : trace_s.values().count(False)
        }
        return self.phantom_stats, self.trace_stats


    def get_tester_ip(self):

        self.client_ip = None
        try:
            ip1 = self._validate_ipfile('first.json')
            ip2 = self._validate_ipfile('second.json')
            ip3 = self._validate_ipfile('third.json')

            if not (ip1 or ip2 or ip3):
                raise Exception("Getting IP address failure!?")

            if ip1 and ip2:
                assert ip1 == ip2, "IP 1 and 2 mismatch"
            if ip1 and ip3:
                assert ip1 == ip3, "IP 1 and 3 mismatch"
            if ip2 and ip3:
                assert ip2 == ip3, "IP 2 and 3 mismatch"

            if ip1:
                self.client_ip = ip1
            if ip2:
                self.client_ip = ip2
            if ip3:
                self.client_ip = ip3

        except Exception as xxx:
            print "Unable to import the three IP json file", xxx
            raise xxx

        return self.client_ip


    def get_trace_country(self, host):
        """
        This is used differently in version 1 or version 3,
        Here is version 3
            has IP traced and
            symbolic link from the hostname
        """
        try:
            country_tjf = self._pathof('_traceroutes/%s.countries' % host)
            assert os.path.islink(country_tjf), "Not a symlink as expected"
        except Exception:
            print "No traceroute output available for %s" % host
            return None

        country_list = []
        with file(country_tjf) as f:
            # convert the ordered dictionary in a list
            numeric_flow_of_country = json.load(f)
            limit = len(numeric_flow_of_country.keys())

            for i in xrange(limit):
                unicode_key = u"%s" % i

                # TODO - remove dups,
                country_list.append(numeric_flow_of_country[unicode_key])

        return country_list


    def get_trace_tim(self, host):
        return os.path.getctime(
            self._pathof('_traceroutes/%s.countries' % host)
        )



class Import1(Importer):

    def get_tester_ip(self):

        self.client_ip = None
        try:
            ip1 = self._validate_ipfile('first.json')
            ip2 = self._validate_ipfile('second.json')

            if not (ip1 or ip2):
                raise Exception("Getting IP address failure!?")

            if ip1 and ip2:
                assert ip1 == ip2, "IP mismatch"

            self.client_ip = ip1 if ip1 else ip2

        except Exception as xxx:
            print "Unable to get matching IP from the files", xxx
            raise xxx

        return self.client_ip

    def get_trace_complete(self, host):
        """

        try:
        # IP traceroute dict
    ip_pick_f = os.path.join(datadir, '_traceroutes', "%s_countries.json" % included)

    # Country conversion of IP tracerouted dict
    country_pick_f = os.path.join(datadir, '_traceroutes', "%s_countries.json" % included)

    if not (os.path.isfile(ip_pick_f) and os.path.isfile(country_pick_f) ):
        print "Fatal ? missing one of", ip_pick_f, country_pick_f
        raise Exception("Missing output of expected tracroute: %s" % included)

    with file(ip_pick_f) as f:
        route.routing_ip_chain = json.load(f)

    with file(country_pick_f) as f:
        # convert the ordered dictionary in a list
        numeric_flow_of_country = json.load(f)
        limit = len(numeric_flow_of_country.keys())
        route.routing_country_chain = []

        for i in xrange(limit):
            unicode_key = u"%s" % i
            route.routing_country_chain.append(numeric_flow_of_country[unicode_key])

    with file(os.path.join(datadir, '_verbotracelogs', urldir), 'r') as f:
        route.routing_raw_output = unicode(f.read())

    store.add(route)
        """
        raise Exception("NYI")


    def get_trace_country(self, host):
        """
        This is used differently in version 1 or version 3,
        Here is version 1:
            has every host a traceroute dump in .json
            they are "trace JSON files"
        """
        try:
            country_tjf = self._pathof('_traceroutes/%s_countries.json' % host)
        except Exception:
            print "No traceroute output available for %s" % host
            return None

        country_list = []
        with file(country_tjf) as f:
            # convert the ordered dictionary in a list
            numeric_flow_of_country = json.load(f)
            limit = len(numeric_flow_of_country.keys())

            for i in xrange(limit):
                unicode_key = u"%s" % i

                # TODO - remove dups,
                country_list.append(numeric_flow_of_country[unicode_key])

        return country_list


    def get_trace_tim(self, host):
        return os.path.getctime(
            self._pathof('_traceroutes/%s_countries.json' % host)
        )



