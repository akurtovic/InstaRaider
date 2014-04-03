#!/usr/bin/env python
"""
instaRaider.py

@amirkurtovic

"""

from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import re
from time import sleep
import urllib2

def getImageCount(userName):
    '''
    Given a userName, return number of photos posted to Instagram
    NOTE: Not functional yet
    userName: Instagram username
    '''
    response = urllib2.urlopen(url)

    #fix regular expression to match correct tag
    imageCount = re.search(r'counts\":{\"media\":[^\s<>"]\,' , str(response.read()))

def loadInstagram(url):
    '''
    Using Selenium WebDriver, load Instagram page to get page source
    
    '''
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(3)

    # TODO: Once getImageCount functional, loop to load all images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)
    
    source = BeautifulSoup(driver.page_source)
    return source

def getPhotos(source):
    '''
    Given source code for loaded Instagram page,
    extract all hrefs and download full-resolution photos
    
    source: HTML source code of Instagram profile papge
    '''
    
    for x in source.findAll('li', {'class':'photo'}):

        #extract url to AWS thumbnail from each photo
        rawUrl = re.search(r'url\(\"https?://[^\s<>"]+|www\.[^\s<>"]+', str(x))
        
        #format thumbnail url to lead to full-resolution photo
        photoUrl = str(rawUrl.group())[5:-5] + '8.jpg'

        # print URL of full-resolution photo
        # TODO: Use urllib2 to download photo to folder
        print photoUrl
