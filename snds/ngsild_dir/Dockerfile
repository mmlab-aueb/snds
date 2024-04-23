# Use the pre-built mini-NDN image as the base
FROM ghcr.io/named-data/mini-ndn:master


WORKDIR app 

# These are used inside the http_ngsild_proxy.py
COPY closestCDNNode_byID.py /app/
COPY closestCDNNode_byType.py /app/

COPY http_ngsild_proxy.py /app/

