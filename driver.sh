#!/bin/bash

#change to the directory of the script
cd "$(dirname "$0")"
#run the desired logic
python main.py "$@"
