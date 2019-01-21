#!/usr/bin/env python
import sqlite3

DIV = "---"

def vmsg(msg, verbose=False):
    '''say.'''
    if verbose:
        print msg


def db_con(f):
    '''connects to a database or creates one if it doesn't exist.'''
    try:
        conn = sqlite3.connect(f)
        #conn.text_factory = str
        conn.text_factory = sqlite3.OptimizedUnicode
        vmsg("connection success")
        return conn
    except sqlite3.Error as err:
        print 'connection failed:'
        print err.message


def db_ex(cur, sql, tup=None):
    '''execute sql against a cursor and return nothing.'''
    try:
        if tup is None or len(tup) == 0:
            cur.execute(sql)
        elif len(tup) > 0:
            if type(tup) is tuple:
                cur.execute(sql, tup)
            else:
                print "tuple please."
    except sqlite3.Error as err:
        print 'transaction failed:'
        print err.message
    #print "commit."


def db_exec(conn, sql, tup=None):
    '''execute single sql statement and return nothing.'''
    try:
        if tup is None or len(tup) == 0:
            conn.execute(sql)
            conn.commit()
        elif len(tup) > 0:
            if type(tup) is tuple:
                conn.execute(sql, tup)
                conn.commit()
            else:
                print "tuple please."
    except sqlite3.Error as err:
        print 'transaction failed:', err.message
    #print "commit."


def db_exec_many(conn, sql, tup=None):
    '''execute multiple sql statements and return nothing.'''
    if tup is None or len(tup) == 0:
        print "tuple please."

    elif len(tup) > 0:
        if type(tup) is tuple:
            conn.executemany(sql, tup)

        else:
            print "tuple please."


def db_select(conn, sql, tup=None):
    '''run a select of some kind and return a list of records.'''
    try:
        is_exec = False
        if tup is None or len(tup) == 0:
            is_exec = True
            cursor = conn.execute(sql)
        elif len(tup) > 0:
            if type(tup) is tuple:
                is_exec = True
                cursor = conn.execute(sql, tup)
            else:
                print "tuple please."
        if is_exec:
            data = cursor.fetchall()
            #num_fields = len(cursor.description)
            #field_names = [i[0] for i in cursor.description]
        return data
    except sqlite3.OperationalError as err:
        print 'operational fail:',
        if "database is locked" == err.message:
            print "database locked."
            #print "please close firefox and try again."
            print ("please close any programs accessing "
                   "the database and try again.")
    except sqlite3.Error as err:
        print 'select failed:'
        print err.message


#args: tablename
def db_select_all_master(conn, t, verbose=True):
    '''query master and return all records.'''
    #print t
    cursor = conn.execute(("SELECT * FROM sqlite_master"), (t,))
    data = cursor.fetchall()
    #num_fields = len(cursor.description)
    #field_names = [i[0] for i in cursor.description]

    if verbose:
        #for f in field_names:
        #    print f

        print DIV
        print "count: "+str(len(data))
        print DIV

        print "data:"
        for row in range(0, len(data)):
            print data[row], "\n"

    return data


def db_table_schema(conn, tablename, verbose=True):
    '''query master and return create sql.'''

    cursor = conn.execute(("SELECT sql FROM sqlite_master "
                           "WHERE type='table' "
                           "AND name=? "), (tablename,))

    data = list(cursor.fetchall())
    if verbose:
        print data

    return data

def db_table_exists(conn, tablename):
    '''query master and return boolean if create sql exists'''
    data = db_table_schema(conn, tablename, verbose=False)
    if len(data) > 0:
        return True
    else:
        return False

def db_schema(conn, verbose=False):
    '''query master and return create sql for user created tables.'''

    cursor = conn.execute(("SELECT sql FROM sqlite_master "
                           "WHERE type='table' "
                           "AND NOT name='sqlite_sequence'"))

    data = list(cursor.fetchall())
    if verbose:
        print data

    return data


def db_tables(conn):
    '''query master and return a list of user created tables.'''
    tables = []

    cursor = conn.execute(("SELECT name FROM sqlite_master "
                           "WHERE type='table' AND NOT name='sqlite_sequence' "
                           "ORDER BY name;"))
    for row in cursor:
        #print "[0]:", row[0];
        tables.append(row[0])
        #print "[1]=", row[1], "\n";

    vmsg(DIV)
    vmsg("tables:")
    for row in tables:
        vmsg(row)
    vmsg(DIV)
    return tables


def db_schema_(conn, verbose=False):
    '''query database and return structure as list.'''
    tables = []
    data = []

    vmsg(DIV)
    tables = db_tables(conn)
    for table in tables:
        data.append(db_table_schema(conn, table, verbose))

    return data


def db_close_con(conn):
    '''close database connection.'''
    conn.close()
    vmsg("connection closed")


