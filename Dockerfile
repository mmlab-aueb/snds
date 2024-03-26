# Use the pre-built mini-NDN image as the base
FROM minindn:latest


WORKDIR app 

COPY Topology.py ./
COPY ngsild_dir ./ngsild_dir/

# Make sure to import main script last as its that will probably change
COPY snds.py ./

