# InstaRaider
===========
**DISCLAIMER:**

This code is posted for informational purposes only. Use of Instagram is governed by the company's Terms of Use (http://instagram.com/legal/terms/). Any user content posted to Instagram is governed by the Privacy Policy (http://instagram.com/legal/privacy/). While I will make all attempts to ensure that InstaRaider works as described below, any future changes to Instragram may introduce errors. If you find a bug or notice that InstaRaider is not working, please feel free to email me at amirkurtovic@gmail.com

---
### InstaRaider
A Python script that uses Selenium WebDriver to automatically download photos for any Instagram user.
InstaRaider can download all photos for any public Instagram profile without relying on API calls or user authentication. As long as the user's profile is public, InstaRaider will be able to download a specified number of photos.

Requires Selenium WebDriver and BeautifulSoup modules.

@amirkurtovic

### Useage
```python
usage: instaRaider.py [-h] -u USER [-c COUNT]
```

### Output:
```
$ python instaRaider.py -u username -c 25
username has 201 photos on Instagram.
Loading Selenium WebDriver...
Loading Instagram profile...
...........
Raiding Instagram...
Saving photos to ./Images/username/
This could take 0:25.
------
Photos saved so far:
     ---------10--------20--------30--------40--------50
0    #########################
------
Saved 25 images to ./Images/username/
Saved activity in logfile: username.csv

```

### License:
Copyright (c) 2014 Amir Kurtovic. See the LICENSE file for license rights and limitations (MIT).
