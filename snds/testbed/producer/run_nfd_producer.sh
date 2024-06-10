#!/bin/bash

# Function to check if NFD is running
is_nfd_running() {
    pgrep nfd > /dev/null 2>&1
    return $?
}

# Stop NFD if it is running
if is_nfd_running; then
    echo "NFD is running. Stopping it..."
    nfd-stop
else
    echo "NFD is not running."
fi

# Start NFD as a background process
nfd-start &

# Create an NFD face
nfdc face create udp://mmlab-aueb-1.mmlab.edu.gr

# Add routes
nfdc route add / udp://mmlab-aueb-1.mmlab.edu.gr
nfdc route add /localhop/nfd udp://mmlab-aueb-1.mmlab.edu.gr

# Serve certificates
ndn6-serve-certs --inter --cert-file ~/fotiou.cert

echo "NDN setup commands executed successfully."