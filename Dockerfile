# Dockerfile for trackmap perform_analysis script
# version 0.1
FROM ubuntu
MAINTAINER Peter van Heusden <pvh@webbedfeet.co.za>
RUN apt-get update
RUN apt-get install -y zip tor git wget traceroute python-pip gcc python-dev libgeoip-dev geoip-database libfontconfig1 unzip
RUN pip install GeoIP tldextract termcolor PySocks
RUN adduser --disabled-password --gecos "Track Map User" trackmap
USER trackmap
WORKDIR /home/trackmap
RUN git clone https://github.com/vecna/trackmap.git
ADD fetch_phantomjs.sh /home/trackmap/trackmap/fetch_phantomjs.sh
WORKDIR /home/trackmap/trackmap
RUN bash -c /home/trackmap/trackmap/fetch_phantomjs.sh
ENTRYPOINT ["./perform_analysis.py"]
