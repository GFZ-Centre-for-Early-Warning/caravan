#! /usr/bin/python

"""

Module for handling the conversion of character sequences 
(strings or file-like object, including text files, all referred hereafter as 'stream') 
into python objects, by implementing some custom functions for parsing 
streams into (arrays or scalar) of floats, ints, booleans, or more generally
for parsing a stream into tokens of different types (numbers strings, boolean or 
user defined)

Note that the module is compatible in both PY2 and PY3

The module first defines three "base" parse functions ('low' level): 
_default_parseint (same as builtin int, but floats raise exceptions)
_default_parsefloat (same as builtin float, but NaNs raise exceptions)
_default_parsebool ("1", 1, True or "true" - case insensitive, return True, 
                    "0", 0, False or "false" -case insensitive, return False, otherwise
                    raises Exception)


Then, the module defines some utility function for parsing a stream. Note 
that the parse is done by first splitting the stream into tokens, according to 
space characters, separator characters and quote characters. For each token, 
the 'low level' parse function is applied, 
and an array or a scalar (depending on the input) is returned. Any value which is 
not valid (NaN, not parsable, not within a specified range) raises an exception. 
The user can also control the range of the returned array dimension, or 
choose a rounding factor for floats to be applied to any value of the returned 
array. These functions are

parsefloat (calls by default _default_parsefloat)
parseint (calls by default _default_parseint)
parsebool (calls by default _default_parsebool)

and additionally:

parsetime (parses strings in various forms with given separator chars)
parsedate (parses strings in various forms with given separator chars)

Finally, there are two more general utilities which can be applied in more 
general cases for any stream:

parsefield (which is used by all five functions above), which returns the 
tokens of a text field (the name stems from an hypotetic text input field) which 
accepts a parsefunction to be applied to any token to check its validity (or change
its value), and

token: a generator which yields each token of a parsed stream


(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

from __future__ import print_function
from numpy import isscalar

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Oct 22, 2014 11:55:47 AM$"

#import json #,re
from math import isnan #, isinf

import sys
# This module is standalone, therefore we write PY3 compatibility code here
PY3 = sys.version_info[0] == 3
if PY3:
    def isstring(v):
        return isinstance(v, str)
    from io import StringIO
    #from builtins import round as builtin_round #import default float
else:
    def isstring(v):
        return isinstance(v, basestring)
    from StringIO import StringIO 
    #here has been tested that cStringIO StringIO module is "good":
    #see http://www.skymind.com/~ocrow/python_string/
    #However, cStringIO does not support seek and truncate, therefore use StringIO
    #https://docs.python.org/2/library/stringio.html#module-cStringIO
    range = xrange
    #from __builtin__ import round as builtin_round #import default float
    chr = unichr

#from __builtin__ import map as builtin_map #import default float
def _apply(val, func):
    """
        Same as map, but val can be also scalar (returns func(val) in that case)
    """
    return tuple(map(func,val)) if type(val) == tuple else map(func,val) if not isscalar(val) else func(val)

def _default_parseint(val):
    """
        Internal "private" parseint. same as int(val) except that val 
        needs to be an integer and cannot be a float (an exception is thrown in case)
    """
    vi = int(val)
    vf = float(val)
    if vi != vf:
        raise Exception("%s is not an integer " % str(val))
    return vi

def _default_parsefloat(val):
    """
        Internal "private" parsefloat. same as float(val) except that val 
        needs to be nor infinite (positive or negative) neither NaN (an exception is thrown in case)
        If max_decimal_digits is a number greater than zero, rounds the float to the given decimal precision
        so for instance _parsefloat(1.45, 1) = _parsefloat(" 1.45  ", 1) = 1.5
    """
    vf = float(val)
    if isnan(vf):
        raise Exception("value is NaN")
#    elif isinf(vf):
#        raise Exception("value is + or - Infinity")
        
    return vf

_type_float = type(5.0)
_type_int = type(5)

def _default_parsenum(val, decimals=None):
    """
        General purpose parse number function. decimals controls the type of the number returned:
        None (default if missing): smart guess. val is returned if already float or int. Otherwise, 
            val is parsed to both float (val_float) and int (val_int) by using _default_parsefloat and _default_parseint  
            (the former raises exceptions if the parse value is NaN). If val is not parseable to float and int, raises the 
            corresponding exception, if parsable either to float or int, returns the parsed value, if parsable to both, 
            returns val_int if val_int == val_float and val is string with no '.' characters or the 'e' character present.  
            In any other cases, returns the parsed float
        number < -1:  parses to float
        number == -1: parses to int
        number >= 0:  parses to float rounded to the specified number of decimal digits (0 means: round to int, although floats are returned)
    """
    valf= None
    vali = None
    exc = None
    if decimals is None or decimals!=-1:
        try: 
            if _type_float == type(val): return val #check if already float
            valf = _default_parsefloat(val)
            if decimals >=0 : valf = round(valf, decimals)
        except Exception as e: 
            exc = e
            valf= None
    
    if decimals is None or decimals==-1:
        try: 
            if _type_int == type(val): return val #check if already int
            vali = int(valf) if valf is not None else _default_parseint(val)
        except Exception as e: 
            if exc == None: exc = e
            vali= None
    
    if exc is not None: raise exc #either vali, or valf or both are None
    
    #Now either vali, or valf, or both are NON None
    if valf is None and not vali is None: return vali
    elif valf is not None and vali is None: return valf
    
    #if vali == valf then decimals is None (see above) so we can avoid the check in the if
    if vali == valf and isstring(val):
        if val.find('.') < 0 or val.find('e')>=0 or val.find('E')>=0: return vali
        
    return valf

def _default_parsebool(val):
    """
        Parses val to boolean. 
        True is returned if val is the string "true" (case insensitive), "1" or 
        using _default_parseint it evaluates to 1
        False is returned if val is the string "false" (case insensitive), "0" or 
        using _default_parseint it evaluates to 0
    """
    if (val==True or val==False):
        return val
    
    try:
        it = _default_parseint(val)
        if it==1 : return True
        elif it==0: return False
    except:
        if isstring(val):
            v = val.lower()
            if (v=='true' or v=='1'):
                return True
            elif (v=='false' or v=='0'):
                return False
            
    raise Exception("%s not boolean-parsable" % str(val))

def _intervalExc(ret, interval):
    def str_interval(interval):
        return "in the specified range of values (given as function)" if hasattr(interval,"__call__") else \
            ("equal to " if isscalar(interval) else "in ") + str(interval)
    return Exception( "{0} {1} {2}" .format(str(ret) if isscalar(ret) else "array", "not" if isscalar(ret) else "elements not all", str_interval(interval)) )
    
def _dimExc(ret, interval):
    if interval == -1:
        interval = "-1 (scalar)"
        
    ret = str(ret)+" has dimension (-1)" if isscalar(ret) else "array has dimension (python 'len')"
    return _intervalExc(ret, interval)

def _quoteExc(ret, quote_char, type_=None):
    return Exception( "'{0}' {1} {2}" .format(str(ret),"(quoted string) cannot be parsed to", "number" if type_ is None else type_))

pinf = float("infinity") #positive infinity

def numinterval(interval):
    """
        Converts an interval to a numeric interval, replacing None elements with -infinity and +infinity, so that 
        the open (type(interval)=tuple) and closed (type(interval)=list) cases are consistent:
        -float("infinity") must be considered in [None, 3] but not in (None,3)
    """
    if interval is None or isscalar(interval): return interval
    try:
        t = type(interval)
        if t== tuple: interval = list(interval)
        if interval[0] is None: interval[0] = -pinf
        if interval[1] is None: interval[1] = pinf
        if t==tuple: interval = tuple(interval)
        return interval
    except:
        return interval

def parseint(val, interval=None, dim=None, parsefunc = None):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_sep (default: {',',';'})
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then converts each token to int acccording to parsefunc
        
        Returns either an int (e.g. val="12"), a tuple (val = "(1, 3)") or a list 
        (val="[1e5]" but also val = "1 3 4")
        Raises an exception if 
        - interval is specified as a 2 elements tuple (open interval) or list 
            (closed interval) and any token is not in the interval
        - dim is specified as a 2 elements tuple (open interval) or list 
        (closed interval) and the returned element length is not int dim
        
        NOTE: interval and dim can also be functions: in case, they must accept 
        a single argument and return True or False (argument inside or outside interval). 
        
        - if parsefunc raises an exception. parsefunc accepts two arguments: 
        the token string, and its type (None for any token except quoted strings, 
        in that case it is the quoted character). By default (missing or None), 
        it uses the module-level function _default_parseint which raises exceptions 
        if a token is a non-integer float, is not parsable to int or represents 
        a quoted string token (interpreted as a user will of specifying a string 
        type only) 
    """
    
    if parsefunc is None: #default parse function
        def parsefcn(val, quote_char):
            if quote_char: raise _quoteExc(val, quote_char, "integer")
            return _default_parseint(val)
        parsefunc = parsefcn
    
    
    interval = numinterval(interval)
    def pfcn(val, quote_char):
        val = parsefunc(val, quote_char)
        if not isin(val, interval): raise _intervalExc(val, interval)
        return val
        
    val = parsefield(val, parsefunc=pfcn)
    if dim is not None and not isdim(val, dim): raise _dimExc(val, dim)
    return val

def parsefloat(val, decimals=None, interval=None, dim=None, parsefunc = None):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_sep (default: {',',';'})
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then converts each token to float acccording to parsefunc
        
        Returns either an int (e.g. val="12.1"), a tuple (val = "(1, 3.3)") or a list 
        (val="[1e-10]" but also val = "1.2 3.001 4")
        Raises an exception if 
        - interval is specified as a 2 elements tuple (open interval) or list 
            (closed interval) and any token is not in the interval. 
        - dim is specified as a 2 elements tuple (open interval) or list 
        (closed interval) and the returned element length is not int dim. If the 
        element is "scalar" (it does not have an "__iter__" method) then its length 
        is assumed to be -1
        
        NOTE: interval and dim can also be functions: in case, they must accept 
        a single argument and return True or False (argument inside or outside interval).
        interval and dim can be None to specify "skip the check". interval values 
        which are None default to -infinity (index 0) and + infinity (index 1)
        
        decimals is the number of decimal digits each float must be rounded to. 
        It can be greater or equal to zero, otherwise it is ignored
        
        - if parsefunc raises an exception. parsefunc accepts two arguments: 
        the token string, and its type (None for any token except quoted strings, 
        in that case it is the quoted character). By default (missing or None), 
        it uses the module-level function _default_parsefloat which raises exceptions if 
        a token is NaN, is not parsable to float or represents a quoted string 
        token (interpreted as a user will of specifying a string type only) 
    """
    if parsefunc is None: #default parse function
        def parsefcn(val, quote_char):
            if quote_char: raise _quoteExc(val, quote_char, "float")
            return _default_parsefloat(val)
        parsefunc = parsefcn
    
    interval = numinterval(interval)
    def pfcn(val, quote_char):
        val = parsefunc(val, quote_char)
        if not isin(val, interval): raise _intervalExc(val, interval)
        return val if decimals < 0 else round(val, decimals)
        
    val = parsefield(val, parsefunc=pfcn)
    if dim is not None and not isdim(val, dim): raise _dimExc(val, dim)
    return val

def parsenum(val, decimals=None, interval=None, dim=None):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_sep (default: {',',';'})
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then converts each token to numbers acccording to _default_parsenum
        
        Returns either an int (e.g. val="12.1"), a tuple (val = "(1, 3.3)") or a list 
        (val="[1e-10]" but also val = "1.2 3.001 4")
        Raises an exception if 
        - interval is specified as a 2 elements tuple (open interval) or list 
            (closed interval) and any token is not in the interval. 
        - dim is specified as a 2 elements tuple (open interval) or list 
        (closed interval) and the returned element length is not int dim
        
        NOTE: interval and dim can also be functions: in case, they must accept 
        a single argument and return True or False (argument inside or outside interval). 
        
        - if _default_parsenum raises an exception. _default_parsenum is a function 
        which controls how numbers are returned, and uses the argument decimals, which is therefore
        more powerful than the decimals argument in the parsefloat module-level function.
        If decimals is:
        None (default if missing): smart guess: Each token is returned if already float or int. Otherwise, 
            it is parsed to both float (val_float) and int (val_int) by using _default_parsefloat and _default_parseint  
            (the former raises exceptions if the parse value is NaN). If the token is not parseable to float and int, raises the 
            corresponding exception, if parsable either to float or int, returns the parsed value, if parsable to both, 
            returns val_int if val_int == val_float and val is string with no '.' characters or the 'e' character present.  
            In any other cases, returns the parsed float
        number < -1:  parses each token to float
        number == -1: parses each token to int
        number >= 0:  parses each token to float rounded to the specified number of decimal digits (0 means: round to int, although floats are returned)
    """
     
    def parsefcn(val, quote_char):
        if quote_char: raise _quoteExc(val, quote_char, "float")
        val = _default_parsenum(val, decimals)
        if not _isin(val, interval): raise _intervalExc(val, interval)
        return val
        
    val = parsefield(val, parsefunc=parsefcn)
    if dim is not None and not isdim(val, dim): raise _dimExc(val, dim)
    return val

def parsebool(val, parsefunc=None, dim=None):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_sep (default: {',',';'})
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then converts each token to boolean acccording to parsefunc
        
        Returns either an int (e.g. val="true"), a tuple (val = "(1, false)") or a list 
        (val="[True]" but also val = "1 True, false")
        Raises an exception if parsefunc raises an exception. parsefunc accepts 
        two arguments: the token string, and its type (None for any token except 
        quoted strings, in that case it is the quoted character). By default 
        (missing or None), it uses the module-level function _default_parsebool 
        which raises exceptions if a token is not 1, "1", "true" (case insensitive), 
        0, "0" or "false" (case insensitive) or represents a quoted string 
        token (interpreted as a user will of specifying a string type only) 
    """
    if parsefunc is None:
        def parsefcn(val, quote_char):
            if quote_char: raise _quoteExc(val, quote_char)
            if parsefunc: val = _default_parsebool(val)
            return val
        parsefunc = parsefcn
        
    val = parsefield(val, parsefunc=parsefcn)
    if dim is not None and not isdim(val, dim): raise _dimExc(val, dim)
    return val
    
def parsestr(val, parsefunc=None, dim=None):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_sep (default: {',',';'})
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then returns each token (quoted strings will be unquoted and unescaped)
        
        Returns either a string (e.g. val="a string"), a tuple (val = "(1, 'false')") 
        or a list (val="[True]" but also val = "'my little string', 'false'")
        Never raises exceptions, as each token is a string, unless the user 
        defines a parse function by means of parsefunc. parsefunc accepts 
        two arguments: the token string, and its type (None for any token except 
        quoted strings, in that case it is the quoted character). As said, 
        by default (missing or None), no function is called and no exception is thrown 
    """
    val = parsefield(val,parsefunc = parsefunc)
    if dim is not None and not isdim(val, dim): raise _dimExc(val, dim)
    return val

_default_datesep = {'-',"/", "."}

from datetime import date, datetime, timedelta
def _dateexc(val): return Exception("invalid date: '{0}'".format(str(val)))

def parsedate(val, separator_chars = _default_datesep, formatting='', round_ceil=False, empty_date_today = False, parsefunc=parseint):
    """
        Parses val (either a string or file-like object) into tokens (see 
        module-level 'token' function) according to: 
        _default_datesep = {'-',"/", "."} as separator characters
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
       
        and then converts the tokens to (and returns) a python datetime (contrarily 
        to the module-level functions parseint, parsefloat and parsebool, this 
        function never returns a list or tuple)
        
        separator_chars (_default_datesep) can be customized and  denotes the separator 
        characters for each date field (year, month and day). 
        
        formatting is a string denoting the date formatting (defaults to '' if missing), and 
        round_ceil (false if missing) tells whether the returned datetime  
        should be rounded up or down in all unspecified fields. This means that
        IN ANY CASE the time of the returned date will be either 00:00:00 (and 0 microseconds) 
        if round_ceil is False or missing (the default), or 23:59.59 (and 999999 microseconds) 
        if round_ceil is True. Months and days might be also rounded acccording 
        to format.
        
        Example:
        Calling Y and M the current year and month (today().year and today().month)
        and representing heach datetime as 
        year-month-day hours:minutes:seconds.microseconds
        then the list of tokens t parsed from the input val is returned as:
        
        formatting                round_ceil=False        round_ceil=True
                                  (or missing)        
         
        'y' or                    t[0]-1-1 0:0:0.0        t[0]-12-31 23:59.59.999999
        missing and len(t)==1   
        
        'm'                       Y-t[0]-1 0:0:0.0        Y-t[0]-X 23:59.59.999999   
                                                          (X in {31, 30, 28} depending on t[0])
                                                          
        'd'                       Y-M-t[0] 0:0:0.0        Y-M-t[0] 23:59.59.999999
                                               
        'ym' or                   t[0]-t[1]-1 0:0:0.0     t[0]-t[1]-X 23:59.59.999999
        missing and len(t)==2                             (X in {31, 30, 28} depending on t[1])
        
        'my'                      t[1]-t[0]-1 0:0:0.0     t[1]-t[0]-X 23:59.59.999999
                                                          (X in {31, 30, 28} depending on t[0])
        
        'md'                      Y-t[0]-t[1] 0:0:0.0     Y-t[0]-t[1] 23:59.59.999999
        
        'dm'                      Y-t[1]-t[0] 0:0:0.0     Y-t[1]-t[0] 23:59.59.999999
        
        'ymd' or                  t[0]-t[1]-t[2] 0:0:0.0  t[0]-t[1]-t[2] 23:59.59.999999
        missing and len(t)==3
        
        'dmy'                     t[2]-t[1]-t[0] 0:0:0.0  t[2]-t[1]-t[0] 23:59.59.999999
        
        This function raises an exception if any token is not int-parsable 
        (according to the module-level function _default_parseint, which by default 
        includes the case of float-parsable strings), if any integer is invalid in the 
        specified range (e.g., months or days) or, in case formatting is specified, 
        if the token number does not match the expected token numbers of formatting
    """
    
    ret = parsefield(val, separator_chars=separator_chars, parsefunc = parsefunc) #which returns ret if val is not a string
    
    if isscalar(ret): ret = [ret] if ret else []
    if len(ret)==0:
        if empty_date_today: return datetime.today()
        raise _dateexc(val)
    
    if not formatting:
        if len(ret)==1: formatting='y'
        elif len(ret)==2: formatting='ym'
        elif len(ret) == 3: formatting='ymd'
        else: raise _dateexc(val)
    
    if len(formatting) != len(ret):
        raise _dateexc(val)
    
    #default values:
    m,d,h,mm,s,ms= (1,1,0,0,0,0) if not round_ceil else (12, 31, 23, 59, 59, 1000000-1)
    
    if formatting == 'y': return datetime(ret[0],m,d,h,mm,s,ms)
    elif formatting == 'dmy': return datetime(ret[2],ret[1],ret[0],h,mm,s,ms) 
    elif formatting == 'ymd': return datetime(ret[0],ret[1],ret[2],h,mm,s,ms)
    else:
        ret_date = None
        if formatting == 'ym': ret_date = datetime(ret[0],ret[1], 1,0,0,0,0)
        elif formatting == 'my': ret_date = datetime(ret[1],ret[0], 1,0,0,0,0)
        else:
            t = date.today()
            if formatting == 'm': ret_date = datetime(t.year,ret[0],1,0,0,0,0)
            elif formatting == 'md': return datetime(t.year, ret[0],ret[1], h,mm,s,ms)
            elif formatting == 'dm': return datetime(t.year, ret[1],ret[0], h,mm,s,ms)
            elif formatting == 'd': return datetime(t.year, t.month, ret[0], h,mm,s,ms)
        
        if ret_date is None: raise _dateexc(val)
        
        if round_ceil:
            #in thi case we need to go up one month, and then substract one millisecond
            #Getting till the end of the specified month iss too complex with integers 
            #(what about bisestiles years if we are the 28th of february?)
            y = ret_date.year+1 if ret_date.month == 12 else ret_date.year
            m = 1 + (ret_date.month  % 12) #basically ret_date.month+1 unless ret_date,month=12
            ret_date = datetime(y, m, 1, 0,0,0,0) - timedelta(0,0,1) #1 microsecond
        
        return ret_date
        

_default_timesep = {':',"-", "."}
from datetime import time
def _timeexc(val): return Exception("invalid time: '{0}'".format(str(val)))
def parsetime(val, separator_chars = _default_timesep, round_ceil=False, empty_time_now = False, parsefunc = parseint):
    """
        Parses val (either a string or file-like object) into tokens according to 
        _default_timesep = {':',"-", "."} as separator characters
        _default_quote (default: {'"',"'"})
        _default_ws = (default: set([chr(i) for i in range(33)]))
        (see module-level token function)
        and then converts the tokens to a python time, returning it (contrarily 
        to the module-level functions parseint, parsefloat and parsebool, this 
        function never returns a list or tuple)
        
        separator_chars (_default_timesep) can be customized and denotes the separator characters 
        for each date field (hours, minutes and seconds). Called t the list of 
        parsed tokens (as integers, using the module-level function _default_parseint), 
        time as the python time() function (current time) and denoting the 
        times below in the standard format HH:MM:SS, the returne value is
        
        time            if no token is found (e.g., empty string)
        t[0]:M:S.MS      if len(t) == 1 
        t[0]:t[1]:S.MS    if len(t) == 2
        t[0]:t[1]:t[2].MS  if len(t) == 3
        
        where M, S, MS are zero if round_ceil is False, else 59,59, 999999 respectively
        (set missing fields to their maximum which preserve the given input fields)
        
        This function raises an exception if any token is not int-parsable 
        (according to the module-level function _default_parseint, which by default 
        includes the case of float-parsable strings) or if any integer is invalid in the 
        specified range
    """
    m,s,ms = (59, 59, 1000000-1) if round_ceil else (0, 0, 0)
    ret = parsefield(val, separator_chars=separator_chars, parsefunc = parsefunc) #which returns ret if val is not a string
    if isscalar(ret): ret = [ret] if ret else []
    if len(ret)==0: 
        if empty_time_now: return time()
    elif len(ret)==1: return time(ret[0],m,s,ms)
    elif len(ret)==2: return time(ret[0], ret[1], s ,ms)
    elif len(ret) == 3: return time(ret[0], ret[1], ret[2], ms)
    raise _timeexc(val)


def isscalar(value):
    """
        Returns if value is a scalar value, i.e. it is not an iterable. Thus, numbers, string, dates, times and boolean are scalar, list and tuples not
    """
    return not hasattr(value,"__iter__")

def _isin(val, interval):
    """
        Returns true if the number val is in interval. Interval can be: 
        2-element list (math closed interval), 
        2-element tuple (math open interval),
        a "scalar" number N (equivalent to [N,N])
        a function: in case, it must accept a single argument and return True or False (argument inside or outside interval). 
            so that interval= lambda x: x>1 and x <3 is equivalent to interval=(1,3)
        If interval is None, this function returns True. 
        For any other value of interval which is not a 2-element tuple or list, this method returns False.
        If tuple or list, interval can contain None values, they will default to -Infinity (for interval[0]) or +Infinity (for interval[1])
        Examples:
        isin(7.8, [5, None]) returns True
        isin(7.8, [7.8, None]) returns True
        isin(7.8, (7.8, None)) returns False
        isin(n, (None, None)) = isin(n, None) returns True for any number n
    """
    i = interval #just for less typing afterwards...
    if i is None:
        return True
    
    if hasattr(interval, "__call__"):
        return interval(val)
    
    if isscalar(interval):
        return val == interval
        
    t = type(i)
    return (i[0] is None or val > i[0]) and (i[1] is None or val < i[1]) if (t==tuple and len(i)==2) else \
        ((i[0] is None or val >= i[0]) and (i[1] is None or val <= i[1]) if (t==list and len(i)==2) else False)

def isin(val, interval):
    """
        Returns True if val is in interval.
        interval can be a 2-element tuple (open interval) or list (closed interval), 
        or a function. In the latter case, it must accept a single argument A and return 
        True (A inside interval) or False (A outside interval). val can also be a 
        generator (including list or tuples), in that case the function iterates 
        over each val element and returns True if all elements are in interval.
        If interval is None, this function returns True. if any interval element 
        at index 0 or 1 is None, it is skiiped (so that, e.g., for numbers, [None, -3] 
        is basically equivalent to [-infitnity, -3] or to the assertion "val must be <= -3")
    """
    if interval is None: return True
    
    if not isscalar(val):
        for v in val:
            if not _isin(v, interval): return False
        return True
    
    return _isin(val, interval)

def isdim(val, interval):
    """
        Returns True if the val 'dimension' (python len(val) function) is in interval. 
        If val has is an iterable without a length, raises an Exceptions. 
        Otherwise, if val is scalar (e.g., simple number, but also string), then 
        its dimension is considered -1.
        interval can be a 2-element tuple (open interval) or list (closed interval), 
        or a function. In the latter case, it must accept a single argument A and 
        return True (A inside interval) or False (A outside interval). If interval 
        is None, this function returns True. if any interval element at index 0 or 1 
        is None, it is skiiped (so that, e.g., for numbers, [None, -3] is basically 
        equivalent to [-infitnity, -3] or to the assertion "val must be <= -3")
    """
    if interval is None: return True
    dim = -1
    if not isscalar(val) and hasattr(val, "__len__"):
        dim = len(val)
    return _isin(dim, interval)
    
#    if scalar and _isin(-1, interval): return True
#    leng = 0 if val is None else 1 if scalar else len(val)
#    return _isin(leng, interval)


_default_sep = {',',';'}
_default_quote = {'"',"'"}
_default_ws = set([chr(i) for i in range(33)])

def parsefield(s, separator_chars = _default_sep, quote_chars=_default_quote, whitespace_chars=_default_ws, parsefunc = None):
    #Note: parseFunc takes the token (parsed) and the type (None for normal token, the quote char for quoted token)
    """
        Parses a field string (such as an html input value) into tokens, returning 
        the array of tokens. Note that this method is not optimized for parsing long strings. 
        The type of each token can be specified by parsefunc 
        (if None, all tokens will be strings). If s is not a string, iterates over its elements 
        (if iterable) or over s itself, applying parsefunc to any iterated element
        
        Retuns a list, a tuple or a single element according to the input value type. 
        With default settings, assuming no parsefunc:
        
        s                       returned value
        "4"                     "4" 
        "4 True" or "[4 True]"  ["4", "True"]
        "(4,True)"              ("4", "True")
        Any iterable            returns an iterable (tuple if tuple, list in any other case) with the same elements
        Any other value         returns the value
        
        
        By default, this method detects and returns more than one token if commas,
        or spaces (not whithin quoted strings) are found, or alternatively the 
        string starts and ends with '[' and ']' (a list is returned or 
        '(' and ')' (a tuple is returned). In any other case, a scalar (string, 
        number, boolean or any other object) is returned
        
        separator_chars, quote_chars and whitespace_chars are respectively 
        _default_sep, _default_quote and _default_ws, and are documented in the 
        module level function token. 
        Provide sets of characters (1-length strings) to slightly improve performances, if needed.
        
        parsefunc is a function accepting two arguments: the token parsed (string) 
        and the type, which is None unless the token is a quoted string (in that case t is the 
        quote character). It will then return the object to be returned. It can raise
        Exceptions for non parsable tokens: for instance, a parsing process which 
        expects all numbers might rais one surely if the argument t is not None 
        (quoted strings found), or try to parse to int if, for instance, "7.54" 
        has to be considered as number
    """
    
    t=None
    if isstring(s):
        i=0
        l = len(s)
        while i<l and s[i] in whitespace_chars:
            i+=1
        
        if i<l and (s[i]=='[' or s[i]=='('):
            j=l-1
            while j>i and s[j] in whitespace_chars:
                j-=1
                
            if (s[i]=='[' and s[j]==']') or (s[i]=='(' and s[j]==')'):
                t = list if s[i]=='[' else tuple
                s = StringIO(s)
                s.seek(i+1)
                s.truncate(j)
    else:
        if isscalar(s): t=None
        else: t=tuple if type(s)==tuple else list
        
    res =[]
    if parsefunc:
        for v, q in token(s, separator_chars, quote_chars,whitespace_chars, parse_num=None, parse_bool=None):
            #if q is None and not v: v = None
            #print("tokena:" + str(v)+" "+str(parsefunc(v,q)))
            res.append(parsefunc(v,q))
    else:
        for v, q in token(s, separator_chars, quote_chars,whitespace_chars, parse_num=None, parse_bool=None):
            res.append(v)
            #res.append(None if q is None and not v else v)
    
    if t is None:
        l = len(res)
        if l==0: res = ''
        elif l==1: res = res[0]
    elif t==tuple:
        res = tuple(res)
    
    #print("A "+str(res))
    #res = res[0] if t is None and len(res)==1 else tuple(res) if t==tuple else res
    return res

#adjacent wspaces are ignored if they follow or preceed a separator char, otherwise they are treated as sep char
#separator chars simply separate tokens
#quote chars 
def token(s, separator_chars = _default_sep, quote_chars= _default_quote, whitespace_chars=_default_ws, 
parse_num = _default_parsefloat, parse_bool = _default_parsebool):
    """
    Parses s into tokens, returning a generator which can be used in a loop. 
    The generator returns the tuple (token, quoted) where token can e either string, 
    number or boolean (depending on the parameters) and quoted is non None only 
    for quoted strings, to distinguish them from unquoted strings.
    
    Example with default arguments:

        for v, t in token('a true 1.1e3 "quote with space"'):
            #will return:
            #v = 'a' (string), t = None (no quote)
            #v = True (boolean), t = None
            #v = 1100 (integer), t = None
            #v = 'quote with spaces' (string), t = '"'

    Arguments: 

    s the string or file-like object (i.e., with a read method which, with argument 
        1, returns a character) to be tokenized
    separator_chars ({',', ';'} by default): denotes the separator characters, i.e. 
        those characters which separate tokens, and are never included in the latter
    whitespace_chars ({chr(0), ..., chr(32)} by default): denotes whitespace characters, 
        i.e. "second citizen" separator characters, as they differ from the former in 
        two things:
        1) one or more adjacent whitespaces are treated as a single whitespace block
        2) any block of whitespaces which preceeds or follows a separator character is 
            simply ignored (as nothing was typed)
        Thus, with the default settings "a b" and "a , b" both return the tokens 'a' and 'b'
    quote_chars ({',', "'"} by default): specifies the quote characters, i.e. characters 
        that need to denote strings to be returned as they are, after being unquoted. 
        The characters backslash+'n', backslash+'r' and backslash+'t' are returned as nelwine, 
        carriage return and tab, respectively. End-of-lines ('\r' or '\n') 
        found (or end-of-stream reached) while parsing a quoted string will raise Exceptions
    parse_num: (default: _default_parse_float), if specified, it must be a function 
        which takes the token and parses into number. For every token found, the 
        function is run and the relative number is returned. If the function raises 
        exceptions or is not specified, all tokens will be returned as strings 
        (unless the parse_bool function is specified, see below)
    parse_bool: (default: _default_parse_bool), if specified, it must be a function 
        which takes the token and parses into boolean. For every token found, the 
        function is run (AFTER parse_num, if the latter is specified) and the 
        relative boolean is returned. If the function raises exceptions or is not 
        specified, all tokens will be returned as strings (unless the parse_num function 
        is specified, see above)

    NOTE ON parse_bool and parse_num: Quoted tokens, i.e. tokens parsed as 
        string within quote_chars, will not be affected by the parse process 
        and always returned as strings
        
    """
    
    if not isstring(s) and not hasattr(s,"read"):
        if not hasattr(s, "__iter__"):
            yield s, None
        else:
            for v in s:
                yield v, None
        return
            
    if isstring(s):
        s = StringIO(s)
        
    if not hasattr(s, "read"): #for safety
       raise Exception("invalid token argument, must implement the read method")
   
    if not isinstance(separator_chars, set):
        separator_chars = set(separator_chars)
    if not isinstance(quote_chars, set):
        quote_chars = set(quote_chars)
    if not isinstance(whitespace_chars, set):
        whitespace_chars = set(whitespace_chars)
    
    #convert s into a list of strings, where quotes are NOT touched:
    buf = None
    found_ws = False
    last_char_is_sep = False
    c = s.read(1)
    quote_char = ''
    
    def add(c, buf):
        if not c: return
        if not buf: buf = StringIO()
        #print('adding {}'.format(c))
        buf.write(c)
        return buf
    
    def data(quote_char=None):
        if not buf: return '', quote_char or None
        v = buf.getvalue()
        buf.close()
        if quote_char: return v, quote_char
        #buf = None
        if parse_num:
            try: return parse_num(v), None 
            except: pass
        if parse_bool:
            try: return parse_bool(v), None 
            except: pass
        return v, None    
                
    while c:
        if quote_char:
            if c==quote_char:
                quote_char = ''
                yield data(c)
                buf = None
                c = s.read(1)
                continue    
            elif c=='\\':
                c = s.read(1)
                if c=='n': c = '\n'
                elif c=='r': c = '\r'
                elif c=='t': c = '\t'
            elif c=='\n' or c=='\r':
                raise Exception("Unclosed quoted string '{0}' (end-of-line found)".format(buf.getvalue()))
            buf = add(c, buf)
            c = s.read(1)
            continue
            
        if c in whitespace_chars:
            if not found_ws: found_ws = True
            c = s.read(1)
            continue
        
        ws_found = found_ws #used below, we can't rely on found_ws cause we need to set it to false now 
        #in order to avoid to set it in all if below.
        found_ws = False
        
        if c in separator_chars:
            yield data()
            buf = None
            c = s.read(1)
            #was the last character?
            if not c:
                #add another token: (e.g., '(4,5,)'. Note that this is not the
                #Python syntax but if more conistent, and avoids '[,]' to be equal to '[]'
                yield data()
                buf = None
                #we will exit the loop now
            continue    
        
        if ws_found:
            if buf:    
                yield data()
                buf = None
        
        if c in quote_chars and not buf:
            quote_char = c;
            c = s.read(1)
            continue
        
        buf = add(c, buf)
        c = s.read(1)
            
    if buf: 
        if quote_char:
            raise Exception("Unclosed quoted string '{0}' (end-of-stream found)".format(buf.getvalue()))
        #print('accusi')
        yield data()
    
    return
#    if hasattr(s, "close"):
#        s.close()

def _ps(arr):
    s = str(type(arr)) +": "+ '|'.join([str(s)+" ("+str(type(s))+")" for s in arr]) if hasattr(arr,"__len__") and not isstring(arr) else \
        "'"+str(arr)+"' ("+str(type(arr))+")" if isstring(arr) else str(arr)+" ("+str(type(arr))+")"
    print(s)
    
if __name__ == "__main__":
    
    print(str(parsefield('2014',parsefunc=parseint)))
    
#     
#     s=[
#         " 14:00 , [asd, d gtr;],  asd ",
#         [3,4,5],
#         " 3.4445666 4 , 5",
#         " 3.4445666 14 , 5",
#         " 0.1 0.4 , 0.5  ",
#         "",
#         "  ",
#         "  \"asd , asd",
#         "\"asd ,\" asd",
#         "1 , false",
#         "[1.23]",
#         "(1.23, -4)",
#         "1.12"
#     ]
#     
#     for ss in s:
#         _ps(ss)
#         try:
#             sss = parsefloat(ss, decimals=1, interval=[-10,10], dim=[0,3])
#         except Exception as e:
#             import traceback
#             #traceback.print_exc()
#             sss = e
#         _ps(sss)
#         print("\n")