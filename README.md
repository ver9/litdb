# litdb

firefox sqlite via commandline

## supported versions
our project prioritizes running from livecd

works with  
firefox 61

## getting started

## BACKUP MANUALLY

litdb has the ability to delete both bookmarks  
and folders.  please backup as usual before  
attempting a backup or restore.  

**_with firefox:_**  
[export bookmarks](https://support.mozilla.org/en-US/kb/export-firefox-bookmarks-to-backup-or-transfer) 

**_without firefox:_**  
1.  _find profile folder_  
   [find profile without opening](https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data#w_finding-your-profile-without-opening-firefox)
  
  
    or  
    ```
    cd ~/; find . -name "places.sqlite"  
    ``` 

2.  _make copy of places.sqlite_ 

    ```
    cp places.sqlite places1.sqlite  
    ```  
### dependencies

install lxml  
https://lxml.de/installation.html
```
sudo apt-get install python-lxml
```
install beautiful soup  
https://www.crummy.com/software/BeautifulSoup/bs4/doc/  
```
sudo apt-get install python-bs4
```
one liner
```
sudo apt-get install python-bs4 python-lxml
```

### installing

download & install via dpkg
```
sudo dpkg -i litdb_x_x_y.deb
```

first time backup
```
litdb
```
if installation succeeded then
a timestamped entry now exists in downloads


## authors

* **ver9** - [ver9](https://github.com/ver9)


## license

This project is licensed under the Apache 2 License see LICENSE file for details




