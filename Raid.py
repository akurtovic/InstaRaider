"""
Raid.py
CL tool using instaRaider.py to archive public Instagram photo for a specified user
@amirkurtovic
"""
from instaRaider import *
import sys

if (len(sys.argv) != 2):
	print "Useage: ./Raid.py username"
else:
        userName = str(sys.argv[1])
        
        # compile URL from argument
        url = 'http://instagram.com/' + userName + '/'
        
        # check if Instagram username is valid
        req = urllib2.Request(url)

        validUser = True
        try:
            urllib2.urlopen(req)
        except:
            print "Could not find the Instagram user"
            validUser = False

        if(validUser):
            # Get source code from fully loaded Instagram profile page
            source = loadInstagram(url)
            # Download all photos identified on profile page
            getPhotos(source, userName)
