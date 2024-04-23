FROM minindn:latest

# Install required tools
RUN apt-get update && apt-get install -y \
    inotify-tools \
    rsync \
    tree  \
    screen

RUN cp -n /usr/local/etc/ndn/nfd.conf.sample /usr/local/etc/ndn/nfd.conf


# Set the working directory to /app
WORKDIR /app

COPY ./pyproject.toml ./

# Copy your application files
COPY ./snds/testbed.conf ./snds/
COPY ./snds/http_utils ./snds/http_utils
COPY ./snds/Topology.py ./snds/
COPY ./snds/ngsild_dir ./snds/ngsild_dir/
COPY ./snds/producer_dir ./snds/producer_dir/
COPY ./snds/forwarder_dir ./snds/forwarder_dir/
COPY ./snds/consumer_dir ./snds/consumer_dir/
COPY ./snds/scripts_for_nodes_config.yaml ./snds
COPY ./snds/snds_main.py ./snds
COPY ./snds/__init__.py ./snds

# Install dependencies using pip and the pyproject.toml file
RUN pip install --upgrade pip \
    && pip install build \
    && python -m build --wheel \
    && pip install --editable .

# Set PYTHONPATH to include the /snds directory
ENV PYTHONPATH="./snds:${PYTHONPATH}"


