#!/usr/bin/env python
"""
instaRaider.py

usage: instaRaider.py [-h] -u USER [-c COUNT]

@amirkurtovic

"""
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.common.action_chains import ActionChains
import re
from time import sleep
import urllib
import urllib2
import urlparse
import os
import sys
import argparse
import re

class instaRaider(object):

    def getImageCount(self, url):
        '''
        Given a url to Instagram profile, return number of photos posted
        '''
        response = urllib2.urlopen(url)
        countsCode = re.search(r'\"media":{"count":\d+', response.read())
        count = re.findall(r'\d+', countsCode.group())
        return count[0]

    def loadInstagram(self, profileUrl):
        '''
        Using Selenium WebDriver, load Instagram page to get page source
    
        '''
        count = self.getImageCount(self.profileUrl)
        print self.userName + " has " + str(count) + " photos on Instagram."

        print "Loading Selenium WebDriver..."
        
        # Load webdriver and scale window down
        driver = webdriver.Firefox()

        print "Loading Instagram profile..."
        # load Instagram profile and wait for PAUSE 
        driver.get(self.profileUrl)
        driver.implicitly_wait(self.PAUSE)

        # Check if the profile is private. If so, exit
        try:
            driver.find_element_by_css_selector('.-cx-PRIVATE-Shell__main')
        except:
            sys.exit("User profile is private. Aborting.")

        clicks = (int(count)-60)/20+1

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Load full Instagram profile if more than initial 60 photos desired
        if (args.count < 61):
            pass
        else:
            # Click on "Load more..." label
            print self.loadLabelCssSelector
            element = driver.find_element_by_css_selector(self.loadLabelCssSelector)
            driver.implicitly_wait(self.PAUSE)
            element.click()


            for y in range(clicks):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(self.PAUSE)
                sys.stdout.write('.')
                sys.stdout.flush()
     
        # After load all profile photos, retur source to getPhotos()
        source = driver.page_source
        
        # close Firefox window
        driver.close()

        return source

    def validUser(self, userName):
        '''
        returns True if Instagram username is valid
        '''
        # check if Instagram username is valid
        req = urllib2.Request(self.profileUrl)

        try:
            urllib2.urlopen(req)
        except:
            return False
        # if req doesn't fail, user profile exists
        return True

    def photoExists(self, url):
        '''
        Returns true if photo exists
        Used when checking which suffix Instagram used for full-res photo
        url: URL to Instagram photo
        '''
        try:
            urllib2.urlopen(url)
        except:
            return False
    
        return True


    def getPhotos(self, source, userName, count):
        '''
        Given source code for loaded Instagram page,
        extract all hrefs and download full-resolution photos
    
        source: HTML source code of Instagram profile papge
        '''
        # directory where photos will be saved
        directory = './Images/' + userName + '/'

        # check if directory exists, if not, make it
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # logfile to store urls is csv format
        logfile = './Images/' + userName + '/' + userName + '.csv'
        try:
            file = open(logfile, "a")
        except IOError:
            print "\nLog file does not exist."

        # photo number for file names
        photoNumber = 0
    
        # indexes for progress bar
        photosSaved = 0
        progressBar = 0

    
        print "\nRaiding Instagram..."
        print "Saving photos to " + directory
    
        print "------"
        # print progress bar
        print "Photos saved so far:"
        print "---------10--------20--------30--------40--------50"

        links = re.findall(r'display_src":"[https]+:...[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-]*', source)

        for x in links:

            if (photoNumber >= count):
                break
            else:
                # increment photonumber for next image
                photoNumber += 1
                photoUrl = x[14:]
                photoUrl = photoUrl.replace('\\', '')
                split = urlparse.urlsplit(photoUrl)
                photoName = directory + split.path.split("/")[-1]

                # save full-resolution photo if its new
                if not os.path.isfile(photoName):
                    urllib.urlretrieve(photoUrl, photoName)
                
                # save filename and url to CSV file
                file.write(photoUrl + "," + photoName + "\n")
            
                # print hash to progress bar
                if (photosSaved == 50):
                    photosSaved = 1
                    progressBar += 50
                    sys.stdout.write('\n')
                    sys.stdout.write('#')
                    sys.stdout.flush()
                
                else:
                    # increment progress bar
                    photosSaved += 1
                    sys.stdout.write('#')
                    sys.stdout.flush()
                
                sleep(self.PAUSE)

        print "\n------"
        print "Saved " + str(photoNumber) + " images to " + directory
        
        # close logfile
        file.close()
        print "Saved activity in logfile: " + logfile
    
    
    def __init__(self, userName):
        self.userName = userName
        self.profileUrl = 'http://instagram.com/' + userName + '/'
        self.PAUSE = 1
        self.postCount = "span.-cx-PRIVATE-PostsStatistic__count"
        self.loadLabelCssSelector = "div.-cx-PRIVATE-AutoloadingPostsGrid__moreLoadingIndicator"

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description="InstaRaider")
    parser.add_argument('-u', '--user', help="Instagram username", required=True)
    parser.add_argument('-c', '--count', help="# of photos to download", type=int)
    args = parser.parse_args()
    ready = False

    if (args.user):
        userName = args.user
        raider = instaRaider(userName)

        if(raider.validUser(userName)):
            ready = True
            url = raider.profileUrl
        else:
            print "Username " + userName + " is not valid."

    if (args.count):
        if (args.count > raider.getImageCount(url)):
            count = raider.getImageCount(url)
        else:
            count = args.count
    else:
        count = raider.getImageCount(url)

    if(ready):
        # Get source code from fully loaded Instagram profile page
        source = raider.loadInstagram(url)

        # Download all photos identified on profile page
        raider.getPhotos(source, userName, count)
        
        
