# InstaRaider
===========
**NOTE ABOUT FUTURE MAINTENANCE:**

5-27-2016 I started this project more than two years ago because I simply needed a quick script to download all of my Instagram photos. Since then it's been cloned thousands of times and used for awesome stuff like quickly gathering lots of images to train machine learning algorithms and probably not-so-awesome stuff like downloading Instagram model pictures. I'm glad that people have found it useful and have forked InstaRaider and contributed over that time, however, I don't have the time or the interest in continuing to maintain this project. As with any web scrapping application, stuff is bound to change and break over time. I will still accept pull requests that fix any major issues, but if somebody else is interested in taking over this project please let me know. I have opened an issue (https://github.com/akurtovic/InstaRaider/issues/65) to be used for disucssion.

---
**DISCLAIMER:**

This code is posted for informational purposes only. Use of Instagram is governed by the company's Terms of Use (http://instagram.com/legal/terms/). Any user content posted to Instagram is governed by the Privacy Policy (http://instagram.com/legal/privacy/). While I will make all attempts to ensure that InstaRaider works as described below, any future changes to Instragram may introduce errors. If you find a bug or notice that InstaRaider is not working, please create a New Issue on Github

---
### InstaRaider
InstaRaider is a Instagram archiving tool that downloads all photos for any Instagram user.
InstaRaider can download all photos for any public Instagram profile without relying on API calls or user authentication. 

### Installation (Ubuntu/Debian)
This ensures that all dependencies are satisfied on Ubuntu/Debian

    sudo apt-get update
    sudo apt-get install python-pip python git
    sudo pip install urllib3
    sudo apt-get install python-bs4 python-pip python git
    sudo pip install selenium requests
    git clone https://github.com/akurtovic/InstaRaider
    cd InstaRaider
Some older versions of selenium which come bundled with Ubuntu/Debian contain bugs. If InstaRaider fails due to selenium or firefox driver issues, update selenium with:
```
sudo pip install -u selenium
```

### Usage
The first time you use InstaRaider for a specific username, it will download all the photos on that user's profile.
On subsequent uses, InstaRaider will only download new photos (unless you rename or remove the photos from the Images directory for that specific username). 
```python
usage: instaRaider.py [-h] [-n imageCount] USERNAME ./DIRECTORY/TO/SAVE/IMAGES
```

### Output:
```
$ python instaRaider.py -n 100 username ./images/username
username has 263 posts on Instagram.
The first 100 of them will be downloaded.
Loading Instagram profile...
Saving photos to ./images/username
Downloaded file 1/100 (123.jpg).
Downloaded file 2/100 (456.jpg).
...
Downloaded file 100/100 (789.jpg).
Saved 100 files to ./images/username
```
### Multiprocessing performance
After 3 independent tests ran on the same machine, for a profile with 565 posts, the script took the following time to run depending on the number of processes ran:

<a href="http://www.imagebam.com/image/ac20ba470493435" target="_blank"><img src="http://thumbnails113.imagebam.com/47050/ac20ba470493435.jpg" alt="imagebam.com"></a> 

### License:
Copyright (c) 2014-2015 Amir Kurtovic. See the LICENSE file for license rights and limitations (MIT).
