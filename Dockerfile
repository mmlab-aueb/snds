FROM minindn:latest

# Install required tools
RUN apt-get update && apt-get install -y \
    inotify-tools \
    rsync

RUN cp -n /usr/local/etc/ndn/nfd.conf.sample /usr/local/etc/ndn/nfd.conf

# Set the working directory to /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy your application files
COPY Topology.py ./
COPY ngsild_dir ./ngsild_dir/
COPY producer_dir ./producer_dir/
COPY consumer_dir ./consumer_dir/
COPY scripts_for_nodes_config.yaml ./
COPY snds.py ./

