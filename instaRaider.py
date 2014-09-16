#!/usr/bin/env python
"""
instaRaider.py

usage: instaRaider.py [-h] -u USER [-c COUNT]

@amirkurtovic

TEST

"""
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import re
from time import sleep
import urllib
import urllib2
import os
import sys
import argparse

class instaRaider(object):

    def getImageCount(self, url):
        '''
        Given a url to Instagram profile, return number of photos posted
        '''
        response = urllib2.urlopen(url)
        countsCode = re.search(r'counts\":{\"media\":\d+', response.read())
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
        driver.set_window_size(40,40)
        driver.set_window_position(20,20)
        
        # load Instagram profile and wait for PAUSE 
        driver.get(self.profileUrl)
        driver.implicitly_wait(self.PAUSE)

        print "Loading Instagram profile..."

        clicks = (int(count)-60)/20+1

        for x in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(self.PAUSE)
    
        # Load full Instagram profile if more than initial 60 photos desired
        if (args.count < 61):
            pass
        else:
            # Click on "Load more..." label
            element = driver.find_element_by_xpath(self.loadLabelXPATH)

            for y in range(clicks):
                element.click()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sys.stdout.write('.')
                sys.stdout.flush()
                sleep(self.PAUSE)
     
        # After load all profile photos, retur source to getPhotos()
        source = BeautifulSoup(driver.page_source)
        
        # close Firefox window
        driver.close()

        return source

    def validUser(self, userName):
        '''
        returns True if Instagram username is valid
        '''
        valid = True
        # check if Instagram username is valid
        req = urllib2.Request(self.profileUrl)

        try:
            urllib2.urlopen(req)
        except:
            valid = False
        # if req doesn't fail, user profile exists
        return valid

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

    
        for x in source.findAll('li', {'class':'photo'}):
    
            if (photoNumber >= count):
                break
            else:
                # increment photonumber for next image
                photoNumber += 1
            
                #extract url to thumbnail from each photo
                rawUrl = re.search(r'url\(\"https?://[^\s<>"]+|www\.[^\s<>"]+', str(x))
    
                # format thumbnail url to lead to full-resolution photo
                # Instagram full-res URLs end in suffixes stored in fullResSuffixes list
                photoUrl = str(rawUrl.group())[5:-5]
                suffix = ''
                for item in self.fullResSuffixes:
                    url = photoUrl + item
                    if(self.photoExists(url)):
                        suffix = item
    
                photoUrl = str(rawUrl.group())[5:-5] + suffix
                photoName = directory + userName + "_" + str(photoNumber) + '.jpg'

                # save full-resolution photo
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
        self.fullResSuffixes = ['7.jpg', '8.jpg', 'n.jpg']
        self.PAUSE = 1
        self.loadLabelXPATH = "/html/body/div/div/div/section/div/span/a/span[2]/span/span"

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description="InstaRaider")
    parser.add_argument('-u', '--user', help="Instagram username", required=True)
    parser.add_argument('-c', '--count', help="# of photos to download", type=int)
    args = parser.parse_args()

    if (args.user):
        userName = args.user

        raider = instaRaider(userName)
        url = raider.profileUrl

        if not args.count:
            count = raider.getImageCount(url)
        else:
            count = args.count
            if raider.getImageCount(url) < count:
                print "You want to dowload %r photos." % args.count
                print "The user only has %r photo." % raider.getImageCount(url)
                print "Downloading all photos."
                count = raider.getImageCount(url)
            
        
        if(raider.validUser(userName)):
            # Get source code from fully loaded Instagram profile page
            source = raider.loadInstagram(url)

            # Download all photos identified on profile page
            raider.getPhotos(source, userName, count)
        else:
            print "Username " + userName + " is not valid."
        