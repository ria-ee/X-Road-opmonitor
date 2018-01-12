#!/bin/bash

# Check if server list update is necessary
if [[ $# -eq 1 ]] ; then
    python3 -m collector_module.update_servers
fi

# Run collector
python3 -m collector_module.collector
