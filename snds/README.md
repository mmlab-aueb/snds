# Secure Named Data Sharing minindn implementation
This folder includes scripts that setup a simple topology, which can be used for validating NDN application for the SNDS project in the Mini-NDN networking emulation tool, which is a fork of Mininet.

## Run with docker

The image inside the mini-ndn repository must be built. Do not build it from inside the git ``submodule`` rather clone the repo and proceed to build the image using: 


```
docker build -t minindn .
```

The image then can be executed using: 
```
docker run -m 4g --cpus=4 -it --privileged \
       -v /lib/modules:/lib/modules \
       minindn bin/bash
```


To run the local implemenation you can use the ``run_through_docker.sh``: 

```
chmod +x run_through_docker.sh
./run_through_docker
```

The files of the project will be found inside the ``/app/`` folder. You can run ``snds.py`` using: 

```
sudo python snds.py <specify_conf_file_here>
```

Note that sudo is important here. 

You should also run using: 

```
sudo python snds.py <specify_conf_file_here> 2>&1 | tee logs/snds.log
```

To redirect the output to both stdout and stderr's to the snds.log file.

## Run without docker
* Clone the mini-ndn repository (`git clone https://github.com/named-data/mini-ndn`)
* Install mini-ndn by running (`./install.sh`)


In the minindn directory, run `sudo python snds.py `. 
