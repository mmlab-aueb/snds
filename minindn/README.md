# Secure Named Data Sharing minindn implementation
This folder includes scripts that setup a simple topology, which can be used for validating NDN application for the SNDS project in the Mini-NDN networking emulation tool, which is a fork of Mininet.

## Prerequisites 
* Clone the mini-ndn repository (`git clone https://github.com/named-data/mini-ndn`)
* Install mini-ndn by running (`./install.sh`)

## Execution
In the minindn directory, run `sudo python3 snds.py snds-topology.conf`. Then, in the `mini-ndn>` command prompt run `xterm consumer producer ngsild forwarder`.
In the xterm of `producer` run: 
```
export HOME=/tmp/minindn/producer
python3 SNDS_r_service.py
```
In the xterm of `consumer` run:
```
export HOME=/tmp/minindn/consumer
python3 SNDS_service.py
```
In the xterm of `ngsild` run:
```
python3 http_ngsild_proxy.py
```
In the xterm of `forwarder` run:
```
python3 client.py
```
