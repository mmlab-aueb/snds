# Use the pre-built mini-NDN image as the base
FROM minindn:latest


WORKDIR app 

COPY Topology.py ./
COPY snds.py ./

