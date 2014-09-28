#!/usr/bin/python

import os
import json
import datetime
import GeoIP
import operator

from tldextract import TLDExtract
from termcolor import colored

INFOFILES = [ 'phantom.log', '_traceroutes', 'unique_id', 'used_media_list',
              '_verbotracelogs', 'domain.infos', 'country', 'information',
              'errors.dns', 'reverse.dns', 'resolution.dns',
              'first.json', 'second.json', 'third.json', '_phantom.trace.stats.json' ]

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


def ip_to_country_tuple(ip):
    """
    This can be removed and or/never called by perform_analysis: is useless
    in the supporter computer, I can compute them only before the import
    """

    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    cc = gi.country_code_by_addr(ip)
    cn = gi.country_name_by_addr(ip)
    del gi
    return cc, cn



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

        # will be initialized later, if
        self.resolution_dns = None

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
            cinfo_str = "%s %s" % (cinfo_str, self.contact_info['ISP'])
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

        if self.resolution_dns:
            return self.resolution_dns

        with file(self._pathof('resolution.dns')) as fp:
            self.resolution_dns = json.load(fp)

        return self.resolution_dns



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

        if not hasattr(self, 'domain_data') :
            self.get_included_hosts()

        assert isinstance(self.disconnect_data, dict)
        assert isinstance(self.domain_data, dict)

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

    def _phantom_collected_stats(self, stored_info):

        assert self.analyzed_media, "Is not yet initialized analyzed_media"

        retdict = {}
        keys = [ 'first', 'second', 'failures']

        for k in keys:
            if stored_info.has_key(k):
                retdict[k] = len(stored_info[k])
            else:
                retdict[k] = 0

        retdict.update({
            'total' : len(self.analyzed_media)
        })
        return retdict


    def get_success_ratio(self):
        """
        In version three are collected correctly only

        """

        with file(self._pathof("_phantom.trace.stats.json"), 'r') as fp:
            mixed_stats = json.load(fp)

        try:
            assert isinstance(mixed_stats, list)
            assert len(mixed_stats) == 2

            phantom_s = mixed_stats[0]
            # Here are broken and useless: mixed_stats[1]

            assert isinstance(phantom_s, dict)
        except Exception as xxx:
            print "Unable to load the Phantom/Traceroute stats: %s" % xxx
            raise xxx

        self.phantom_stats = self._phantom_collected_stats(phantom_s)
        return self.phantom_stats


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
        return [list], 'target_country'
        """

        country_tjf = self._pathof('_traceroutes/%s.countries' % host)
        # exception is catch on caller
        assert os.path.islink(country_tjf), "Not a symlink as expected"

        country_list = []
        with file(country_tjf) as f:
            # convert the ordered dictionary in a list
            numeric_flow_of_country = json.load(f)
            limit = len(numeric_flow_of_country.keys())

            for i in xrange(limit):
                unicode_key = u"%s" % i
                country_list.append(numeric_flow_of_country[unicode_key])

        # before return country_list is resolved target destination
        target_v4 = local_resolve_host(host, self.resolution_dns)
        target_country_name = ip_to_country_tuple(target_v4)[1]

        return country_list, target_country_name


    def get_trace_tim(self, host):
        return os.path.getctime(
            self._pathof('_traceroutes/%s.countries' % host)
        )




class Import4(Import3):


    def _trace_collected_stata(self, received_stats):

        retdict = {}
        keys = ['fail', 'anomaly', 'skipped', 'recover', 'success']

        for k in keys:
            if received_stats.has_key(k):
                retdict.update({k : len(received_stats[k])})
            else:
                retdict.update({k : 0})

        retdict.update({
            'total' : len(self.resolution_dns.keys())
        })
        return retdict


    def get_success_ratio(self):
        """
        In version three are collected correctly only
        """

        with file(self._pathof("_phantom.trace.stats.json"), 'r') as fp:
            mixed_stats = json.load(fp)

        try:
            assert isinstance(mixed_stats, list)
            assert len(mixed_stats) == 2

            phantom_s = mixed_stats[0]
            traces_s = mixed_stats[1]

            assert isinstance(phantom_s, dict)
            assert isinstance(traces_s, dict)

        except Exception as xxx:
            print "Unable to load the Phantom/Traceroute stats: %s" % xxx
            raise xxx

        self.phantom_stats = self._phantom_collected_stats(phantom_s)
        self.trace_stats = self._trace_collected_stata(traces_s)

        return self.phantom_stats, self.trace_stats


    def get_trace_country(self, host):
        """
        Here is version 4
            has IP traced and
            symbolic link from the hostname
            inside of the traced data there are a list and not a dict
            [
                { "0": null, "1": "Italy", "2": "Italy", "3": "Italy",
                  "4": "Italy", "5": "Netherlands", "6": "Europe"
                },
                ["Europe", "EU"]
            ]
        """
        country_tjf = self._pathof('_traceroutes/%s_countries.json' % host)
        # exception catch on caller
        assert os.path.islink(country_tjf), "Not a symlink as expected"

        country_list = []
        with file(country_tjf) as f:
            # convert the ordered dictionary in a list
            composed_traceout = json.load(f)

            destination_location = composed_traceout[1]
            assert isinstance(destination_location, list), "*Expected list %s" % host
            numeric_flow_of_country = composed_traceout[0]
            assert isinstance(numeric_flow_of_country, dict), "*Expected dict %s" % host

            limit = len(numeric_flow_of_country.keys())

            for i in xrange(limit):
                unicode_key = u"%s" % i
                country_list.append(numeric_flow_of_country[unicode_key])

        self.target_geoip = destination_location[0]

        # destination_location is [ CountryName, CCode ]
        #if country_list[-1] != destination_location[0]:
        #    country_list.append(destination_location[0])
        #    Import4.Useful_times += 1

        return country_list, self.target_geoip

    def get_trace_tim(self, host):
        try:
            retfloat = os.path.getctime(
                self._pathof('_traceroutes/%s_countries.json' % host)
            )
            return retfloat
        except Exception as xxx:
            # do not rise alarm the coutry chain is still missing
            # on the mediaroute. class
            return 0.0




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

        # if file do not exist, exception catch on caller
        country_tjf = self._pathof('_traceroutes/%s_countries.json' % host)

        country_list = []
        with file(country_tjf) as f:
            # convert the ordered dictionary in a list
            numeric_flow_of_country = json.load(f)
            limit = len(numeric_flow_of_country.keys())

            for i in xrange(limit):
                unicode_key = u"%s" % i
                country_list.append(numeric_flow_of_country[unicode_key])

        # before return country_list is resolved target destination
        target_v4 = local_resolve_host(host, self.resolution_dns)
        target_country_name = ip_to_country_tuple(target_v4)[1]

        return country_list, target_country_name


    def get_trace_tim(self, host):
        return os.path.getctime(
            self._pathof('_traceroutes/%s_countries.json' % host)
        )




def local_resolve_host(host, resolution_storage):

    for ip, hostlist in resolution_storage.iteritems():
        if host in hostlist:
            return ip

    raise Exception("Failure in resolve something ? %s" % host)


class TrackingResearch:

    def __init__(self, country, test_id, media_kind, media_url, media_ip):

        assert media_ip, "TrackResearch: resolution fail %s" % media_url
        c_code, c_name = ip_to_country_tuple(media_ip)
        self.description = {
            'country': country,
            'media_url': media_url,
            'media_kind': media_kind,
            'media_location': "%s (%s)" % (c_name, c_code),
            'test_id': test_id,
            # remind: test_id and importer_id are the same
        }
        self.company_collection = {}
        self.country_collection = {}

    def add_company(self, company):
        self.company_collection.setdefault(company, 0)
        self.company_collection[company] += 1

    def add_countries(self, country_list):
        for country in country_list:
            self.country_collection.setdefault(country, 0)
            self.country_collection[country] += 1

    def get_numbers(self):
        """
        Return numbers for the class below, PercentageResearch,
        that computer percentages based on the data here stored.
        """
        return self.description['media_kind'], \
               self.country_collection, \
               self.company_collection

    def dump(self, directory):

        complete_data = {
            'info' : self.description,
            'companies' : self.company_collection,
            'countries' : self.country_collection
        }

        destdir = os.path.join(directory, self.description['country'])
        try:
            os.makedirs(destdir)
        except Exception:
            pass

        destfile = os.path.join(destdir, '%d-%s.json' %
                                    ( self.description['test_id'],
                                      self.description['media_kind']) )
        previous = []
        if os.path.isfile(destfile):
            with file(destfile) as f:
                previous = json.load(f)

            os.unlink(destfile)

        previous.append(complete_data)
        with file(destfile, 'w+') as f:
            json.dump(previous, f)


class PercentageResearch:
    """
    The goal of this class is represent the presence of a foreign country
    in the media usage of a target country.
    """

    def _do_dir_join(self, percentdir, fname):
        # useful utility for such
        destdir = os.path.join(percentdir, self.country)
        try:
            os.makedirs(destdir)
        except Exception:
            pass
        return os.path.join(destdir, fname)


    def __init__(self, country, importer_id):

        self.country = country
        self.importer_id = importer_id

        self.media_counter = {
            'global' : 0,
            'national' : 0,
            'local' : 0,
            'blog' : 0
        }

        self.foreign_presence = {
            'global' : {},
            'national' : {},
            'local': {},
            'blog' : {}
        }
        self.company_presence = {
            'global' : {},
            'national' : {},
            'local': {},
            'blog' : {}
        }

        self.country_collector = {}
        self.company_collector = {}


    def add_country_presence(self, media, kind, country_chain):
        if self.foreign_presence[kind].has_key(media):
            self.foreign_presence[kind][media] += country_chain
        else:
            self.foreign_presence[kind].update({ media : country_chain })


    def add_company_presence(self, media, kind, company):

        if not company:
            return

        # this is a single string. so if good the setdefault
        self.company_presence[kind].\
            setdefault(media, []).append(company)


    def add_large_chaotic_info(self, blob):
        """
        blob is:
        (
            'global',
                {
                    None: 51,  u'Europe': 1, u'Australia': 3,
                    u'Singapore': 17, u'Indonesia': 50, u'India': 1,
                    u'United States': 24, u'Asia/Pacific Region': 1,
                    u'Japan': 2, u'Hong Kong': 1, 'Indonesia': 45
                }, {
                    None: 18, u'Google': 11, u'Adobe': 2, u'Nielsen': 1,
                    u'cXense': 1, u'comScore': 1, u'Fairfax Media': 1,
                    u'Chartbeat': 2, u'Fox One Stop Media': 3, u'Amazon.com': 1,
                    u'Skimlinks': 2, u'Optimizely': 2
                }
        )
        """
        self.media_counter[blob[0]] += 1

        for country, entrances in blob[1].iteritems():
            self.country_collector.setdefault(country, 0)
            self.country_collector[country] += entrances

        for company, inclusions in blob[2].iteritems():
            self.company_collector.setdefault(company, 0)
            self.company_collector[company] += inclusions


    def dump_country_presence(self, percentdir):
        """
        The concept is, for every media stock every country you
        pass through, then, after, make computation over the
        media number of section.
        """
        for kind, mediamap in self.foreign_presence.iteritems():

            country_occourrence = {}
            for media, country_chain in mediamap.iteritems():

                for c in country_chain:

                    if country_occourrence.has_key(c):
                        continue

                    # for the country not present in the country_occourrence
                    # iter over all the chains and count
                    media_passing_thru = 0
                    for test_cc_list in mediamap.itervalues():

                        if c in test_cc_list:
                            media_passing_thru += 1
                            # jump to the next media
                            continue

                    country_occourrence.update({c : media_passing_thru})

                # when this loop is completed, next to the other
                # country_chain, looking for more rare country

            clean_kind_content = []
            for country, media_passing_thru in country_occourrence.iteritems():
                clean_kind_content.append({
                    "country" : country,
                    "media_passing_thru" : media_passing_thru,
                    "percentage" : round( 100 *
                                  ( float(media_passing_thru) /
                                    len(mediamap.keys())), 2 )
                })

            clean_kind_content.sort(key=operator.itemgetter('percentage'))

            if not clean_kind_content:
                continue

            dumpf = self._do_dir_join(percentdir,
                                "%d-%s-country-presence.json" % (
                                    self.importer_id, kind
                                ))

            fp = file(dumpf, 'w+')
            json.dump(clean_kind_content, fp)
            fp.close()



    def dump_company_presence(self, percentdir):
        """
        is the same code above, just applied to company list
        """
        for kind, ads_mediamap in self.company_presence.iteritems():

            company_occourrence = {}
            for media, companies_list in ads_mediamap.iteritems():

                for c in companies_list:

                    if company_occourrence.has_key(c):
                        continue

                    # for the company is not present in the company_occourrence
                    # iter over all the chains and count
                    media_passing_thru = 0
                    for test_ads_comp_list in ads_mediamap.itervalues():

                        if c in test_ads_comp_list:
                            media_passing_thru += 1
                            # jump to the next media
                            continue

                    company_occourrence.update({c : media_passing_thru})

                    # when this loop is completed, next to the other
                    # country_chain, looking for more rare country

            clean_kind_content = []
            for company, media_passing_thru in company_occourrence.iteritems():
                clean_kind_content.append({
                    "company" : company,
                    "media_associated_at" : media_passing_thru,
                    "percentage" : round( 100 *
                                          ( float(media_passing_thru) /
                                            len(ads_mediamap.keys())), 2 )
                })

            clean_kind_content.sort(key=operator.itemgetter('percentage'))

            if not clean_kind_content:
                continue

            dumpf = self._do_dir_join(percentdir,
                                      "%d-%s-company-presence.json" % (
                                          self.importer_id, kind
                                      ))

            fp = file(dumpf, 'w+')
            json.dump(clean_kind_content, fp)
            fp.close()


    def dump_large_chaotic_info(self, percentdir):

        destfile = self._do_dir_join(percentdir,
                                     "%d-chaotic_info.json" % self.importer_id)

        summary_dict = {
            'countries_sum' : self.country_collector,
            'companies_sum' : self.company_collector,
            'media_sum' : self.media_counter
        }

        with file(destfile, 'w+') as f:
            json.dump(summary_dict, f)
