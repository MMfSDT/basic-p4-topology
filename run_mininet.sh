#!/bin/bash

# A lot of things came from this guy.
# https://github.com/p4lang/tutorials/blob/master/SIGCOMM_2015/source_routing/run_demo.sh

# Compile the P4 code to JSON.
p4c-bmv2 simple_router.p4 --json ./router/simple_router.json 

# Start the router up.
# sudo ./router/simple_router

# Start the topology script.
sudo python topo.py --behavioral-exe ./router/simple_router --json ./router/simple_router.json --cli ./tools/runtime_CLI.py