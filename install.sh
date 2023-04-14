#!/bin/bash

## CHIP'S JOURNAL INSTALL SCRIPT
##
## A simple bash script to help install CJournal. Pretty straightforward.

# CONSTANTS
CJOURNAL_PATH="$HOME/.local/bin/cjournal"
COMMAND_PATH="$HOME/.local/bin"
BACKUP_PATH="$HOME/backups/cjournal"


# MAIN

# Create directories if they don't exist
if [ ! -d "$CJOURNAL_PATH" ]; then
    mkdir -p "$CJOURNAL_PATH"
fi
if [ ! -d "$BACKUP_PATH" ]; then
    mkdir -p "$BACKUP_PATH"
fi

# Copy the files
rsync -r --progress ./* "$CJOURNAL_PATH/"
cp "$CJOURNAL_PATH/cj" "$COMMAND_PATH/cj"
cp "$CJOURNAL_PATH/bkcj" "$COMMAND_PATH/bkcj"

# Make the files executable
chmod +x "$COMMAND_PATH/cj"
chmod +x "$COMMAND_PATH/bkcj"

# Install dependencies
pip3 install pycryptodome

# Delete uneccessary files
rm -rf "$CJOURNAL_PATH/venv"
rm -rf "$CJOURNAL_PATH/__pycache__"
rm -rf "$CJOURNAL_PATH/.git"
rm -rf "$CJOURNAL_PATH/.gitignore"
rm -rf "$CJOURNAL_PATH/*.db"
rm -rf "$CJOURNAL_PATH/*.log"
rm -rf "$CJOURNAL_PATH/*.code-workspace"