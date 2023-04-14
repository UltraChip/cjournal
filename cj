#!/bin/bash

## CHIP'S JOURNAL KICKOFF SCRIPT
##
## A simple bash script to help kick off CJournal. Pretty straightforward.

# CONSTANTS
CJOURNAL_PATH="$HOME/.local/bin/cjournal"


# MAIN
pushd $CJOURNAL_PATH > /dev/null
python3 cjournal.py "$@"
popd > /dev/null