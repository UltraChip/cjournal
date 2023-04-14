# CHIP'S JOURNAL (CJOURNAL)

A basic journaling program that allows you to securely write and store entries in an encrypted database. Entries can be tagged and searched for later.

## Requirements
- Some flavor of Linux operating system (tested on Mint 20.3 but will probably work on other distributions too)
- Python 3
- Pycryptodome module from PIP. If you use the automated installer (see below) this should be taken care of for you. 

## Installation
1. Clone or download this repository. Unzip if neccessary.
2. Navigate to the directory containing the repository files. 
3. Run the automated installer using command:

    bash ./install.sh

4. OPTIONAL: If desired, program can be configured by editing the config file located at ~/.local/bin/cjournal/journal.conf. Configuration options are detailed below.

## How to Use - File Creation & Writing Your First Entry
- To write a journal entry, simply use the command:

    cj

- When you run the program for the first time, it will create a new database file and prompt you to set up an encryption password for it. **REMEMBER THIS PASSWORD!** If you ever forget it you will be permanently locked out of your journal FOREVER - the only way to make the program usable again will be to delete the database file and restart your journal from scratch. 
- Follow the prompts to create your first journal entry. 

## How to Use - Reading Previously Created Entries
- To see a listing of all your journal entries, use the command:

    cj --all

- You will be prompted to enter your password and then be presented with a table of all your journal entries. Choose an entry by its ID number to read it. 

- If you already know the ID number of the entry you want to see, you can go straight to it with command:

    cj -v <ID#>

- To automatically read your most recently written entry use command:

    cj -l 

    --or--

    cj --last

    --or--

    cj -v -1

- You will be prompted to enter your password and then be immediately taken to your most recent entry. 

## Searching for Specific Entries
- To search for entries by date, use command:

    cj -d \<YYYY-MM-DD>

- To search for entries by tag, use command:

    cj -s \<tag>

- In either case, you will be prompted to enter your password and then be presented with a list of entries matching your search criteria. Choose an entry to view by its ID number. 

## Backing Up Your Journal
- To automatically back up your journal database use command:

  bkcj

- Backups are stored in the ~/backups/cjournal directory with a date/time stamped file name in the form of:

    19700101-0000_CJournal_Backup.db

- If you ever need to restore a backup you can do so by identifying the latest backup file and copying it to ~/.local/bin/cjournal/journal.db (assuming you are still using the default database configuration, see "Configuration Options" below)
- If you wish, you can add additional backup locations (including network locations reachable over SSH) by editing the "BACKUP_LOCATIONS" variable in ~/.local/bin/bkcj

## Table of Command Line Arguments
| Short |     Long |                                       Description |
|   --: |     ---: |                                              ---: |
|    -t |  --title |                  Specify the title for your entry |
|    -e |  --entry |                       The main body of your entry |
|    -a |   --tags | The list of tags (comma-separated) for your entry |
|    -d |   --date |       Search entries by date in YYYY-MM-DD format |     
|    -s | --search |                             Search entries by tag |
|    -v |   --view |        View a specific journal entry by ID number |
|    -l |   --last |              View the most recently written entry |
|       |    --all |                          List all journal entries | 

## Configuration Options
As a reminder, the configuration file is located in ~/.local/bin/cjournal/journal.conf. It can be altered by any text editor. 

- "dbfile" - The location and name of the database file which stores all journal entries.
- "logfile" - The location and name of the program's log file
- "loglevel" - The verbosity of the log