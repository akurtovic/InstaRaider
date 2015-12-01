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
import email.utils as eut
import requests
import calendar
try:
    from requests.packages.urllib3.exceptions import InsecurePlatformWarning
except ImportError:
    from urllib3.exceptions import InsecurePlatformWarning
import time
import warnings
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime
try:
    from gi.repository import GExiv2
except ImportError:
    GExiv2 = None

warnings.filterwarnings("ignore", category=InsecurePlatformWarning)

class PrivateUserError(Exception):
    """Raised if the profile is found to be private"""

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class InstaRaider(object):

    def __init__(self, username, directory, num_to_download=None,
                 log_level='info', use_metadata=False):
        self.username = username
        self.profile_url = self.get_url(username)
        self.directory = directory
        self.PAUSE = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        self.html_source = None
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging(self.log_level)
        self.use_metadata = use_metadata
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
        return image_request.headers

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

        links = self.find_links()

        for link in links:
            photo_url = link['display_src']
            photo_url = photo_url.replace('\\', '')
            photo_url = re.sub(r'/s\d+x\d+/', '/', photo_url)
            caption = link.get('caption')
            date_time = link.get('date_time')
            photo_basename = op.basename(photo_url)
            photo_name = op.join(self.directory, photo_basename)

            # save full-resolution photo if its new
            if not op.isfile(photo_name):
                headers = self.save_photo(photo_url, photo_name)
                photos_saved += 1
                self.log('Downloaded file {}/{} ({}).'.format(
                    photos_saved, num_to_download, photo_basename))
                # put info from Instagram post into image metadata
                if self.use_metadata:
                    self.add_metadata(photo_name, caption, date_time)
                if "last-modified" in headers:
                    modtime = calendar.timegm(eut.parsedate(headers["last-modified"]))
                    os.utime(photo_name, (modtime, modtime))
            else:
                self.log('Skipping file', photo_name, 'as it already exists.')

            if photos_saved >= num_to_download:
                break

        self.log('Saved', photos_saved, 'files to', self.directory)

    def find_links(self):
        """
        Find all image urls/metadata in html_source.

        Returns a list of dicts.
        e.g., [{'display_src': 'http://image.url',
                'caption': 'some text from Instagram post',
                'date_time': '1448420058.0'},
               {...},]
        'display_src' must be present in each dict;
            the other keys are optional.
        """
        photos = []
        if self.use_metadata:
            if not GExiv2:
                self.use_metadata = False
                self.log('GExiv2 python module not found.',
                         'Images will not be tagged.')
        try:
            json_data = re.search(r'(?s)<script [^>]*>window\._sharedData'
                                  r'.*?"nodes".+?</script>',
                                  self.html_source)
            json_data = re.search(r'{.+}', json_data.group(0))
            json_data = json.loads(json_data.group(0))
            photos = list(gen_dict_extract('nodes', json_data))[0]
            # find profile_pic
            profile_pic = list(gen_dict_extract('profile_pic_url', json_data))
            if profile_pic:
                # todo (possible):
                #   add a key in the dict to indicate this is profile_pic.
                #   then we could also name the file "profile.jpg" or similar
                #   and also not include it in photos_saved so if user
                #   uses -n N to download some number of images, he still gets
                #   the first N images rather than N-1 images plus
                #   profile_pic
                profile_pic = [{'display_src': p} for p in profile_pic[:1]]
                photos = profile_pic + photos
        except:
            if self.use_metadata:
                self.use_metadata = False
                self.log('Could not find any image metadata.',
                         'Photos will not be tagged.')
            links = re.finditer(r'src="([https]+:...[\/\w \.-]*..[\/\w \.-]*'
                                r'..[\/\w \.-]*..[\/\w \.-].jpg)',
                                self.html_source)
            photos = [{'display_src': m.group(1)} for m in links]
        for photo in photos:
            date = photo.get('date')
            if date:
                try:
                    photo['date_time'] = datetime.fromtimestamp(date)
                except:
                    photo['date_time'] = None
        return photos

    def add_metadata(self, photo_name, caption, date_time):
        """
        Tag downloaded photos with metadata from associated Instagram post.

        If GExiv2 is not installed, do nothing.
        """
        if GExiv2:
            if caption or date_time:
                # todo: improve error handling
                try:
                    exif = GExiv2.Metadata(photo_name)
                    if caption:
                        try:
                            exif.set_comment(caption)
                        except:
                            self.log('Error setting image caption metadata.')
                    if date_time:
                        try:
                            exif.set_date_time(date_time)
                        except:
                            self.log('Error setting image date metadata.')
                    exif.save_file()
                except:
                    pass


def gen_dict_extract(key, var):
    """
    Recursively search for given dict key in nested dicts.

    from http://stackoverflow.com/a/29652561
    author: hexerei software
    """
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='InstaRaider')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('directory', help='Where to save the images')
    parser.add_argument('-n', '--num-to-download',
                        help='Number of posts to download', type=int)
    parser.add_argument('-l', '--log-level', help="Log level", default='info')
    parser.add_argument('-m', '--add_metadata',
                        help=("Add metadata (caption/date) from Instagram "
                              "post into downloaded images' exif tags "
                              "(requires GExiv2 python module)"),
                        action='store_true', dest='use_metadata')
    args = parser.parse_args()
    username = args.username
    directory = op.expanduser(args.directory)

    raider = InstaRaider(username, directory,
                         num_to_download=args.num_to_download,
                         log_level=args.log_level,
                         use_metadata=args.use_metadata)

    if not raider.validate():
        return

    raider.download_photos()


if __name__ == '__main__':
    main()
