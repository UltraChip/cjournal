## CHIP'S JOURNAL (CJOURNAL)
##
## A basic journaling program that allows you to securely write and store
## entries in an encrypted database. Entries can be tagged and searched for
## later.


# IMPORTS AND CONSTANTS
import sqlite3
import os
import time
import json
import getpass
import sys
import logging
import argparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from configManager import loadConfig

confFile = "./journal.conf"


# FUNCTIONS

def makeDB(filename, key):
    # Creates and initializes a new sqlite3 database. Takes in the
    # filename as input. Does not return anything.
    if os.path.exists(filename):
        print("Database already exists - no need to create it.")
        return
    
    db = sqlite3.connect(filename)
    cursor = db.cursor()

    tab_jrn = """CREATE TABLE journal (
                 jid INTEGER PRIMARY KEY,
                 date TEXT,
                 time TEXT,
                 title BLOB,
                 entry BLOB,
                 tags TEXT); """
    # The first record in the table is a special dummy record that holds test
    # text that the program will use to verify that the key is correct.
    keycheck = "INSERT INTO journal (title) VALUES (?);"

    cursor.execute(tab_jrn)
    cursor.execute(keycheck, (encryptor(key, "keycheck"),))
    cursor.close()
    db.commit()
    db.close()
    logging.info("INIT - Database didn't exist, so it was created.")
    return

def initDB(filename, key):
    # Opens the database for use and verifies that the supplied key is correct.
    # Takes in the filename and key as input. Returns the database object.
    if not os.path.exists(filename):
        makeDB(filename, key)
    db = sqlite3.connect(filename)

    cursor = db.cursor()
    cursor.execute("SELECT title FROM journal WHERE jid = 1;")
    ckeycheck = cursor.fetchone()[0]
    cursor.close()
    try:
        keycheck = decryptor(key, ckeycheck)
        if keycheck != "keycheck":
            logging.error("Key is incorrect. Exiting.")
            print("Key is incorrect. Exiting.")
            exit()
    except:
        logging.error("Key validation failed - probably a bad password.")
        print("Key validation failed - probably a bad password.")
        exit()
    logging.info("INIT - Database opened successfully.")
    return db

def decryptor(key, ctext):
    # Decrypts the supplied ciphertext using the supplied key. Returns the
    # plaintext.
    civ = ctext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv=civ)
    ptext = unpad(cipher.decrypt(ctext[AES.block_size:]), AES.block_size)
    return ptext.decode("utf-8")

def encryptor(key, text):
    # Encrypts the supplied plaintext using the supplied key. Returns the
    # ciphertext.
    cipher = AES.new(key, AES.MODE_CBC)
    ctext = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
    civ = cipher.iv
    cipherblock = civ + ctext
    return cipherblock

def commitEntry(db, key, text, tags=[], title="Untitled Entry"):
    # Commits a new entry to the database. Takes in the database object, key,
    # text, and list of tags as input. Returns the record's jid as output.
    cursor = db.cursor()
    if title == "":
        title = "Untitled Entry"
    ctext = encryptor(key, text)
    ctitle = encryptor(key, title)
    dstamp = time.strftime("%Y-%m-%d", time.localtime())
    tstamp = time.strftime("%H:%M", time.localtime())
    for tag in tags:
        tag = tag.upper()
    cursor.execute("INSERT INTO journal (date, time, title, entry, tags) VALUES (?, ?, ?, ?, ?);", (dstamp, tstamp, ctitle, ctext, json.dumps(tags)))
    cursor.execute("SELECT jid FROM journal WHERE date = ? AND time = ?;", (dstamp, tstamp))
    jid = cursor.fetchone()[0]
    cursor.close()
    db.commit()
    return jid

def getEntry(db, key, jid):
    # Gets a specific entry from the database. Takes in the database object,
    # key, and jid as input. Returns the date, time, decrypted entry text, and 
    # tags as a dictionary.
    cursor = db.cursor()
    if jid == "-1":
        cursor.execute("SELECT * FROM journal ORDER BY jid DESC LIMIT 1;")
    else:
        cursor.execute("SELECT * FROM journal WHERE jid = ?;", (jid,))
    entry = cursor.fetchone()
    cursor.close()
    title = decryptor(key, entry[3])
    text = decryptor(key, entry[4])
    tags = json.loads(entry[5])
    return {"jid":entry[0], "date": entry[1], "time": entry[2], "title": title, "text": text, "tags": tags}

def searchEntries(db, key, tag):
    # Searches the database for entries with the specified tag. Takes in the
    # database object, key, and tag as input. Returns a list of jids and titles
    # as output.
    results = []
    tag = tag.upper() if tag != "__all__" else tag
    cursor = db.cursor()
    if tag == "__all__":
        cursor.execute("SELECT jid, date, time, title FROM journal WHERE jid <> 1;")
    else:
        cursor.execute("SELECT jid, date, time, title FROM journal WHERE tags LIKE ?;", (f"%{tag}%",))
    for row in cursor:
        results.append({"jid":row[0], "date":row[1], "time":row[2], "title":decryptor(key, row[3])})
    cursor.close()
    return results

def searchDate(db, key, date):
    # Searches the database for entries with the specified date. Takes in the
    # database object, key, and date as input. Returns a list of jids and titles
    # as output.
    results = []
    cursor = db.cursor()
    cursor.execute("SELECT jid, date, time, title FROM journal WHERE date = ?;", (date,))
    for row in cursor:
        results.append({"jid":row[0], "date":row[1], "time":row[2], "title":decryptor(key, row[3])})
    cursor.close()
    return results

def searchMode(db, key, args):
    # Searches the database for entries with the specified tag or date. Takes in
    # the database object, key, and arguments as input. Returns a list of jids
    # and titles as output.
    if args.date:
        results = searchDate(db, key, args.date)
    elif args.search:
        results = searchEntries(db, key, args.search)
    elif args.all:
        results = searchEntries(db, key, "__all__")
    else:
        results = []
    
    # Print a table of the search results
    if results:
        print(" ID# | Date       | Time  | Title")
        print("-----+------------+-------+--------------------------------")
        for record in results:
            print("{:4d} | {:10s} | {:4s} | {}".format(record["jid"], record["date"], record["time"], record["title"]))
        print("-----+------------+-------+--------------------------------")

        ans = int(input(f"\nSelect # to view (0 to exit): "))
        if ans == 0:
            print("")
            quit()
        else:
            print("")
            viewEntry(db, key, ans)
    return

def viewEntry(db, key, jid):
    # Gets a specific entry from the database and prints it to the screen. Takes
    # in the database object, key, and arguments as input.
    entry = getEntry(db, key, jid)
    print("TITLE: {}".format(entry["title"]))
    print(f"DATE:  {entry['date']}    TIME:  {entry['time']}")
    print("-"*60)
    print(f"ENTRY:\n    {entry['text']}")
    print("-"*60)
    print(f"TAGS:  {', '.join(entry['tags'])}")
    print("")
    return


# INITIALIZATION

# Load the configuration file
conf = loadConfig(confFile)

# Initialize logger
logging.basicConfig(
    level=conf['loglevel'],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(conf['logfile'], mode='a'),])
        #logging.StreamHandler()])
logging.info("INIT - Logger")

# Get arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--title", help="The title of the journal entry.")
parser.add_argument("-e", "--entry", help="The text of the journal entry.")
parser.add_argument("-a", "--tags", help="Add a list of tags, separated by commas.")
parser.add_argument("-d", "--date", help="Search for a journal entry by date.")
parser.add_argument("-s", "--search", help="Search for a journal entry by tag.")
parser.add_argument("-v", "--view", help="View a specific journal entry by number. Use -1 to view the most recent entry.")
parser.add_argument("-l", "--last", action="store_true", help="View the most recent journal entry. Equivalent to -v -1.")
parser.add_argument("--all", action="store_true", help="List all journal entries.")
args = parser.parse_args()

# Get the key
key = getpass.getpass(f"\nWhat's your password?: ").encode("utf-8")
key = key + b"\x00" * (32 - len(key))

db = initDB(conf['dbfile'], key)


# MAIN

print("")
if args.date or args.search or args.all:
    searchMode(db, key, args)
elif args.view or args.last:
    jid = "-1" if args.last else args.view
    viewEntry(db, key, jid)
else:
    if not args.title:
        title = input("What is the title of this entry?: ").title()
    else:
        title = args.title
        title = title.title()

    if not args.entry:
        print("Enter your entry. Press Ctrl+D when finished.")
        text = sys.stdin.read()
    else:
        text = args.entry

    if not args.tags:
        tgs = input(f"\nAny tags? (separate with commas): ")
    else:
        tgs = args.tags
    tgs = tgs.split(",")
    tags = []
    for tag in tgs:
        tag = tag.strip()
        tag = tag.upper()
        tags.append(tag)

    # Commit the entry to the database
    jid = commitEntry(db, key, text, tags, title)
    logging.info(f"Entry recorded as #{jid}.")
    print(f"Entry recorded as #{jid}.")