# InstaRaider
===========
---
**DISCLAIMER:**

This code is posted for informational purposes only. Use of Instagram is governed by the company's Terms of Use (http://instagram.com/legal/terms/). Any user content posted to Instagram is governed by the Privacy Policy (http://instagram.com/legal/privacy/). While I will make all attempts to ensure that InstaRaider works as described below, any future changes to Instragram may introduce errors. If you find a bug or notice that InstaRaider is not working, please create a New Issue on Github

---
### InstaRaider
InstaRaider is a Instagram archiving tool that downloads all photos for any Instagram user.
InstaRaider can download all photos for any public Instagram profile without relying on API calls or user authentication. 

@amirkurtovic

Requires Selenium WebDriver and BeautifulSoup modules

### Installation (Ubuntu/Debian)
This ensures that all dependencies are satisfied on Ubuntu/Debian

    sudo apt-get update
    sudo apt-get install python-bs4 python-pip python git
    sudo pip install selenium
    git clone https://github.com/akurtovic/InstaRaider
    cd InstaRaider
Some older versions of selenium which come bundled with Ubuntu/Debian contain bugs. If InstaRaider fails due to selenium or firefox driver issues, update selenium with:
```
sudo pip install -u selenium
```

### Useage
The first time you use InstaRaider for a specific username, it will download all the photos on that user's profile.
On subsequent uses, InstaRaider will only download new photos (unless you rename or remove the photos from the Images directory for that specific username). 
```python
usage: instaRaider.py [-h] -u USERNAME
```

### Output:
```
$ python instaRaider.py -u username
username has 25 posts on Instagram.
Loading Instagram profile...
...........
Raiding Instagram...
Saving photos to ./Images/username/
------
Photos saved so far:
     ---------10--------20--------30--------40--------50
0    #########################
------
Saved 25 new images to ./Images/username/
Saved activity in logfile: ./Images/username/username.csv
```

### License:
Copyright (c) 2014-2015 Amir Kurtovic. See the LICENSE file for license rights and limitations (MIT).
