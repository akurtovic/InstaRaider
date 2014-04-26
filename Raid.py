"""
Raid.py
Uses instaRaider.py to save last 60 Instagram photo for a specified user

v 0.1
@amirkurtovic
"""
from instaRaider import *
import sys
import argparse

parser = argparse.ArgumentParser(description="InstaRaider")
parser.add_argument('-u', '--user', help="Instagram username", required=True)
parser.add_argument('-c', '--count', help="# of photos to download. Default/Max: 60", type=int)
args = parser.parse_args()


if (args.user):

    userName = args.user

    if not args.count:
        count = 60
    else: 
        count = args.count
    
    if(validUser(userName)):
        # Get source code from fully loaded Instagram profile page
        url = getUrl(userName)
        source = loadInstagram(url)
        # Download all photos identified on profile page
        getPhotos(source, userName, count)
    else:
        print "Username " + userName + " is not valid."