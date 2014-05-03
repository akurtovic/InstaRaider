# InstaRaider
===========
**DISCLAIMER:**

This code is posted for informational purposes only. Use of Instagram is governed by the company's Terms of Use (http://instagram.com/legal/terms/). Any user content posted to Instagram is governed by the Privacy Policy (http://instagram.com/legal/privacy/). While I will make all attempts to ensure that InstaRaider works as described below, any future changes to Instragram may introduce errors. If you find a bug or notice that InstaRaider is not working, please feel free to email me at amirkurtovic@gmail.com

---
### InstaRaider
A Python script that uses Selenium WebDriver to automatically download photos for any Instagram user.
InstaRaider can dowload all photos for any public Instagram profile without relying on API calls or user authentication. As long as the user's profile is public, InstaRaider will be able to download a specified number of photos.

Requires Selenium WebDriver and BeautifulSoup modules.

@amirkurtovic

### Useage
```python
usage: Raid.py [-h] -u USER [-c COUNT]
```

### Output:
```
$ python Raid.py -u username -c 15
Loading Instagram profile....
Found 195 photos.
..........
Raiding Instagram...
Saving photos to ./Images/username/
------
Photos saved so far:
     ---------10--------20--------30--------40--------50
0    ###############
------
Saved 15 images to ./Images/username/
```

### License:
Copyright (c) 2014 Amir Kurtovic. See the LICENSE file for license rights and limitations (MIT).
