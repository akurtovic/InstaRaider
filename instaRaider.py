#!/usr/bin/env python
"""
insta_raider.py

usage: insta_raider.py [-h] -u USERNAME

@amirkurtovic

"""
import argparse
import logging
import os
import os.path as op
import re
import requests
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
import time
import warnings
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

warnings.filterwarnings("ignore", category=InsecurePlatformWarning)

class PrivateUserError(Exception):
    """Raised if the profile is found to be private"""

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class InstaRaider(object):

    def __init__(self, username, directory, num_to_download=None,
                 log_level='info'):
        self.username = username
        self.profile_url = self.get_url(username)
        self.directory = directory
        self.PAUSE = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        self.html_source = None
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging(self.log_level)
        self.set_num_posts(num_to_download)
        self.setup_webdriver()

    def get_url(self, path):
        return urlparse.urljoin('https://instagram.com', path)

    def set_num_posts(self, num_to_download=None):
        self.num_posts = int(self.get_posts_count(self.profile_url) or 0)
        self.num_to_download = num_to_download

    def setup_logging(self, level=logging.INFO):
        self.logger = logging.getLogger('instaraider')
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def log(self, *strings, **kwargs):
        level = kwargs.pop('level', logging.INFO)
        self.logger.log(level, u' '.join(str(s) for s in strings))

    def setup_webdriver(self):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("general.useragent.override", self.user_agent)
        self.webdriver = webdriver.Firefox(self.profile)
        self.webdriver.set_window_size(480, 320)
        self.webdriver.set_window_position(800, 0)

    def get_posts_count(self, url):
        """
        Given a url to Instagram profile, return number of photos posted
        """
        response = requests.get(url)
        counts_code = re.search(r'\"media":{"count":\d+', response.text)
        if not counts_code:
            return None
        return re.findall(r'\d+', counts_code.group())[0]

    def log_in_user(self):
        driver = self.webdriver
        self.log('You need to login to access this profile.',
                 'Redirecting you to the login page in the browser.',
                 level=logging.WARN)
        driver.get(self.get_url('accounts/login/'))

        # Wait until user has been successfully logged in and redirceted
        # to his/her feed.
        WebDriverWait(driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.-cx-PRIVATE-FeedPage__feed'),
            )
        )

        self.log('User successfully logged in.', level=logging.INFO)
        self.set_num_posts()  # Have to set this again
        driver.get(self.profile_url)

    def load_instagram(self):
        """
        Using Selenium WebDriver, load Instagram page to get page source

        """
        self.log(self.username, 'has', self.num_posts, 'posts on Instagram.')
        if self.num_to_download is not None:
            self.log("The first", self.num_to_download, "of them will be downloaded.")

        num_to_download = self.num_to_download or self.num_posts
        driver = self.webdriver
        # load Instagram profile and wait for PAUSE
        self.log("Loading Instagram profile...")
        driver.get(self.profile_url)
        driver.implicitly_wait(self.PAUSE)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            el = driver.find_element_by_css_selector(
                '.-cx-PRIVATE-ProfilePage__advisoryMessageHeader'
            )
        except NoSuchElementException:
            pass
        else:
            if el.text.lower() == 'this account is private':
                self.log_in_user()

        if (num_to_download > 24):
            scroll_to_bottom = self.get_scroll_count(num_to_download)
            element = driver.find_element_by_css_selector('div.-cx-PRIVATE-AutoloadingPostsGrid__moreLoadingIndicator a')
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
        num_to_download = self.num_to_download or self.num_posts
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
                self.log('Downloaded file {}/{} ({}).'.format(
                    photos_saved, num_to_download, op.basename(photo_name)))
            else:
                self.log('Skipping file', photo_name, 'as it already exists.')

            if photos_saved >= num_to_download:
                break

        self.log('Saved', photos_saved, 'files to', self.directory)


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
