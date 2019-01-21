#!/usr/bin/env python
'''manage sqlite via commandline'''

'''
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Disclaimer of Warranty. Unless required by applicable law or
agreed to in writing, Licensor provides the Work (and each
Contributor provides its Contributions) on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied, including, without limitation, any warranties or conditions
of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
PARTICULAR PURPOSE. You are solely responsible for determining the
appropriateness of using or redistributing the Work and assume any
risks associated with Your exercise of permissions under this License.
'''

import time
import random
import re
import os
import sys
import copy
from urlparse import urlparse, urlsplit
import uuid
import _htm_io
import _path
import _natural as _nat
from _web_link import web_link, is_link
from _lit3 import (db_con,
                   db_ex,
                   db_exec,
                   db_select,
                   db_close_con,
                   db_table_exists)

DIV = "---"
#"%Y_%m_%d"
valid_formats = ["Y", "m", "d"]


def dmsg(msg, dbg=False):
    '''diag.'''
    if dbg:
        print msg


def vmsg(msg, verbose=False):
    '''say.'''
    if verbose:
        print msg


def mvg(verbose=False, *msgs):
    '''say.'''
    if verbose:
        for msg in msgs:
            print msg


def dbg_links(links, dbg=False):
    '''show links processing.'''
    if dbg:
        print "num links:"+str(len(links))
        for k in links:
            print k.title
            print k.url
            print "---"


#-----------
def wrapper(func, *args, **kwargs):
    '''roll a function and arguments into single unit.'''
    def wrapped():
        '''roll a function.'''
        return func(*args, **kwargs)
    return wrapped


#----------

def is_unicode(value):
    '''test if string is unicode and return boolean.'''
    return isinstance(value, unicode)


def str_to_bool(value):
    '''convert string value to boolean and return.'''
#   try:
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
#   else:
#       raise ValueError('error converting string to boolean')
#   except: ValueError
#        print 'error converting string to boolean'


def replace_regex(value, rep, expr, m=0):
    '''regular expression replacement.  return string.'''
    return re.sub(expr, rep, value, m)


def find_regex(value, expr):
    '''search for pattern and return the boolean result.'''
    if value is not None:
        return re.match(expr, value)


def search_dir_regex(dir_name, pattern):
    '''search a directory for a pattern and return the boolean result.'''
    paths = []
    for path in os.listdir(dir_name):
        if find_regex(path, pattern):
            paths.append(path)

    return paths


def regex_filter(value):
    '''remove most troublesome patterns from strings.'''
    if value is not None:
        if find_regex(value, ".*\\\u2014.*") \
            or find_regex(value, ".*\\\u2013.*"):
            #print "---found it---!"
            value = replace_regex(value, "-", "\\\u2013")
            value = replace_regex(value, "-", "\\\u2014")
        #if find_regex(value, "\\\[uUxX][A-Za-z0-9]{2,10}"):
        #    print "found regex!"
        value = replace_regex(value, "", "\\\[uUxX][A-Za-z0-9]{2,10}")

#only allow A-Z, a-z, and 0-9
#                for i in range(0, len(value)):
#                  if re.match("^[A-Za-z0-9]*$", value[i]) \
#                       or value[i]==" ":
#                            val += value[i]
    return value


#----------
def show_fields(data, indexes=None,
                sep="  ", format_rows=True):
    '''display list of data in a specified format.'''
    dmsg("<show_fields>")
    if data:
        if indexes is not None:
            for row in data:
                dmsg(row)
                if format_rows:
                    fields = format_url_entries(row)
                else:
                    fields = row
                #print fields
                dmsg(fields)
                rowstr = ""
                for index in indexes:
                    if index < len(fields):
                        if fields[index] is not None:
                            rowstr += str(fields[index])+sep
                print rowstr
        else:
            for row in data:
                print row
    dmsg("</show_fields>")


def db_select_urls(conn):
    '''query database and return all urls as list.'''
    data = None
    dmsg("<db_select_urls>")
    data = db_select(conn,
                     ("SELECT moz_places.url, moz_bookmarks.title "
                      "FROM moz_places, moz_bookmarks WHERE "
                      "moz_places.id = moz_bookmarks.fk AND "
                      "url LIKE 'http%'"
                      "ORDER BY moz_places.id")
                    )
    dmsg("</db_select_urls>")
    return data


def db_select_folders(conn):
    '''query database and return all folders as list.'''
    data = None
    dmsg("<db_select_folders>")
    data = db_select(conn,
                     ("SELECT type, title FROM moz_bookmarks WHERE "
                      "type = 2 "
                      "ORDER BY title")
                    )
    dmsg("</db_select_folders>")
    return data


def db_show_urls(conn):
    '''query database and display urls.'''
    data = None
    dmsg("<db_show_urls>")
    data = db_select_urls(conn)

    show_fields(data, [0])
    dmsg("</db_show_urls>")


def db_show_folders(conn):
    '''query database and display folders.'''
    data = None

    dmsg("<db_show_folders>")
    data = db_select_folders(conn)

    show_fields(data, [1], format_rows=False)
    dmsg("</db_show_folders>")


def db_show_pairs(conn):
    '''print the url and title of each entry listed in bookmarks.'''
    dmsg("<db_show_pairs>")
    data = None

    data = db_select_urls(conn)
    show_fields(data, [1, 0])
    dmsg("</db_show_pairs>")


def db_con_home():
    '''connect to last profile in user's home directory.'''
    conn = None
    bk_dir = _path.downloads_or_home()
    #raw_input(str(bk_dir))

    dmsg("bk dir:" + bk_dir)
    home_path = _path.get_home()
    paths = _path.get_moz(home_path)
    for path in paths:
        places_path = path + "/"+'places.sqlite'
        is_file = str(_path.is_file(places_path))
        dmsg(path)
        dmsg(places_path)
        dmsg("places is_file:" + is_file)

        if is_file:
            conn = db_con(places_path)


    if conn is not None:
        return conn
    else:
        raise ValueError('could not connect to data store')


def lower(conn):
    '''make title entries all lower case.'''
    db_exec(conn, ("UPDATE moz_bookmarks SET title=LOWER(title)"
                   "WHERE title<>'Tags' AND title<>'All Bookmarks'"
                   "AND title<>'Downloads' AND title<>'History'"
                   "AND title<>'Bookmarks Menu' "
                   "AND title<>'Bookmarks Toolbar'"
                   "AND title<>'Other Bookmarks' AND parent<>1"))


def strip(conn):
    '''trim database to bare essentials.'''
    #db_exec(conn, "UPDATE moz_places WHERE url LIKE 'http%'")
    db_exec(conn, "UPDATE moz_places SET last_visit_date=NULL ")
    #db_exec(("UPDATE moz_bookmarks SET dateAdded=NULL,
    #          "lastModified=NULL WHERE( parent=2 AND position>0)"))
    db_exec(conn, ("UPDATE moz_bookmarks "
                   "SET dateAdded=NULL, lastModified=NULL"))
    db_exec(conn, ("DELETE FROM moz_items_annos "
                   "WHERE anno_attribute_id >= 4"))


def clean(conn):
    '''
    sanitize the database.
    put everything back where you found it.
    '''
    links = []
    get_urls(conn, links)
    reset_tables(conn)
    #args: list of weblinks, check_exists, verbose
    imp_urls(conn, links, check_exists=False)


def shuffle(conn, folder, allow_original=False):
    '''put urls in random order.'''
    links = []
    get_urls(conn, links)
    links_ = copy.deepcopy(links)
    random.shuffle(links)
    if not allow_original and len(links) > 1:
        while links_ == links:
            random.shuffle(links)
    #dbg_links(links)
    soft_reset_tables(conn)
    #args: list of weblinks, check_exists, verbose
    imp_urls(conn, links, check_exists=False,
             folder=folder)


def sort(conn, title=True):
    '''
    sort entries a-z.
    sort by title by default.
    '''
    links = []
    get_urls(conn, links)
    if title:
        links.sort(key=lambda x: x.title, reverse=False)
    else:
        links.sort(key=lambda x: x.url, reverse=False)
    #dbg_links(links)
    soft_reset_tables(conn)
    imp_urls(conn, links, check_exists=False)


def reload_user(conn, base, imp_dir=None,
                indx=0, numbered=True, timestamp=True,
                date_format="%d_%m_%Y", folder=None):
    '''
    import last backup.
    0 being current and 1 being previous.
    '''
    full_path = None
    dmsg("<reload_user>")
    imp_dir = _path.downloads_or_home(imp_dir)
    #if imp_dir is None:
    #    imp_dir = _path.get_downloads_dir()
        #print "imp dir: "+str(imp_dir)
    #imp_user(results.i_val, results.v_val)
    #print "reloading..."
    #print timestamp
    fyl = last_xpo_path(base, xpo_dir=imp_dir, numbered=numbered,
                        timestamp=timestamp, date_format=date_format)
    dmsg("last fyl:" + str(fyl))
    if fyl is not None and imp_dir is not None:
        full_path = imp_dir + "/" + fyl
        #print full_path
        #reset_tables(conn)
        imp_user(conn, full_path, folder=folder)
    dmsg("</reload_user>")
    return fyl


#----------
def strip_special(value):
    '''strip special characters from a string. return string.'''
    chars = "(),'"
    for i in range(0, len(chars)):
        #print chars[i]
        value = value.replace(chars[i], "")
    return value


def reset_tables(conn):
    '''clear database of all links and user created folders.'''
    cur = conn.cursor()
    db_ex(cur, "DELETE FROM moz_places WHERE url LIKE 'http%'")
    db_ex(cur, ("DELETE FROM moz_bookmarks "
                "WHERE (guid == 'root________' AND id > 20)"))
    db_ex(cur, ("DELETE FROM moz_bookmarks "
                "WHERE (guid == 'unfiled_____') AND id > 20"))
    #delete any entry in moz_books which doesn't contain at
    #least four trailing underscores.
    db_ex(cur, "DELETE FROM moz_bookmarks "
               "WHERE guid NOT LIKE '%!_!_!_!_'"
               "ESCAPE '!'")
    if db_table_exists(conn, "moz_origins"):
        db_ex(cur, "DELETE FROM moz_origins")
    if db_table_exists(conn, "moz_hosts"):
        db_ex(cur, "DELETE FROM moz_hosts")
    db_ex(cur, "DELETE FROM moz_historyvisits")
    if db_table_exists(conn, "moz_favicons"):
        db_ex(cur, "DELETE FROM moz_favicons")
    db_ex(cur, ("DELETE FROM moz_items_annos "
                "WHERE anno_attribute_id = 1 AND item_id > 3"))
    db_ex(cur, ("DELETE FROM moz_items_annos "
                "WHERE anno_attribute_id >= 4"))
    conn.commit()


def soft_reset_tables(conn):
    '''only delete links.'''
    cur = conn.cursor()
    db_ex(cur, "DELETE FROM moz_places WHERE url LIKE 'http%'")
    db_ex(cur, "DELETE FROM moz_bookmarks "
               "WHERE guid NOT LIKE '%!_!_!_!_' "
               "ESCAPE '!' AND type = 1")
    if db_table_exists(conn, "moz_hosts"):
        db_ex(cur, "DELETE FROM moz_hosts")
    if db_table_exists(conn, "moz_origins"):
        db_ex(cur, "DELETE FROM moz_origins")
    db_ex(cur, "DELETE FROM moz_historyvisits")
    if db_table_exists(conn, "moz_favicons"):
        db_ex(cur, "DELETE FROM moz_favicons")
    db_ex(cur, ("DELETE FROM moz_items_annos "
                "WHERE anno_attribute_id = 1 AND item_id > 3"))
    db_ex(cur, ("DELETE FROM moz_items_annos "
                "WHERE anno_attribute_id >= 4"))
    conn.commit()


def sanitize_str(val):
    '''remove most problematic characters.'''
    val = val.encode('ascii', 'ignore')
    val = val.replace("u'", "")
    val = regex_filter(val)
    val = val.replace("'", "")
    val = val.replace('"', "")
    val = val.replace('\\\\', "\\")
    val = regex_filter(val)
    val = _htm_io.remove_pad(val)
    return val


def format_url_entries(entry, url_index=0, title_index=1):
    '''sanitize a url entry pair and return a list.'''
    values = None
    url = None
    txt = None
    row = list(entry)

    if is_link(row[url_index]):
        url = row[url_index]
        txt = row[title_index]
        url = sanitize_str(url)
        txt = sanitize_str(txt)

    values = [url, txt]
    return values


def places_count(conn):
    '''query database for number of urls and return.'''
    dmsg("<places_count>")
    data = db_select(conn,
                     ("SELECT COUNT(moz_places.url) "
                      "FROM moz_places, moz_bookmarks "
                      "WHERE moz_places.id = moz_bookmarks.fk "
                      " AND moz_places.url LIKE 'http%'")
                    )
    (count,) = data[0]
    dmsg("</places_count>")
    return count


def test_bookmarks_guid(conn):
    '''
    display all entries whose guids do
    not contain a trailing underscore.
    '''
    dmsg("<test_bookmarks_guid>")
    data = db_select(conn,
                     ("SELECT * FROM moz_bookmarks "
                      "WHERE guid NOT LIKE '%!_' ESCAPE '!'")
                    )
    show_fields(data)


def get_urls(conn, links):
    '''translate urls in database to a list of objects.'''
    dmsg("<get urls>")
    data = db_select_urls(conn)
    for row in data:
        dmsg(row)
        #print row
        fields = format_url_entries(row)
        dmsg(fields)
        if fields[0] is not None and fields[1] is not None:
            lnk = web_link(fields[0], fields[1])
            links.append(lnk)
    dmsg("</get urls>")


def valid_format(value):
    '''test if date format is handled and return boolean.'''
    is_valid = set(valid_formats)

    return value in is_valid


#args: base, list of filenames, empty list for natural names,
#empty dict for index
#results: sorted list of in names in natural format and dictionary
#index of the original names
def names_to_nat(base, names, index, date_format="%d_%m_%Y"):
    '''
    convert a list of filenames with dates
    to natural sorted format.
    '''
    nat_names = []
    for i in names:
        date_str = ""
        j = path_date(i)
        k = path_index(i)
        if j is not None:
            date_str = _nat.convert_date(j, date_format, "%Y_%m_%d")
        new_path = base + date_str + "("+str(k)+").htm"
        index[new_path] = i
        nat_names.append(new_path)
    nat_names = _nat.sort(nat_names)
    return nat_names


def file_stamp(base, time_stamp=True,
               date_format="%d_%m_%Y"):
               #verbose=False):
    '''timestamp filename and return string.'''
    now = time.strftime(date_format)
    dmsg("base path:" + base)
    dmsg("now: " + now)

    if time_stamp:
        fyl = base + "." + now
    else:
        fyl = base
    return fyl


def date_indices(listx, not_None=True):
    '''return last dated index in a list.'''
    index_start = None
    index_stop = None
    if not_None:
        for j in xrange(0, len(listx)):
            p_date = path_date(listx[j])
            if index_start is None and p_date is not None:
                index_start = j
            elif index_start is not None and p_date is not None:
                index_stop = j
    else:
        for i in xrange(0, len(listx)):
            p_date = path_date(listx[i])
            #print "p_date:"+p_date
            if index_start is None and p_date is not None:
                index_start = i
            elif index_start is not None and p_date is not None:
                index_stop = i
    return (index_start, index_stop)


#args:base backup name,
def last_xpo_path(base, xpo_dir=None, numbered=True,
                  timestamp=True, date_format="%d_%m_%Y"):
    '''return path of most current backup.'''
    dmsg("<last_xpo_path>")
    ext = ".htm"

    xpo_dir = _path.downloads_or_home(xpo_dir)

    #check the directory for a file that already exist with same
    #name
    files = _path.search_dir(xpo_dir, base+"*"+ext)
    listz = []
    dictz = {}
    listz = names_to_nat(base=base+".",
                         names=files, index=dictz,
                         date_format=date_format)

    #find the start and stop index of all the dated files
    if timestamp:
        index_start, index_stop = date_indices(listz, not_None=True)
    elif not timestamp:
        index_start, index_stop = date_indices(listz, not_None=False)

    #print "listz:"+str(listz)
    #print "index_start:"+str(index_start)
    #print "index_stop:"+str(index_stop)
    if index_start is not None and index_stop is None:
        fyl = dictz[listz[index_start]]
    elif index_stop is not None:
        fyl = dictz[listz[index_stop]]
    else:
        fyl = None
    dmsg("</last_xpo_path>")
    return fyl


def next_xpo_path(base, xpo_dir=None, numbered=True,
                  timestamp=True, date_format="%d_%m_%Y"):
    '''return path of future backup.'''
    dmsg("<next_xpo_path>")
    ext = ".htm"
    now = time.strftime(date_format)

    xpo_dir = _path.downloads_or_home(xpo_dir)
    vmsg(xpo_dir)

    fyl = file_stamp(base, timestamp, date_format)

    if numbered:

        files = _path.search_dir(xpo_dir, base+"*.htm")
        first_export = False

        if len(files) > 0:
            last_fyl = last_xpo_path(base=base, xpo_dir=xpo_dir,
                                     numbered=numbered, timestamp=timestamp,
                                     date_format=date_format)
            index = path_index(last_fyl)
            via_date = path_date(last_fyl)
            if via_date is None and index is None:
                index = 0
                via_date = now
                first_export = True
            if via_date is None and index is not None:
                first_export = False
            elif via_date != now:
                index = 0
                via_date = now
                first_export = True
            else:
                first_export = False

        elif len(files) == 0:
            index = 0
            via_date = now
            first_export = True

        #print "path_date: " + via_date
        #print "now:" + now
        #print "index:" + str(index)

        if timestamp:
            if via_date == now and not first_export:
                fyl += idx(index+1)
            else:
                fyl += idx(0)
        else:
            if not first_export:
                fyl += idx(index+1)
            else:
                fyl += idx(0)
    dmsg("</next_xpo_path>")
    return fyl + ext


def idx(val, opn="(", close=")"):
    return opn + str(val) + close


#dirty version
def path_index(path):
    '''return index of an index formatted path.'''
    bucket = ""
    in_paren = False
    for i in range(0, len(path)):
        if path[i] == "(":
            in_paren = True
        elif path[i] == ")":
            in_paren = False

        if in_paren and path[i] != "(":
            bucket += path[i]

    if bucket.isdigit():
        value = int(bucket)
        return value
    else:
        return None


#dirty version
def path_date(path):
    '''
    check if there is a numeric string
    between the basename and the first parenthesis.
    '''
    bucket = ""
    start_date = False
    end_date = False
    for i in range(0, len(path)):
        if path[i] == "." or path[i] == "(":
            if not start_date:
                start_date = True
            elif start_date:
                end_date = True

        if start_date and (path[i] != "." and path[i] != "("):
            bucket += path[i]
        elif start_date and end_date:
            break

#   if is_date(bucket):
    value = bucket
    if ")" not in value and value != "":
        return value
    else:
        return None


def guidd(length=12):
    '''
    generate guid specified length
    without predictable -.
    return a string.
    '''
    guid_ = str(uuid.uuid4())
    guid_ = guid_.replace("-", "")
    return guid_[:length]       


def imp_place(conn, title, url, cur=None, folder=None):
    '''import single url into database'''
    data = None
    places_id = None
    max_position = None
    #parent = 2
    parent = 5
    typ = 1
    data = db_select(conn,
                     "SELECT id FROM moz_places WHERE url=?",
                     (url,))
    places_id = strip_special(str(data[0]))
    data = db_select(conn,
                     #"SELECT MAX(position) FROM moz_bookmarks WHERE parent = 2")
                     "SELECT MAX(position) FROM moz_bookmarks WHERE parent = 5")
    max_position = strip_special(str(data[0]))

    if folder is not None:
        data = db_select(conn,
                         ("SELECT id FROM moz_bookmarks "
                          "WHERE type = 2 AND title = ?"),
                         (folder,))
        
        print "data::"+str(data)
        folder_id = strip_special(str(data[0]))
        if folder_id > 0:
            parent = folder_id

    guid_ = guidd()
    if max_position == 'None':
        max_position = 0
    else:
        max_position = int(max_position) + 1

    if cur is not None:
        db_ex(
            cur,
            ("INSERT INTO moz_bookmarks("
             "title, parent, type, fk, position, guid)"
             "VALUES(?,?,?,?,?,?);"),
            (title, str(parent),
             str(typ), str(places_id),
             str(max_position), str(guid_)))
    else:
        db_exec(conn,
                ("INSERT INTO moz_bookmarks"
                 "(title, parent, type, fk, position, guid)"
                 "VALUES(?,?,?,?,?,?);"),
                (title, str(parent),
                 str(typ), str(places_id),
                 str(max_position), str(guid_)))


#args: list of weblinks, check_exists, verbose
def imp_urls(conn, links, check_exists=True,
             folder=None):
    '''add links to database.'''
    #data = db_select("SELECT moz_places.id, moz_places.url, moz_bookmarks.title FROM /
    #moz_places, moz_bookmarks where moz_places.id = moz_bookmarks.fk")
    url = None
    title = None
    dmsg("<imp_urls>")
    cur = conn.cursor()

    if check_exists:
        #db_exec(conn, 'BEGIN TRANSACTION')

        for i in range(0, len(links)):
            url = links[i].url
            title = links[i].title
            vmsg(title)
            vmsg(url)
            vmsg("---")
            if db_table_exists(conn, "moz_hosts"):
                if not host_exists(conn, url):
                    db_exec(conn,
                            ("INSERT INTO moz_hosts(host, frecency, typed, prefix) "
                             "VALUES(?,140,0,NULL)"),
                            (hostname(url),))
            elif db_table_exists(conn, "moz_origins"):
                if not origins_exists(conn, url):
                    db_exec(conn,
                            ("INSERT INTO moz_origins(prefix, host, frecency) "
                             "VALUES(?,?,140)"),
                            (prefix(url), hostname(url),))
                    #print "inserting nonexistant record."
                    #print "exists:" + str(origins_exists(conn, url))

            if not link_exists(conn, url):
                guid_ = guidd()
                db_exec(conn,
                        "INSERT INTO moz_places(url, guid) VALUES(?, ?)",
                        (url, guid_))

            if not bookmark_exists(conn, url):
                imp_place(conn, title, url, folder=folder)
            title = None
            url = None
        #db_exec(conn, 'COMMIT')
    elif not check_exists:
        #filter distinct links here
        distinct_links = []
        for i in range(0, len(links)):
            url = links[i].url
            title = links[i].title
            found = False
            for j in range(0, len(distinct_links)):
                if distinct_links[j].url == links[i].url:
                    found = True
                    break
            if not found:
                distinct_links.append(links[i])

        #dmsg("distinct links:"+str(len(distinct_links)))
        db_ex(cur, 'BEGIN;')
        #cur.execute("BEGIN;")
        for i in range(0, len(distinct_links)):
            #vmsg(title)
            #vmsg(url)
            #vmsg("---")

            #removing this check is faster but more error prone
            #if not bookmark_exists(url):

            db_ex(cur, "INSERT INTO moz_places(url) VALUES(?);",
                  (distinct_links[i].url,))
            #cur.execute("INSERT INTO moz_places(url) VALUES(?);",
            #           (distinct_links[i].url,))

        conn.commit()
        db_ex(cur, 'BEGIN;')
        for i in range(0, len(distinct_links)):
            imp_place(conn, distinct_links[i].title,
                      distinct_links[i].url, cur, folder=folder)

        conn.commit()

    dmsg("</imp_urls>")


def valid_path(test_path, test_dir=None):
    '''check file exists.  return None or valid file path.'''
    path = ""
    if _path.is_file(test_dir + "/" + test_path):
        path = test_dir + "/" + test_path
    elif _path.is_file(test_dir + test_path):
        path = test_dir + test_path
    elif _path.is_file(test_path):
        path = test_path
    else:
        path = None

    return path


#args: path to import from, verbose
def imp_user(conn, imp_path, imp_dir=None,
             folder=None):
    '''import htm urls into current user's places file.'''
    links = []
    valid = None

    imp_dir = set_default(imp_dir, _path.downloads_or_home(), None)

    if imp_path is None:
        print "please supply a file path."
    else:
        #validate the path and handle mistakes with
        #being too forward or not forward enough
        imp_path_ = _path.abs_pth(imp_path)
        #valid = valid_path(imp_path, imp_dir)
        valid = valid_path(imp_path_, imp_dir)
        dmsg("full path:" + str(valid))
        dmsg("is_file:" + str(_path.is_file(valid)))
        if valid is not None:
            dmsg("imp_path: " + valid)
            _htm_io.find_links(valid, links)
            imp_urls(conn, links,
                     check_exists=True,
                     folder=folder)
        else:
            print "file doesn't exist."

    dmsg("<imp_user>")
    #must be full path; file:/// in find_links()


def xpo_places(conn, xpo_path, file_name=None,
               head_title="", numbered=True, timestamp=False,
               date_f="%d_%m_%Y"):
    '''export places file urls into htm.'''
    dmsg("<xpo_places>")
    #print date_f
    links = []

    if file_name is None:
        file_name = "bkm"

    vmsg("dir: " + xpo_path + "; base:" + file_name)

    get_urls(conn, links)
    xpo_urls(xpo_path, file_name,
             links, head_title,
             numbered=numbered,
             timestamp=timestamp, date_f=date_f)
    dmsg("</xpo_places>")


#user_path = full path to the firefox profile to be backed up;
#xpo_dir = destination directory of the backup;
def xpo_user(conn, file_name=None, xpo_dir=None,
             head_title="", verbose=True, numbered=True,
             timestamp=False, date_f="%d_%m_%Y",
             user_path=None):
    '''unless otherwise specified backup current user.'''
    vmsg("exporting...", verbose)

    xpo_dir = _path.downloads_or_home()

    vmsg("xpo dir:" + xpo_dir, verbose)
    xpo_places(conn, xpo_path=xpo_dir, file_name=file_name,
               head_title=head_title, numbered=numbered,
               timestamp=timestamp, date_f=date_f)

def xpo_htm(file_name=None, xpo_dir=None,
            head_title="", numbered=True,
            timestamp=False, date_f="%d_%m_%Y",
            user_path=None):
    '''create an empty backup.'''
    verbose = False

    xpo_dir = _path.downloads_or_home()
    vmsg("xpo dir:" + xpo_dir, verbose)
    xpo_urls(xpo_dir, file_name,
             links=None,
             head_title=head_title,
             numbered=numbered,
             timestamp=timestamp,
             date_f=date_f)

def xpo_urls(xpo_path, base_fname, links,
             head_title="", numbered=False,
             timestamp=True, date_f="%d_%m_%Y_%H_%M_%S"):
    '''export links to datestamped htm file.'''
    dmsg("<xpo_urls>")
    now = time.strftime(date_f)

    dmsg("path:" + xpo_path)
    dmsg("base:" + base_fname)
    dmsg("now: " + now)

    if timestamp or numbered:
        fyl = next_xpo_path(base_fname, xpo_dir=xpo_path,
                            numbered=numbered, timestamp=timestamp,
                            date_format=date_f)
    else:
        fyl = base_fname + ".htm"
    fyl = xpo_path + "/" + fyl

    dmsg("next path:" + fyl)

    indn = _htm_io.indent()
    _htm_io.write_top(fyl, head_title)
    _htm_io.write_line(fyl, indn+"<DL>")
    _htm_io.write_line(fyl, indn+"<!--#-->")

    if links is None:
        len_links = 0
    else:
        len_links = len(links)

    for k in range(0, len_links):
        if links[k].url is not None and links[k].title is not None:
            dmsg(links[k].title + " " + links[k].url)
            _htm_io.write_link(fyl, links[k].url,
                               links[k].title, "")

            dmsg(links[k].url)
            dmsg(links[k].title)
            dmsg(DIV)

    _htm_io.write_line(fyl, indn+"</DL>")
    _htm_io.write_line(fyl, indn+"<!--#-->")
    _htm_io.write_bottom(fyl)
    dmsg("</xpo_urls>")


def hostname(url):
    '''return domain from url string.'''
    url_obj = urlparse(url)
    return url_obj.hostname

def prefix(url):
    '''return prefix from url string.'''
    url_obj = urlsplit(url)
    return url_obj.scheme

def link_exists(conn, url):
    '''test if link exists in database.'''
    data = None
    count = None
    data = db_select(conn,
                     "SELECT count(*) FROM moz_places WHERE url=?",
                     (url,))
    count = str(data[0])
    count = strip_special(count)
    if int(count) == 0:
        return False
    elif int(count) == 1:
        return True

def origins_exists(conn, url):
    '''test if host url exists in database.'''
    data = None
    count = None
    data = db_select(conn,
                     "SELECT count(*) FROM moz_origins WHERE host=?",
                     (hostname(url),))
    count = str(data[0])
    count = strip_special(count)
    if int(count) == 0:
        return False
    elif int(count) == 1:
        return True

def host_exists(conn, url):
    '''test if host url exists in database.'''
    data = None
    count = None
    data = db_select(conn,
                     "SELECT count(*) FROM moz_hosts WHERE host=?",
                     (hostname(url),))
    count = str(data[0])
    count = strip_special(count)
    if int(count) == 0:
        return False
    elif int(count) == 1:
        return True


def bookmark_exists(conn, url):
    '''
    test if there is bookmark refencing a link
    in database with a specified url.
    '''
    data = None
    count = None
    data = db_select(conn,
                     "SELECT id FROM moz_places WHERE url=?",
                     (url,))
    places_id = str(data[0])
    places_id = strip_special(places_id)
    #print places_id

    data = db_select(conn,
                     "SELECT COUNT(*) FROM moz_bookmarks WHERE fk=?",
                     (places_id,))
    count = str(data[0])
    count = strip_special(count)
    #print "count:" + count
    if count == 'None':
        print "None!"
        return False
    else:
        int(count)
    if int(count) == 0:
        return False
    elif int(count) == 1:
        return True


def transform(conn, results):
    '''perform in place changes on database.'''
    if results.s_val:
        strip(conn)

    if results.l_val:
        lower(conn)

    if results.sh_val:
        #print "sh..."
        #wrapped = wrapper(shuffle, conn)
        #print timeit.timeit(wrapped, number=1)
        print str(results.f_val)
        shuffle(conn, results.f_val)
    elif results.z_val:
        sort(conn)

    return (results.s_val or
            results.l_val or
            results.sh_val or
            results.z_val)


def set_default(value, default, *values):
    '''collapse an if statement which sets a value.'''
    for val in values:
        if value == val:
            return default
    return value


def run(results):
    '''execute.'''
    date_format = "%Y_%m_%d"
    #date_format = "%d_%m_%Y"
    f_name_ = "cbi"
    head_ = "confidential"

    if results.g_val:
        xpo_htm(file_name=f_name_,
                xpo_dir=None,
                head_title=head_,
                numbered=True,
                timestamp=True,
                date_f=date_format)
        sys.exit()
    #-ds
    if results.ds_val is None:
        conn = db_con_home()
    else:
        if _path.is_file(results.ds_val):
            ds_path = _path.abs_pth(results.ds_val)
            conn = db_con(ds_path)
        else:
            raise ValueError('could not connect to data store')

    #.litrc file here
    #you should overright rc
    #values with commandline switches
    #and not vice versa

    t_val = False
    if results.t_val is not None:
        t_val = True
        date_format = results.t_val

    #export
    if results.x_val is not None:
        f_name = set_default(results.x_val, f_name_, '')
        head = set_default(results.y_val, head_, None, '')

        #-x -f
        if results.c_val:
            clean(conn)
        else:
            transform(conn, results)

            #backup or reload but not both
            if results.r_val:
                reload_user(conn=conn, base=f_name,
                            numbered=True, timestamp=t_val,
                            date_format=date_format,
                            folder=results.f_val)
            else:
                xpo_user(conn, f_name, None,
                         head, results.v_val, results.n_val,
                         t_val, date_format)
        #-dx
        if results.d_val:
            reset_tables(conn)
    #import
    elif results.i_val is not None:
        if results.d_val:
            reset_tables(conn)
        elif results.sr_val:
            soft_reset_tables(conn)
        imp_user(conn, imp_path=results.i_val,
                 folder=results.f_val)

    #reload
    elif results.r_val:
        f_name = set_default(results.x_val, f_name_, None, '')
        head = set_default(results.y_val, head_, None, '')
        reload_user(conn=conn, base=f_name, numbered=True,
                    timestamp=True, date_format=date_format,
                    folder=results.f_val)

    #reset, view links
    #or backup
    elif results.x_val is None:
        if results.d_val:
            reset_tables(conn)
        elif results.sr_val:
            soft_reset_tables(conn)
        elif results.v_val:
            db_show_pairs(conn)
        elif results.vf_val:
            db_show_folders(conn)
        elif results.o_val:
            db_show_urls(conn)
        else:
            if not transform(conn, results):
                #print "xporting..."
                xpo_user(conn, f_name_, None, head_,
                         verbose=results.v_val, numbered=True,
                         timestamp=True, date_f=date_format)

    db_close_con(conn)
