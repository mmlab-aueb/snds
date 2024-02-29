# Use the pre-built mini-NDN image as the base
FROM ghcr.io/named-data/mini-ndn:master


WORKDIR app 

COPY snds.py /app/
COPY snds-topology.conf /app/

