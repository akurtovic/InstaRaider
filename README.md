# InstaRaider
===========

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
$ python Raid.py -u username -c 25
Loading Instagram profile....
Found 143 photos.
...
Raiding Instagram...
Saving photos to ./Images/username/
------
#########################
------
Saved 25 images to ./Images/username/
```
