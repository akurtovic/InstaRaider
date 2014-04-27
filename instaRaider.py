#!/usr/bin/env python
"""
instaRaider.py

@amirkurtovic

"""

from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import re
from time import sleep
import urllib
import urllib2
import os
import sys

PAUSE = 1

def getImageCount(url):
    '''
    Given a url to Instagram profile, return number of photos posted
    '''
    response = urllib2.urlopen(url)
    countsCode = re.search(r'counts\":{\"media\":\d+', response.read())
    count = re.findall(r'\d+', countsCode.group())
    return count[0]

def loadInstagram(url):
    '''
    Using Selenium WebDriver, load Instagram page to get page source
    
    '''
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(PAUSE)

    print "Loading Instagram profile...."
    count = getImageCount(url)
    print "Found " + str(count) + " photos."
    clicks = (int(count)-60)/20+1

    for x in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(PAUSE)
    
    # Click on "Load more..." label
    element = driver.find_element_by_xpath("//html/body/span/div/div/div/section/div/span/a/span[2]/span/span")

    for y in range(clicks):
        element.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(PAUSE)
     
    # After load all profile photos, retur source to getPhotos()
    source = BeautifulSoup(driver.page_source)
    return source

def getUrl(userName):
    '''
    returns profile url for Instagram username
    '''
    # compile URL from argument
    url = 'http://instagram.com/' + userName + '/'
    return url

def validUser(userName):
    '''
    returns True if Instagram username is valid
    '''
    url = getUrl(userName)
    # check if Instagram username is valid
    req = urllib2.Request(url)

    try:
        urllib2.urlopen(req)
    except:
        return False
    
    # if req doesn't fail, user profile exists
    return True

def photoExists(url):
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


def getPhotos(source, userName, count):
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

    photoNumber = 0
    print "\nRaiding Instagram..."
    print "Saving photos to " + directory
    print "------"
    
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
            fullResSuffixes = ['7.jpg', '8.jpg', 'n.jpg']
            for item in fullResSuffixes:
                url = photoUrl + item
                if(photoExists(url)):
                    suffix = item
    
            photoUrl = str(rawUrl.group())[5:-5] + suffix
            photoName = directory + userName + "_" + str(photoNumber) + '.jpg'

            # save full-resolution photo
            urllib.urlretrieve(photoUrl, photoName)
            sys.stdout.write('#')
            sys.stdout.flush()
            sleep(PAUSE)

    print "\n------"
    print "Saved " + str(photoNumber) + " images to " + directory
