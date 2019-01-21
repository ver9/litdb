#!/usr/bin/python
'''make most frequent filepaths accessable'''

'''
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
'''

import pwd
import os
from os.path import expanduser
import fnmatch

def abs_pth(pth):
    '''return absolute path given any filename.'''
    return os.path.abspath(pth)

def get_home():
    '''return home path.'''
    home = expanduser("~")
    return home


def is_file(f):
    '''test is of type file.  return boolean.'''
    return os.path.isfile(f)


def is_dir(d):
    '''test is of type directory. return boolean.'''
    return os.path.isdir(d)


def print_home():
    '''display current user's home path'''
    print get_home()


def search_dir(dir_name, pattern):
    '''search paths within a directory.  return list.'''
    paths = []
    if is_dir(dir_name):
        for path in os.listdir(dir_name):
            if fnmatch.fnmatch(path, pattern):
                paths.append(path)

    return paths


def print_dir(dir_name):
    '''display paths within a directory.'''
    if is_dir(dir_name):
        for path in os.listdir(dir_name):
            print path


def list_subdir(dir_name):
    '''display subdirectories.'''
    #for x in os.walk(dir_name, False):
    if is_dir(dir_name):
        for x in os.walk(dir_name).next()[1]:
            print x


def get_users_home():
    '''return home directory for current user.'''
    home_dirs = []
    for p in pwd.getpwall():
        #print p[0], grp.getgrgid(p[3])[0]
        user_id = int(p[2])
        if int(user_id >= 1000) and (user_id != 65534):
            print p[0], p[5]
            home_dirs.append(p[5])

    return home_dirs


def get_moz(dir_name):
    '''return mozilla directory for current user.'''
    moz_paths = []
    moz_dir = get_home()+"/.mozilla/firefox/"
    for f in search_dir(moz_dir, "*.default"):
        moz_paths.append(moz_dir+f)
    return moz_paths


def get_downloads_dir():
    '''return downloads dir for the current user.'''
    #xfce users
    user_dirs_pth = '/.config/user-dirs.dirs'
    home_ud_pth = get_home()+user_dirs_pth
    probable_pth = get_home()+"/Downloads"

    #raw_input("::"+home_ud_pth+"")
    if is_file(home_ud_pth):
        #raw_input(home_ud_pth+" exists!")
        with open(home_ud_pth) as f:
            segs = []
            for line in f:
                if line[0] != '#':
                    if line.find('XDG_DOWNLOAD_DIR') != -1:
                        #print line
                        segments = line.split('=')
                        #print segments
                        segs.append(segments)
                        directory = segs[0][1]
                        directory = directory.replace("\n", "")
                        directory = directory.replace('"', '')
                        directory = directory.replace("$HOME", get_home())
                        return directory
    elif is_dir(probable_pth):
        return probable_pth
    else:
        return None


def get_working_dir():
    '''return current path.'''
    return os.getcwd()


def get_config_dirs():
    '''return configuration directory for the current user.'''
    config_pth = get_home() + '/.config/user-dirs.dirs'
    if is_file(config_pth):
        with open(config_pth) as f:
            segs = []
            for line in f:
                if line[0] != '#':
                    if line.find('XDG_') != -1:
                        print line
                        segments = line.split('=')
                        print segments
                        segs.append(segments)


def downloads_or_home(pth=None):
    '''return either downloads or home path.'''
    if pth is None:
        pth = get_downloads_dir()

    if pth is None:
        pth = get_home()

    return pth

#---

def tst_search_print(pth, term):
    for f in search_dir(pth, term):
        print f


def tst_search_dir():
    tst_search_print(get_home(), "*.txt")


def tst_search_dir2():
    pth = get_home() + "/.tst"
    os.mkdir(pth)
    tst_search_print(pth, "*.txt")
    os.rmdir(pth)


def tst_get_moz():
    for f in get_moz(get_home):
        print f


def tst_get_downloads_dir():
    print get_downloads_dir()


def tst_get_users_home():
    print get_users_home()


##tsts                  #p/f
#print_home()           #x
#list_subdir(get_home())#x
#print_dir(get_home())  #x
#tst_search_dir()       #x
#print get_users_home() #x
#tst_get_moz()          #x
#tst_get_downloads_dir()#x
#tst_get_users_home()   #x
#tst_search_dir2()      #x
