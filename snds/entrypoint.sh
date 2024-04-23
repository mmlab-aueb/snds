#!/bin/bash
# Start NFD
service nfd start

# Execute the passed command
exec "$@"
