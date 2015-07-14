#!/usr/bin/env python
"""
instaRaider.py

usage: instaRaider.py [-h] -u USERNAME

@amirkurtovic

"""
import selenium.webdriver as webdriver
import time
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
        print self.userName + " has " + str(count) + " posts on Instagram."
        
        # Load webdriver
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
        driver = webdriver.Firefox(profile)
        driver.set_window_size(480, 320)
        driver.set_window_position(800, 0)

        print "Loading Instagram profile..."
        # load Instagram profile and wait for PAUSE 
        driver.get(self.profileUrl)
        driver.implicitly_wait(self.PAUSE)

        # Check if the profile is private. If so, exit
        try:
            driver.find_element_by_css_selector('.-cx-PRIVATE-Shell__main')
        except:
            sys.exit("User profile is private. Aborting.")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        if (int(count) > 24):
            scrollToBottom = self.getScrollCount(count)
            element = driver.find_element_by_css_selector(self.loadLabelCssSelector)
            driver.implicitly_wait(self.PAUSE)
            element.click()

            for y in range(scrollToBottom):
                self.scrollPage(driver)
     
        # After load all profile photos, retur source to getPhotos()
        time.sleep(1)
        source = driver.page_source
        
        # close Firefox window
        driver.close()

        return source

    def scrollPage(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        driver.execute_script("window.scrollTo(0, 0);")


    def getScrollCount(self, count):
        return (int(count)-24)/12+1

    def isValidUser(self, userName):
        '''
        returns True if Instagram username is valid
        '''
        req = urllib2.Request(self.profileUrl)

        try:
            urllib2.urlopen(req)
        except:
            return False
        return True

    def printProgressBar(self, directory):
        print "Saving photos to " + directory
        print "------"
        print "Photos saved so far:"
        print "---------10--------20--------30--------40--------50"

    def updateProgressBar(self, photosSaved):
        if (photosSaved % 50 == 0):
            sys.stdout.write('#')
            sys.stdout.write('\n')
            sys.stdout.flush()
        
        else:
            sys.stdout.write('#')
            sys.stdout.flush()

    def getLogfile(self, userName):
        logfile = './Images/' + userName + '/' + userName + '.csv'
        try:
            file = open(logfile, "a")
        except IOError:
            print "\nError trying to open log file."

        return file

    def savePhoto(self, photoUrl, photoName):
        imageRequest = urllib2.Request(photoUrl, headers=self.header)
        imageData = urllib2.urlopen(imageRequest).read()
        output = open(photoName,'wb')
        output.write(imageData)
        output.close()

    def getPhotos(self, source, userName):
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
        logfile = self.getLogfile(userName)
    
        # index for progress bar
        photosSaved = 0
        self.printProgressBar(directory)

        links = re.findall(r'src="[https]+:...[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-].jpg', source)

        for x in links:
            photoUrl = x[5:]
            photoUrl = photoUrl.replace('\\', '')
            split = urlparse.urlsplit(photoUrl)
            photoName = directory + split.path.split("/")[-1]

            # save full-resolution photo if its new
            if not os.path.isfile(photoName):
                self.savePhoto(photoUrl, photoName)
                photosSaved += 1
                self.updateProgressBar(photosSaved);
            
            # save filename and url to CSV file
            logfile.write(photoUrl + "," + photoName + "\n")
            
        print "\n------"
        print "Saved " + str(photosSaved) + " new images to " + directory
        
        # close logfile
        logfile.close()
    
    def __init__(self, userName):
        self.userName = userName
        self.profileUrl = 'http://instagram.com/' + userName + '/'
        self.PAUSE = 1
        self.postCount = "span.-cx-PRIVATE-PostsStatistic__count"
        self.loadLabelCssSelector = "div.-cx-PRIVATE-AutoloadingPostsGrid__moreLoadingIndicator a"
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.header = { 'User-Agent' : self.user_agent }

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description="InstaRaider")
    parser.add_argument('-u', '--user', help="Instagram username", required=True)
    args = parser.parse_args()
    ready = False

    if (args.user):
        userName = args.user
        raider = instaRaider(userName)

        if(raider.isValidUser(userName)):
            ready = True
            url = raider.profileUrl
        else:
            print "Username " + userName + " is not valid."

        count = raider.getImageCount(url)

    if(ready):
        # Get source code from fully loaded Instagram profile page
        source = raider.loadInstagram(url)

        # Download all photos identified on profile page
        raider.getPhotos(source, userName)
