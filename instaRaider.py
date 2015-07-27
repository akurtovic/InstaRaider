#!/usr/bin/env python
"""
insta_raider.py

usage: insta_raider.py [-h] -u USERNAME

@amirkurtovic

"""
from __future__ import print_function
import argparse
import os
import os.path as op
import re
import requests
import time
import selenium.webdriver as webdriver
import logging


class PrivateUserError(Exception):
    """Raised if the profile is found to be private"""

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class InstaRaider(object):

    def __init__(self, username, directory, num_to_download=None,
                 log_level='info'):
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging(self.log_level)
        self.username = username
        self.profile_url = 'http://instagram.com/{}/'.format(username)
        self.directory = directory
        self.num_posts = self.get_posts_count(self.profile_url)
        self.num_to_download = num_to_download or self.num_posts
        self.PAUSE = 1
        self.postCount = "span.-cx-PRIVATE-PostsStatistic__count"
        self.load_label_css_selector = "div.-cx-PRIVATE-AutoloadingPostsGrid__moreLoadingIndicator a"
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        self.html_source = None

    def setup_logging(self, level=logging.INFO):
        self.logger = logging.getLogger('instaraider')
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def log(self, *strings, **kwargs):
        level = kwargs.pop('level', logging.INFO)
        self.logger.log(level, u' '.join(str(s) for s in strings))

    def get_posts_count(self, url):
        """
        Given a url to Instagram profile, return number of photos posted
        """
        response = requests.get(url)
        counts_code = re.search(r'\"media":{"count":\d+', response.text)
        if not counts_code:
            return None
        return re.findall(r'\d+', counts_code.group())[0]

    def load_instagram(self):
        """
        Using Selenium WebDriver, load Instagram page to get page source

        """
        self.log(self.username, 'has', self.num_posts, 'posts on Instagram.')
        if self.num_posts != self.num_to_download:
            self.log("The first", self.num_to_download,
                     "of them will be downloaded.")

        # Load webdriver
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
        driver = webdriver.Firefox(profile)
        driver.set_window_size(480, 320)
        driver.set_window_position(800, 0)

        self.log("Loading Instagram profile...")
        # load Instagram profile and wait for PAUSE
        driver.get(self.profile_url)
        driver.implicitly_wait(self.PAUSE)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if (int(self.num_to_download) > 24):
            scroll_to_bottom = self.get_scroll_count(self.num_to_download)
            element = driver.find_element_by_css_selector(self.load_label_css_selector)
            driver.implicitly_wait(self.PAUSE)
            element.click()

            for y in range(int(scroll_to_bottom)):
                self.scroll_page(driver)

        # After load all profile photos, retur, source to download_photos()
        time.sleep(1)
        source = driver.page_source

        # close Firefox window
        driver.close()

        return source

    def scroll_page(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        driver.execute_script("window.scrollTo(0, 0);")

    def get_scroll_count(self, count):
        return (int(count) - 24) / 12 + 1

    def validate(self):
        """
        returns True if Instagram username is valid
        """
        req = requests.get(self.profile_url)

        try:
            req.raise_for_status()
        except:
            self.log('User', self.username, 'is not valid.',
                     level=logging.ERROR)
            return False

        if '"is_private":true' in req.text:
            self.log("User profile is private.", level=logging.ERROR)
            return False

        if not self.num_posts:
            self.log('User', self.username, 'has no photos to download.',
                     level=logging.ERROR)
            return False
        return True

    def save_photo(self, photo_url, photo_name):
        image_request = requests.get(photo_url, headers=self.headers)
        image_data = image_request.content
        with open(photo_name, 'wb') as fp:
            fp.write(image_data)

    def download_photos(self):
        """
        Given source code for loaded Instagram page,
        extract all hrefs and download full-resolution photos

        source: HTML source code of Instagram profile papge
        """

        if self.html_source is None:
            self.html_source = self.load_instagram()

        # check if directory exists, if not, make it
        if not op.exists(self.directory):
            os.makedirs(self.directory)

        # index for progress bar
        photos_saved = 0
        self.log("Saving photos to", self.directory)

        links = re.findall(r'src="[https]+:...[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-]*..[\/\w \.-].jpg', self.html_source)

        for link in links:
            photo_url = link[5:]
            photo_url = photo_url.replace('\\', '')
            split = urlparse.urlsplit(photo_url)
            photo_name = op.join(self.directory, split.path.split("/")[-1])

            # save full-resolution photo if its new
            if not op.isfile(photo_name):
                self.save_photo(photo_url, photo_name)
                photos_saved += 1
                self.log(photos_saved, 'out of', self.num_to_download, 'saved.')

                self.log('Downloaded', photo_url, op.basename(photo_name))
            else:
                self.log('File', photo_name, 'already exists.')

            if self.num_to_download and photos_saved >= self.num_to_download:
                    break

        self.log('Saved', photos_saved, 'images to', self.directory)


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='InstaRaider')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('directory', help='Where to save the images')
    parser.add_argument('-n', '--num-to-download',
                        help='Number of posts to download', type=int)
    parser.add_argument('-l', '--log-level', help="Log level", default='info')
    args = parser.parse_args()
    username = args.username
    directory = op.expanduser(args.directory)

    raider = InstaRaider(username, directory,
                         num_to_download=args.num_to_download,
                         log_level=args.log_level)

    if not raider.validate():
        return

    raider.download_photos()


if __name__ == '__main__':
    main()
