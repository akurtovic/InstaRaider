"""
Raid.py
CL tool using instaRaised.py to archive public Instagram photo for a specified user
@amirkurtovic

TODO: 
"""
from instaRaider.py import *
import sys

if (len(sys.argv) != 2):
	print "Useage: ./instaRaider.py username"

# compile URL from argument
url = 'http://instagram.com/' + str(sys.argv[1]) + '/'

# check if Instagram username is valid
req = urllib2.Request(url)
try:
	urllib2.urlopen(req)
except URLError, e:
    print e.code
    print e.read()

# Get source code from fully loaded Instagram profile page
source = loadInstagram(url)

# Download all photos identified on profile page
getPhotos(source)
