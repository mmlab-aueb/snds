#!/bin/bash

HOSTNAME=$1
TYPE=$2

export HOME=/tmp/minindn/$HOSTNAME 
python3 /home/minindn/snds/minindn/SNDS_r_service.py $TYPE & #> /tmp/minindn/${HOSTNAME}_r.txt & 
python3 /home/minindn/snds/minindn/http_ngsild_proxy.py & #> /tmp/minindn/${HOSTNAME}_proxy.txt & 