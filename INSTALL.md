Currently the software is only tested on Ubuntu ( it might work in other distributions, but it is currently untested)

## Ubuntu

Create a directory to store the project files and change directory there:

    wget -c https://raw.githubusercontent.com/vecna/trackmap/master/setup.sh
    bash setup.sh
    cd trackmap-master
    ./perform_analysis.py -c NAMEOFTHECOUNTRYWHICHYOUARECONNECTEDTOINTERNET

This software uses `sudo` to execute some commands, so it will ask for your password when it executes. The project
software is installed in a subdirectory called *trackmap-master*.

If you read "OK" at the end, go to the section [Run the test script](https://github.com/vecna/trackmap#run-the-test-script)

### Ubuntu 14.04 and newer

sudo apt-get update
sudo apt-get install wget unzip traceroute libfontconfig1 python-pip python-requests python-termcolor phantomjs phantomjs
sudo pip install tldextract PySocks


## Debian based systems 

Install some base requirements (run with sudo):

    sudo apt-get update
    sudo apt-get install unzip wget -y
    sudo apt-get install traceroute python-pip python-termcolor python-requests -y
    sudo apt-get install libfontconfig1 -y
    sudo pip install tldextract

And, if you want use Tor to send result, you've also to get 'PySocks' module with pip.
Create one directory to store the project files:

    mkdir trackmap
    cd trackmap

    wget https://github.com/vecna/trackmap/archive/master.zip
    unzip master.zip
    cd trackmap-master
    ./fetch_phantomjs.sh

## Arch Linux

Install the required packages:

    sudo pacman -S unzip wget python2-pip traceroute fontconfig
    sudo pip2 install tldextract termcolor requests

If you want to use Tor at the end to send the results, you'll also need to install the 'PySocks' package with pip.

Create a directory to where you'll store all trackmap files:

    mkdir trackmap
    cd trackmap

    wget https://github.com/vecna/trackmap/archive/master.zip
    unzip master.zip
    cd trackmap-master
    ./fetch_phantomjs.sh

### Run the test script

Change directory to the directory where you installed the test script and run:

    python2 perform_analysis.py -c NAME_OF_YOUR_COUNTRY


## Docker

A [Docker](https://www.docker.com/) image has been created for this tool, using the Dockerfile provided in the directory.

Clone a fresh copy from the repository, build a new image and tag it with `trackmap`:

    docker build -t trackmap github.com/vecna/trackmap

Alternatively the image can be built from a working copy:

    docker build -t trackmap /home/me/src/trackmap

Run the test script:

    docker run -it trackmap -c NAME_OF_YOUR_COUNTRY

