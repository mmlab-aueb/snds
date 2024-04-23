#!/bin/bash
docker build -t snds .

# Stop the container if it's running
docker stop snds-app || true  # The `|| true` ensures that the script continues even if this command fails (e.g., if the container is not found).

docker rm -f snds-app  # Remove the existing container if it exists

# create the logs directory if it doesn't exist
mkdir -p ./snds/logs

#Run interactive shell session
docker run -m 4g --cpus=4 -it --privileged \
  --env-file .env \
  -v /lib/modules:/lib/modules \
  -v ./snds/logs:/app/snds/logs \
  --name snds-app \
  snds \
  /bin/bash

#Run without interactive shell
#docker run -m 4g --cpus=4 --privileged \
#  --env-file .env \
#  -v /lib/modules:/lib/modules \
#  -v ./logs:/mini-ndn/app/ \
#  --name snds-app \
#  snds \
#  sudo python snds.py
