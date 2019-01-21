#!/usr/bin/python
'''read and write htm'''

'''
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
'''


import urllib2
from bs4 import BeautifulSoup
from _web_link import web_link

def remove_pad(value):
    '''delete whitespace.'''
    value = value.lstrip()
    return value

def indent(spaces=False, tab_len=4):
    '''return appropriate tabs or spacing.'''
    indent_ = ""
    if spaces:
        if tab_len == 2:
            indent_ = "  "
        elif tab_len == 4:
            indent_ = "    "
        else:
            for _ in xrange(0, tab_len):
                indent_ += " "
    else:
        indent_ = "\t"

    return indent_

def write(file_pth, line):
    '''overwrite.'''
    file_obj = open(file_pth, "wb")
    file_obj.write(line+"\n")
    file_obj.close()

def write_line(file_pth, line):
    '''append.'''
    file_obj = open(file_pth, "a")
    file_obj.write(line+"\n")
    file_obj.close()
    #print "file writen:"+line;


def write_link(file_pth, address, title, descript, spaces=False, tab_len=4):
    '''insert link.'''
    indn = ""
    indn = indent(spaces=spaces, tab_len=tab_len)
    indn += indn
    write_line(file_pth, indn+"<DT><A HREF='"+address+ "'>"+title+"</A>")
    write_line(file_pth, indn+"<DD>"+descript)


def write_top(file_pth, head_title=None, spaces=False, tab_len=4):
    '''insert opening htm tags.'''
    indn = ""
    indn = indent(spaces=spaces, tab_len=tab_len)

    write(file_pth, "<HTML>")
    if head_title is not None:
        write_line(file_pth, indn+"<HEAD>")
        write_line(file_pth, indn+"<TITLE>"+head_title+"</TITLE>")
        write_line(file_pth, indn+"</HEAD>")


def write_bottom(file_pth):
    '''insert closing htm tags.'''
    write_line(file_pth, "</HTML>")


def find_links(file_pth, nks):
    '''search for links in htm.'''
    page = urllib2.urlopen("file:///"+file_pth)
    soup = BeautifulSoup(page, "lxml")
    #print soup.prettify()
    raw_links = soup.findAll('a')
    #print links
    #print div
    search_str = 'a href="'
    #search_str2 = '">'
    search_str2 = '"'
    search_str3 = ">"
    search_str4 = '</a>'
    for k in raw_links:
        #print link
        k = str(k)
        start_index = k.find(search_str)
        url_index = start_index+len(search_str)
        stop_index = k.find(search_str2, url_index)
        close_index = k.find(search_str3)
        title_index = close_index+1
        title_stop_index = k.find(search_str4)
        #print link[url_index:stop_index]
        #print link[title_index:title_stop_index]
        lnk = web_link(remove_pad(k[url_index:stop_index]),
                       remove_pad(k[title_index:title_stop_index]))
        nks.append(lnk)

#----------
def tst_write():
    '''simulate adding links to file.'''
    indn1 = indent()
    indn2 = indn1 + indn1
    file_pth = "tst.html"
    write_top(file_pth, "tst_write")
    write_line(file_pth, indn1+"<DL>")
    write_line(file_pth, indn2+"<DT><A HREF='https://www.startpage.com'>search</A>")
    write_line(file_pth, indn2+"<DD>startpage search")
    write_line(file_pth, indn2+"<DT><A HREF='https://www.wikipedia.org'>wiki</A>")
    write_line(file_pth, indn2+"<DD>wikipedia")
    write_link(file_pth, "http://www.timeanddate.com/worldclock/",
               "time", "time & date")
    write_line(file_pth, indn1+"</DL>")
    write_bottom(file_pth)

def tst_print_htm_link(indn):
    '''test displaying indentation with a single link in html.'''
    print "<HTML>"
    print indn+"<A HREF='https://www.wikipedia.org'>wiki</A>"
    print "</HTML>"

def tst_indent1():
    '''
    test indentation varying length
    from 1-8 with both tabs and spaces.
    '''
    indn0 = indent(spaces=True, tab_len=8)
    indn1 = indent(spaces=True)
    indn2 = indent(spaces=True)
    #print "indent 2"
    indn3 = indent(spaces=True, tab_len=2)
    #print "indent 1"
    indn4 = indent(tab_len=1)
    #print "spaces; 8"
    tst_print_htm_link(indn0)
    #print "spaces; 4"
    tst_print_htm_link(indn1)
    #print "tabs"
    tst_print_htm_link(indn2)
    #print "spaces; 2"
    tst_print_htm_link(indn3)
    #print "spaces; 1"
    tst_print_htm_link(indn4)

#tst_write();
#tst_indent1()
