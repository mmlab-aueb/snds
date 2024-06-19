# run_nfd_producer.sh
#!/bin/bash

LOGFILE="./nfd_producer.log"
CONFIG_FILE="producer.conf"

# Truncate the logfile at the start
: > $LOGFILE

# Read configurations from the config file
echo "Reading configuration from $CONFIG_FILE..." | tee -a $LOGFILE
prefix=$(grep 'prefix' $CONFIG_FILE | awk -F '=' '{print $2}')
certificate_file=$(grep 'certificate_file' $CONFIG_FILE | awk -F '=' '{print $2}')
nfd_url=$(grep 'nfd_url' $CONFIG_FILE | awk -F '=' '{print $2}')
echo "Configuration read: prefix=$prefix, certificate_file=$certificate_file, nfd_url=$nfd_url" | tee -a $LOGFILE

# Function to check if NFD is running
is_nfd_running() {
    pgrep -x nfd > /dev/null 2>&1
    return $?
}

# Stop NFD if it is running
if is_nfd_running; then
    echo "$(date): NFD is running. Stopping it..." | tee -a $LOGFILE
    sudo nfd-stop | tee -a $LOGFILE
    sleep 2  # Wait a bit for NFD to stop
    if is_nfd_running; then
        echo "$(date): Failed to stop NFD." | tee -a $LOGFILE
        exit 1
    else
        echo "$(date): NFD stopped successfully." | tee -a $LOGFILE
    fi
else
    echo "$(date): NFD is not running." | tee -a $LOGFILE
fi

# Start NFD as a background process and wait for it to be ready
echo "$(date): Starting NFD..." | tee -a $LOGFILE
sudo nfd-start | tee -a $LOGFILE &
sleep 2  # Wait a bit for NFD to start

# Check if NFD started successfully
if is_nfd_running; then
    echo "$(date): NFD started successfully." | tee -a $LOGFILE
else
    echo "$(date): Failed to start NFD." | tee -a $LOGFILE
    exit 1
fi

# Create an NFD face
echo "$(date): Creating NFD face..." | tee -a $LOGFILE
if nfdc face create udp://$nfd_url | tee -a $LOGFILE; then
    echo "$(date): NFD face created successfully." | tee -a $LOGFILE
else
    echo "$(date): Failed to create NFD face." | tee -a $LOGFILE
    exit 1
fi

# Add routes
echo "$(date): Adding routes..." | tee -a $LOGFILE
if nfdc route add / udp://$nfd_url | tee -a $LOGFILE; then
    echo "$(date): Route to / added successfully." | tee -a $LOGFILE
else
    echo "$(date): Failed to add route to /." | tee -a $LOGFILE
    exit 1
fi

if nfdc route add /localhop/nfd udp://$nfd_url | tee -a $LOGFILE; then
    echo "$(date): Route to /localhop/nfd added successfully." | tee -a $LOGFILE
else
    echo "$(date): Failed to add route to /localhop/nfd." | tee -a $LOGFILE
    exit 1
fi

# Serve certificates
echo "$(date): Serving certificates..." | tee -a $LOGFILE
if ndn6-serve-certs --inter --cert-file $certificate_file | tee -a $LOGFILE; then
    echo "$(date): Certificates served successfully." | tee -a $LOGFILE
else
    echo "$(date): Failed to serve certificates." | tee -a $LOGFILE
    exit 1
fi

echo "$(date): NDN setup commands executed successfully." | tee -a $LOGFILE
