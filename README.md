# InstaRaider
===========
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
