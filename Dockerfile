# Dockerfile for helpagainsttrack perform_analysis script
# version 0.1
FROM ubuntu
MAINTAINER Peter van Heusden <pvh@webbedfeet.co.za>
RUN apt-get install -y tor git wget torsocks traceroute python-pip gcc python-dev libgeoip-dev geoip-database libfontconfig1 unzip
RUN pip install GeoIP tldextract termcolor
RUN adduser --disabled-password --gecos "Track Map User" trackmap
USER trackmap
WORKDIR /home/trackmap
RUN git clone https://github.com/vecna/helpagainsttrack.git
ADD fetch_phantomjs.sh /home/trackmap/helpagainsttrack/fetch_phantomjs.sh
WORKDIR /home/trackmap/helpagainsttrack
RUN bash -c /home/trackmap/helpagainsttrack/fetch_phantomjs.sh
ENTRYPOINT ["./perform_analysis.py"]