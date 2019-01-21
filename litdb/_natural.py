#!/usr/bin/python
'''natural sort'''

'''
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
'''

import re
import datetime

DIV = "----------"

def sort(values):
    '''sort list of values and return list.'''
    conv = lambda text: int(text) if text.isdigit() else text.lower()
    alpha_key = lambda key: [conv(c) for c in re.split('([0-9]+)', key)]
    return sorted(values, key=alpha_key)


def convert_date(value, from_format, to_format):
    '''convert between two date arrangements.'''
    if from_format == to_format:
        return value
    else:
        return datetime.datetime.strptime(
            value, from_format).strftime(to_format)


def print_list(listz):
    for value in listz:
        print value


def tst_sort0():
    '''mixed letters and numbers.'''
    listy = ["a1000",
             "a1",
             "a2",
             "a3",
             "a10",
             "a11",
             "a100"]
    print_list(listy)
    print DIV
    print_list(sort(listy))


def tst_sort1():
    '''days & dates'''
    listy = ['cbi.2016_01_31(0).htm',
             'cbi.2016_01_01(0).htm',
             'cbi.2016_01_15(0).htm']
    print_list(listy)
    print DIV
    print_list(sort(listy))


def tst_sort2():
    '''months in m_d_Y format'''
    listy = ['cbi.2016_01_01(0).htm',
             'cbi.2016_01_15(0).htm',
             'cbi.2016_01_31(0).htm',
             'cbi.2015_01_01(0).htm',
             'cbi.2015_01_15(0).htm',
             'cbi.2015_01_31(0).htm'
            ]
    print_list(listy)
    print DIV
    print_list(sort(listy))


def tst_sort3():
    '''years in m_d_Y format'''
    listy = ['cbi.2014_01_01(0).htm',
             'cbi.2013_01_01(0).htm',
             'cbi.2012_01_01(0).htm',
             'cbi.2009_01_01(0).htm',
             'cbi.2008_01_01(0).htm',
             'cbi.2010_01_01(0).htm'
            ]
    print_list(listy)
    print DIV
    print_list(sort(listy))


def tst_sort4():
    '''file numbers in m_d_Y format'''
    listy = ['cbi.2016_01_01(1).htm',
             'cbi.2016_01_01(0).htm',
             'cbi.2016_01_01(2).htm',
             'cbi.2016_01_01(3).htm',
             'cbi.2016_01_01(5).htm',
             'cbi.2016_01_01(4).htm',
            ]
    print_list(listy)
    print DIV
    print_list(sort(listy))


def tst_convert1():
    '''
    test converting between different
    date formats
    '''
    print "expected: 01/01/00"
    print "        : "+convert_date("2000-01-01",
                                    '%Y-%m-%d',
                                    '%m/%d/%y')
    print "expected: 01/29/00"
    print "        : "+convert_date("2000-01-29",
                                    '%Y-%m-%d',
                                    '%m/%d/%y')


##tsts##            #pass
#tst_sort0()        #x
#tst_sort1()        #x
#tst_sort2()        #x
#tst_sort3()        #x
#tst_sort4()        #x
#tst_convert1()     #x
