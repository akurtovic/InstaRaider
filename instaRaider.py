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
from multiprocessing import Process
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

class MultiDownloader(Process):

    def __init__(self, link, headers, name):
        super(MultiDownloader, self).__init__()
        self.link = link
        self.headers = headers
        self.photo_name = name

    def run(self):
        image_request = requests.get(self.link, headers=self.headers)
        image_data = image_request.content
        with open(self.photo_name, 'wb') as fp:
            fp.write(image_data)
        self.headers = image_request.headers
        if "last-modified" in self.headers:
            modtime = calendar.timegm(eut.parsedate(self.headers["last-modified"]))
            os.utime(self.photo_name, (modtime, modtime))
        


class InstaRaider(object):

    def __init__(self, username, directory, num_to_download=None,
                 log_level='info', use_metadata=False, get_videos=False,
                 process_number=100):
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
        self.get_videos = get_videos
        self.set_num_posts(num_to_download)
        self.setup_webdriver()
        self.process_number = process_number

    def __del__(self):
        if self.webdriver:
            self.webdriver.close()

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
        counts_code = re.search(r'\"media":\s*{"count":\s*\d+', response.text)
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
            element = driver.find_element_by_css_selector('a._oidfu')
            driver.implicitly_wait(self.PAUSE)
            element.click()

            for y in range(int(scroll_to_bottom)):
                self.scroll_page(driver)

        # After load all profile photos, retur, source to download_photos()
        time.sleep(1)
        source = driver.page_source

        return source

    def scroll_page(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.05)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.05)

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

        downloaders = []

        for link in links:
            photo_url = link['display_src']
            photo_url = photo_url.replace('\\', '')
            photo_url = re.sub(r'/s\d+x\d+/', '/', photo_url)
            photo_url = re.sub(r'/\w+\.\d+\.\d+\.\d+/', '/', photo_url)
            caption = link.get('caption')
            date_time = link.get('date_time')
            photo_basename = op.basename(photo_url)
            photo_name = op.join(self.directory, photo_basename)

            # save full-resolution photo if its new
            if not op.isfile(photo_name):
                if len(downloaders) > self.process_number:
                    downloaders.pop(0).join()


                downloader = MultiDownloader(photo_url, self.headers, photo_name)
                downloaders.append(downloader)
                downloader.start()

                photos_saved += 1
                self.log('Downloaded file {}/{} ({}).'.format(
                    photos_saved, num_to_download, photo_basename))
                # put info from Instagram post into image metadata
                if self.use_metadata:
                    self.add_metadata(photo_name, caption, date_time)

            else:
                self.log('Skipping file', photo_name, 'as it already exists.')

            if photos_saved >= num_to_download:
                break

        for downloader in downloaders:
            name = downloader.name
            headers = downloader.join()


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
        else:
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

    def download_videos(self):
        """
        Given source code for loaded Instagram page:
        - discover all video wrapper links
        - activate all links to load video url
        - extract and download video url
        """

        if not self.get_videos:
            return;

        # We need to use the driver to query the video wrappers
        driver = self.webdriver

        num_to_download = self.num_to_download or self.num_posts
        if self.html_source is None:
            self.html_source = self.load_instagram()
        if not op.exists(self.directory):
            os.makedirs(self.directory)

        videos_saved = 0
        self.log("Saving videos to", self.directory)

        # Find all of the video wrappers
        video_wrapper_elements = driver.find_elements_by_xpath('.//*[@id="react-root"]/section/main/article/div/div[1]/div/a[.//*[@Class="w79 f99"]]')
        video_wrapper_urls = [link.get_attribute('href') for link in video_wrapper_elements]

        downloaders = []

        for video_wrapper in video_wrapper_urls:
            # Fetch the link of the video wrapper
            driver.get(video_wrapper)

            # Wait until the real video appears
            WebDriverWait(driver, 60).until(
                expected_conditions.presence_of_all_elements_located(
                    (By.CLASS_NAME, 's68')
                )
            )

            # Get the real video, since only 1 video can be clicked on at a time, we only expect there to be a single result
            video_elements = driver.find_elements_by_class_name('s68')
            if len(video_elements) > 0:
                video_url = video_elements[0].get_attribute('src')
                video_name = op.join(self.directory, video_url.split('/')[len(video_url.split('/')) - 1])

                if not op.isfile(video_name):
                    if len(downloaders) > self.process_number:
                        downloaders.pop(0).join()
                    downloaders.append(MultiDownloader(video_url, self.headers, video_name))
                    #self.save_photo(video_url, video_name)
                    videos_saved += 1
                    self.log('Downloaded file {}/{} ({}).'.format(
                        videos_saved, num_to_download, op.basename(video_name)))
                else:
                    self.log('Skipping file', video_name, 'as it already exists.')

                if videos_saved >= num_to_download:
                    break

        for downloader in downloaders:
            downloader.join()

        self.log('Saved', videos_saved, 'videos to', self.directory)

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
    parser.add_argument('-v', '--get_videos',
                        help=("Download videos"),
                        action='store_true', dest='get_videos')
    parser.add_argument('-p', '--process',
                        help=("Number of concurrent processes to use"),
                        action='store', dest='process_number',
                        type=int, default=100)
    args = parser.parse_args()
    username = args.username
    directory = op.expanduser(args.directory)

    raider = InstaRaider(username, directory,
                         num_to_download=args.num_to_download,
                         log_level=args.log_level,
                         use_metadata=args.use_metadata,
                         get_videos=args.get_videos,
                         process_number=args.process_number)

    if not raider.validate():
        return

    raider.download_photos()
    raider.download_videos()


if __name__ == '__main__':
    main()
