#!/usr/bin/python
'''url and title pairs.'''

'''
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
'''

class web_link(object):
    '''roll url and title pairs.'''
    def __init__(self, url, title=None):
        self.url = url
        self.title = title

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.url == other.url \
                and self.title == other.title)

    def __ne__(self, other):
        return not self.__eq__(other)


def is_link(field):
    '''check if string contains url prefix and return boolean.'''
    is_lnk = False
    if field.find("http", 0, len(field)) != -1:
        is_lnk = True
    return is_lnk


#---
def test_link1():
    '''basic create and display'''
    lnk1 = web_link('https://en.wikipedia.org/wiki/Main_Page', 'wikipedia')
    print lnk1


def test_link2():
    '''equality'''
    lnk1 = web_link('https://en.wikipedia.org/wiki/Main_Page', 'wikipedia')
    lnk2 = web_link('https://en.wikipedia.org', 'wikipedia')
    lnk3 = web_link('https://en.wikipedia.org/wiki/Main_Page', 'wikipedia')
    print str(lnk1 == lnk2)
    print str(lnk1 == lnk1)
    print str(lnk1 == lnk3)

#               #pass
#test_link1()   #x
#test_link2()   #x
