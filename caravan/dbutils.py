#! /usr/bin/python

"""
     Utilities for connecting with the Caravan database. It implements the Connection class
     which wraps a psycopg2 connection with some utilities like:
     execute, fetchall, close, commit, cursor
     plus async support so that the user does not have to care about issues 
     (auto waits between two dbase operations, commits only in non async mode)
     
(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""
from __future__ import print_function


__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Oct 5, 2014 8:00:00 PM$"

import psycopg2 
import select
import socket #used to retreive if we are runnign on makalu, see below
# via socket.gethostname()

_DEBUG_= 0
ASYNC = 1
HOST = 'localhost' #if "makalu" == socket.gethostname() else "makalu.gfz-potsdam.de" #'lhotse21.gfz-potsdam.de' #'localhost'
DBNAME = 'caravan'
USER = 'postgres'
PSWD = 'postgres'

def wait(conn):
    """
        Wait function for asyncrhonous psycopg database connection. 
        See http://initd.org/psycopg/docs/advanced.html#asynchronous-support
        
        Example usage:
            aconn = psycopg2.connect(database='test', async=1)
            wait(aconn)
            acurs = aconn.cursor()
            acurs.execute("SELECT pg_sleep(5); SELECT 42;")
            wait(acurs.connection)
            acurs.fetchone()[0]
    """
    while 1:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [])
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [])
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)

def connect(host=HOST, dbname=DBNAME, user=USER,  password=PSWD, async=ASYNC):
    #see http://initd.org/psycopg/docs/advanced.html#asynchronous-support
    aconn = psycopg2.connect(host=host, dbname=dbname, user=user,  password=password, async=async)
    if async:
        if _DEBUG_:
            print("waiting (async=1)")
        wait(aconn)
    return aconn

def cursor(connection, operation, parameters=None):
    """
        Shorthand for
            c = connection.cursor()
            c.execute(operation,parameters)
            wait(c.connection) #only if connection.async
            return c
        Note also that this method takes care of asynchronous connection by 
        calling the wait function, and blocks
        until the cursor isn't available. For more info, see
        http://initd.org/psycopg/docs/advanced.html#asynchronous-support
    """
    #from http://initd.org/psycopg/docs/faq.html#best-practices
    #Cursors are lightweight objects and creating lots of them should not pose any kind of problem. 
    #But note that cursors used to fetch result sets will cache the data and use memory in proportion to the result set size. 
    #Our suggestion is to almost always create a new cursor and dispose old ones as soon as the data is not required anymore (call close() on them.) 
    #The only exception are tight loops where one usually use the same cursor for a whole bunch of INSERTs or UPDATEs.
    cursor = connection.cursor()
    if parameters is None:  cursor.execute(operation)
    else: cursor.execute(operation, parameters)
        
    if cursor.connection.async: #see http://initd.org/psycopg/docs/connection.html#connection.async
        if _DEBUG_:
            print("waiting (async=1)")
        wait(cursor.connection)
    
    return cursor

def execute(connection, operation, parameters=None):
    """
        Shorthand for
            c = connection.cursor()
            c.execute(operation,parameters)
            wait(c.connection) #only if connection.async
            c.close()
        Therefore, the operation must NOT be a query operation (e.g., insert/delete is fine, not select)
        Note also that this method takes care of asynchronous connection by 
        calling the wait function, and blocks
        until the cursor isn't available. For more info, see
        http://initd.org/psycopg/docs/advanced.html#asynchronous-support
    """
    cursor(connection, operation, parameters).close()

def fetchall(connection, operation, parameters=None):
    """
        Shorthand for
            c = connection.cursor()
            c.execute(operation,parameters)
            wait(c.connection) #only if connection.async
            ret = c.fetchall()
            c.close()
            return ret
        Therefore, the operation must NOT be a query operation (e.g., select is fine, insert/delete not)
        Note also that this method takes care of asynchronous connection by 
        calling the wait function, and blocks
        until the cursor isn't available. For more info, see
        http://initd.org/psycopg/docs/advanced.html#asynchronous-support
    """
    c = cursor(connection, operation, parameters)
    ret = c.fetchall()
    c.close()
    return ret
    
class Connection(object):
    """
        Wrapper class for the psycopg connection class.
        It supports shorthands methods for: 
        the creation of cursor via an execution command:
            cursor = Connection.cursor(operation [,parameters])), 
        the execution of non query commands (e.g., insert delete):
            Connection.execute(operation [,parameters])) 
        and the execution and return of query commands (e.g., select): 
            v = Connection.fetchall(operation [,parameters])
        Plus close() and commit() methods which delegate the relative connection methods
        
        All methods (excluding close) take also care of potential asynchronous connections, waiting (e.g. fetchall) 
        or doing nothing and returning silently (e.g., commit)
        
        If this class is too "hight level" and you know what you are doing, you can always 
        use C by calling Connection.conn
    """
    def __init__(self, host=HOST, dbname=DBNAME, user=USER,  password=PSWD, async=ASYNC):
#        self.host = host
#        self.async = async
#        self.password = password
#        self.dbname = dbname
#        self.user = user
        self.conn = connect(host=host, dbname=dbname, user=user,  password=password, async=async)
        
    def cursor(self, operation, parameters=None):
        """
            See module level cursor function
        """
        return cursor(self.conn, operation, parameters)
    
    def execute(self, operation, parameters=None):
        """
            See module level cursor function
        """
        return execute(self.conn, operation, parameters)
    
    def fetchall(self, operation, parameters=None):
        """
            See module level cursor function
        """
        return fetchall(self.conn, operation, parameters)
    
    @property
    def closed(self):
        return self.conn.closed != 0
    
    def close(self):
        """
            Closes the underlying psycopg connection. Does nothing if the connection is already closed
        """
        if not self.closed:
            self.conn.close()
    
    def commit(self):
        """
            Commits the underlying connection. Does nothing and returns silently if the latter is in async mode
        """
        if not self.conn.async:
            self.conn.commit()
            
    def __del__(self):
        self.close()
    