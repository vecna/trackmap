
## Collects output from other countries
   
    git clone https://github.com/vecna/helpagainsttrack.git
    cd helpagainsttrack
    ./setup_requirements.sh
    ./perform_analysis.py media_lists/germany

At the moment only few country news media lists are available. 

# Output collected

### URL included 

the script **perform\_analysis.py** make connection with phantomjs at all the hosts related to the
country under test. Save the URL of the included scripts. 

They are saved in output/*$MEDIA\_NAME*/\_\_urls

### TLD domain analysis

for every included script domain, are splitted subdoman.domanin.tld, and are stored in output/domain.info in Pickle format

### Traceroute analysis

in output/traceroutes/*$MEDIA\_NAME*\_countries.pickle has the country code of the HOP list (Pickle)
in outout/traceroutes/*$MEDIA\_NAME*\_ip.pickle there are the list of HOP (Pickle)

### debug logs

In output/phantom.log is collected the output of all the phantomjs execution
In output/traceoutput.log is collected the output of all the traceroute executed


## Vagrant setup

### Still not functional and probably never !?

    vagrant box add precise64 http://files.vagrantup.com/precise64.box
    vagrant box add trusty http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box

