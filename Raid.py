"""
Raid.py
Uses instaRaider.py to save Instagram photo for a specified user

v 0.1
@amirkurtovic
"""
from instaRaider import *
import sys
import argparse

parser = argparse.ArgumentParser(description="InstaRaider")
parser.add_argument('-u', '--user', help="Instagram username", required=True)
parser.add_argument('-c', '--count', help="# of photos to download", type=int)
args = parser.parse_args()


if (args.user):
    userName = args.user

    raider = instaRaider(userName)
    url = raider.profileUrl

    if not args.count:
        count = raider.count
    else: 
        count = args.count
    
    if(raider.validUser(userName)):
        # Get source code from fully loaded Instagram profile page
        source = raider.loadInstagram(url)

        # Download all photos identified on profile page
        raider.getPhotos(source, userName, count)
    else:
        print "Username " + userName + " is not valid."
