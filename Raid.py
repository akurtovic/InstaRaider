"""
Raid.py
Uses instaRaider.py to save last 60 Instagram photo for a specified user

v 0.1
@amirkurtovic
"""
from instaRaider import *
import sys

if (len(sys.argv) != 2):
	print "Useage: ./Raid.py username"
else:
        userName = str(sys.argv[1])

        if(validUser(userName)):
            # Get source code from fully loaded Instagram profile page
            url = getUrl(userName)
            source = loadInstagram(url)
            # Download all photos identified on profile page
            getPhotos(source, userName)
        else:
            print "Username " + userName + " is not valid."