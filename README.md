# InstaRaider
===========

A Python script that uses Selenium WebDriver to automatically download photos for any Instagram user.
Requires Selenium WebDriver and BeautifulSoup modules.
InstaRaider is limited to downloading up to 60 photos from a public profile but does not rely on API calls. As long as the user's profile is public, InstaRaider will be able to download photos.

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
