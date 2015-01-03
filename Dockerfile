# Dockerfile for trackmap perform_analysis script
# version 0.1
FROM ubuntu:trusty
MAINTAINER Peter van Heusden <pvh@webbedfeet.co.za>
RUN apt-get update && apt-get install -y \
    libfontconfig1 \
    python-pip \
    traceroute \
    unzip \
    wget \
    zip
RUN pip install \
    PySocks \
    termcolor \
    tldextract
RUN adduser --disabled-password --gecos "Track Map User" trackmap
COPY . /home/trackmap/trackmap
RUN chown -R trackmap:trackmap /home/trackmap/trackmap
USER trackmap
WORKDIR /home/trackmap/trackmap
RUN bash -c /home/trackmap/trackmap/fetch_phantomjs.sh
ENTRYPOINT ["./perform_analysis.py"]
