#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
    Micro-micro WSGI web framework. 
    Supports both Python 2 and 3 (Tested on 2.7.6 and 3.4.0)
    
    The framework supports get, post, json input and output, as well as static files 
    (e.g., images, text, whatever) transmission from client to server (and viceversa).
    No cookies, no sessions, nothing else supported: this is a lightweight basic 
    framework not suited for big applications: it was assembled due to the 
    increasing needs of some web projects which on the other hand did not require 
    the implementation (and learning costs) of big web frameworks. 
    The code is the result of several refinements and learned-from-scratch steps: 
    the source is intentionally over-documented also to leave the 'learning history' untouched, 
    both for the author (in case of code updates) but also for potential external users, 
    including wsgi newbies for which this module might be a good and clearer first step. 
    
    The code here has been improved thanks to stackoverflow posts as well as 
    bottle.py and WebOp web frameworks. The syntax follows Flask and Bottle 
    frameworks
    
    ====USAGE==================================================================
    
    Simple example "myapp.py" (detailed below): in principle, 
    The user has to create a new App, and create routes, 
    i.e. map urls (strings or regular expressions) to functions returning 
    the request response body which will be passed to the client:
    
    +--------------------------------------------------------------------------+
    | import wsgi #import module                                               |
    | app = wsgi.App() #init our web app                                       |
    |                                                                          |
    | #add routes                                                              |
    |                                                                          |
    | #what to do with the "main page":                                        |
    | @app.route('index.html', {'Content-Type':'text/html;charset=utf-8'})     |
    | def post_fcn(request, response):                                         |
    |    #implement your body function here, e.g:                              |
    |    return \"\"\"                                                            |
    |           <form type='post' action='post_form' target=result>            |
    |           type a value: <input type='text' name=form_value value='2'>    |
    |           </form>                                                        |
    |           <iframe name=result></iframe>                                  |
    |           \"\"\"                                                            |
    |                                                                          |
    | #what to do with post_form above, when submitted?                        |
    | #note: missing url defaults to the function name below 'post_form'       |
    | @app.route(headers={'Content-Type':'text/html;charset=utf-8'})           |
    | def post_form(request, response):                                        |
    |    #implement your body function here, e.g:                              |
    |    return \"\"\"                                                            |
    |           form submitted with value {0}                                  |
    |           \"\"\".format(request.post['form_value'][0])                      |
    |                                                                          | 
    +--------------------------------------------------------------------------+ 
     
    (see below for a more detailed explanation of the route decorators) 
    When implemented with given routes, the web app is ready to be called by  
    a wsgi server, or a simple python server, for instance this runs your 
    app (supposing it is implemented in myapp.py):
    
    +--------------------------------------------------------------------------+
    | from miniwsgi import run                                                 |
    | from myapp import app                                                    | 
    |                                                                          |
    | miniwsgi.run(app) #opens localhost/index.html in the default browser     |
    +--------------------------------------------------------------------------+
    
    Either 'from myapp import ...' or 'import myapp' will automatically
    add the given routes to app. It is therefore best practice to implement all 
    routes in the module where your app resides in order to automatically 
    setup your app when you import it (otherwise you need more imports 
    before calling miniwsgi.run)
    
    A wsgi application (including our app) is an object with a __call__ method, 
    i.e. it behaves like a Python function. It is called whenever a request is 
    made from the client, and receives an environment dictionary of request properties. 
    The environment (referred as environ here) owns all data necessary to process 
    the response. The wsgi app retrieves the url, looks for an implemented url and, 
    if found, then calls the relative body function (see two examples above) 
    which must return the response body to be sento to the client in one of these 
    forms:
        file-like objects (use open(file,'rb'), providing a reponse 
            charset in the response headers, in case of text files)
        bytes or strings (string means unicode objects in Python<3), 
        iterable of bytes or strings (including tuples and lists) 
    
    Additionally, the body function might also want to modify the response headers 
    and status from within its body. The response is passed as second argument 
    to each body function and it represented by a miniwsgi.Response object, a 
    dict-like object of response headers (always strings. E.g.: 
        response['Content-length'] = str(45)). 
    It is initialized with the headers argument of the decorator, if any 
    ({'Content-Type':'text/html;charset=utf-8'} in the example). It has 
    also a status property which can be set or return the response status to be 
    sent back to the client. See the http.client module (httplib in Python<3) 
    for a set of common status
    
    The first argument passed to each body function is a miniwsgi.Request object 
    representing the request from the client, and has several methods 
    to get the client data such as request.post, request.body, request.get, 
    request.json, request.url, request.environ
    
    For each route mapping an url to a sserver response, both request and a response 
    objects are internally stored within the app and are re-initialized automatically 
    from within the App __call__ body before calling the body function
    
    Notes:
    
    In general, the user does not have to care about 'static' files, i.e. when the response 
    body is a pyhisical existing file to be sent to the client (e.g., *.js, *.css, images)
    as this case is handled by the app. The user may choose to treat the main 
    html page as static (thus, doing nothing) or implementing a decorator if the 
    page must be dynamic (including the case it loads an html file but modifies it)
   
    The response content-type should always be speccified, wither as route 
    decorator argument, or within body_func. For text files, also a charset 
    might be important:
    
    IT IS HIGHLY RECOMMENDED TO USE UTF-8 ONLY AS THE ENCODING FOR ALL YOUR TEXT 
    FILES or strings to be sent and got to or from the client, as utf-8 is almost 
    standard (as of end 2014) and covers almost all user and internationalization needs. 
    
    The character encoding is handled by the app in two ways:
        For static files whose content type starts with 'text/' without charset set, 
    'utf-8' is automatically set. The client then knows that those bytes have to 
    be decoded following the given charset. 
    
    For any non-static returned body which is string, (including strings elements 
    of lists or tuples), the object returned by the body function will be encoded 
    into bytes following the response charset, which defaults to 'utf-8' if missing. 
    Note that if you are a Python<3 user, strings means unicode. In python 2 bytes 
    and strings are the same, so if we have byte strings we just send them as they are, 
    crossing the fingers :-)
    
    The response content-length is not mandatory and will automatically be calculated 
    and set (thus overridden) by the app if the body function returns bytes, strings, 
    tuples and lists. For "generic" iterables the assumption is that the user wanted 
    to return an iterable not list nor tuple (e.g., avoid memory leaks), so the 
    content length (which by the way, is not mandatory in a wsgi specification) 
    is either set by the user in the body function, or will be missing
    
    The arguments of the route decorator are both optional but when given must be:
        url (string or regular expression)
        headers (dictionary of string keys and string values)
    
    The route decorator can be specified in several ways: 
    @app.route      #maps the following decorated function name to itself
    @app.route(var) #as above, if args is a dict (it will be set as headers dict)
                    #otherwise, maps var to the function body
    @map.route(url, headers) #self explanatory
    @map.route(url='..', headers='...') #self-explanatory
    
    
    (c) 2014, GFZ Potsdam

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation; either version 2, or (at your option) any later
    version. For more information, see http://www.gnu.org/
"""

#Question: is it harmless in python3??
#We cannot put this import in the if below cause it must be the first statement in the module (argh!)
from __future__ import print_function #this makes print() also work in python<3

#with the above import, we can define:
def debug(msg):
    print(msg)

__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="$Jun 23, 2014 1:15:27 PM$"

#TERMINOLOGY:
#Request : From Client to Server
#Response: From Server to Client
#Server: Receive Request and Send Response
#Client: Send Request and Receive Response


_DEBUG_ = True; #debug variable, as of Juli 2014 it controls whether exceptions should be printed on terminal, along with other messages

#Code copied from WebOP:

import sys
# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

from io import BytesIO
#pragma: no cover apparently tells coverage to ignore the line to not pollute the reposrts with uneusefu sruff
#see http://stackoverflow.com/questions/11992448/pragmas-in-python for the question,
#http://nedbatchelder.com/code/coverage/ (coverage) and
#http://nedbatchelder.com/code/coverage/excluding.html (excluding code from coverage) for details
if PY3: # pragma: no cover
    import http.client as httplib
    string_class = str
    from urllib.parse import parse_qsl
    _range_ = range
    #integer_class = int,
    #class_types = type,
    #text_class = str
    #long = int
else:
    import httplib
    string_class = basestring
    from urlparse import parse_qsl
    _range_ = xrange
    #integer_class = (int, long)
    #class_types = (type, types.ClassType)
    #text_class = unicode
    #long = long

try: import simplejson as json #see http://stackoverflow.com/questions/712791/what-are-the-differences-between-json-and-simplejson-python-modules
except ImportError: import json

from collections import OrderedDict
import os
import traceback
import re
import email.utils
import time
import cgi
from wsgiref.util import FileWrapper

#To implement classes, we should start a server with a given application(environ, start_response), with an iterable class 
#(which implements the __iter__(self) method, or with a class which implements the __call__(environ, start_response) method
#See http://legacy.python.org/dev/peps/pep-0333/#the-application-framework-side (quite confusing in my opinion)
#and the second answer to this topic: http://stackoverflow.com/questions/21059640/wsgiref-error-attributeerror-nonetype-object-has-no-attribute-split

#STATIC METHODS:

def escape(string, quote=True): #calls the relative PY2 and PY3 library, defined as htmllib (see above)
    """
        Replace special characters "&", "<" and ">" to HTML-safe sequences.
        If the optional flag quote is true (the default), the quotation mark
        characters, both double quote (") and single quote (') characters are also
        translated. It basically calls the python escape function which is located differently 
        in PY2 and PY3
    """
    #Read also here http://stackoverflow.com/questions/19803741/decoding-html-entities-in-python2
    #which btw instantiates new classes for such a "simple" job, so I prefer my solution
    #NOTE: the two functions below (see urls) do almost the SAME THING!
    if PY3:
        import html as htmllib
        #see https://hg.python.org/cpython/file/3.4/Lib/html/__init__.py#l12
        return htmllib.escape(string, quote)
    else:
        ret = cgi.escape(string, quote)
        #cgi does not escape "'". See https://hg.python.org/cpython/file/2.7/Lib/cgi.py#l1039
        if quote: ret = ret.replace('\'', "&#x27;")
        return ret

def unescape(string):
    """
    Convert all named and numeric character references (e.g. &gt;, &#62;,
    &x3e;) in the string s to the corresponding unicode characters.
    In PY3, This function uses the rules defined by the HTML 5 standard
    for both valid and invalid character references, and the list of
    HTML 5 named character references defined in html.entities.html5.
    """
    #Read also here http://stackoverflow.com/questions/19803741/decoding-html-entities-in-python2
    #which btw instantiates new classes for such a "simple" job, so I prefer my solution in PY3. In PY2 no other choice
    #NOTE: the two functions below (see urls) do almost the SAME THING!
    if PY3:
        import html as htmllib
        #https://hg.python.org/cpython/file/3.4/Lib/html/__init__.py#l122
        return htmllib.unescape(string)
    else:
        #See https://hg.python.org/cpython/file/2.7/Lib/HTMLParser.py#l447
        import HTMLParser
        h = HTMLParser.HTMLParser()
        return h.unescape(string)


#Reads the file pointed by the given url (relative path can be given) and returns its content as string, or None on FileNotFound    
def geturlbody(environ, charset='UTF-8'):
    """
        Reads the content of the given url, returning a string
        raises an exception if file not found
    """
    url = geturl(environ)
    if os.path.exists(url):
        file_obj = open(url, 'rb') if PY3 else open(url, 'r') 
        file_body = file_obj.read() 
        file_obj.close() 
        return file_body.decode(charset)
    else: 
        raise Exception("read error: {0} not found".format(url or "url"));

def geturl(environ):
    """
        Reads the url string from environ, basically
        environ['PATH_INFO'].lstrip('/')
    """
    url = environ['PATH_INFO'] 
    if(url):
        url = url.lstrip("/")
    return url

from tempfile import TemporaryFile
import binascii

def getpost(environ, body=None):
    """
        Parses post data from environ['wsgi.input'] in the form of a FieldStorage (Fs) objects, which is a dict of 
        of keys associated to (one or more) nested FieldStorage - or MiniFieldStorage - object(s). A single key represents e.g. the 'name' attribute of a 
        submitted form, e.g., 
        <form action=... target=... method="post" enctype="multipart/form-data">
            <input name='preference' value='a'>
            <input name='preference' value='a'>
            <input name='fileupload' value='a' type='file'>
        </form>
        and calling server side fromn within e.g., a body function(request, response):
            form = request.post
        will return a FieldStorage object with keys 'preference' and 'fileupload'. Each key value 
        (either FieldStorage or MiniFieldStorage object) 
        does not need to be inspected in detail (actually most web frameworks return their 
        own dict wrapping or modifying the returned FieldStorage), just be aware that you can use:
            for key in form.keys() 
                form.getlist(key)   # returns a list of the unicode string value(s) associated to key
                form[key].file      # returns (if any) the file pointer relative to the uploaded vile associated to key
                form[key].filename  # returns (if any) the file name of the uploaded vile associated to key
            
        The last two properties (form[key].file and form[key].filename) can be tested to see if key is associated to 
        an uploaded file. If yes, the module function
            fs_writefile(form[key],..args) 
        lets you write the file to disk (theoretically, only once in PY3 nd at leisure otherwise: http://bugs.python.org/issue18394#msg207958)
        
        If there are more than one uploaded file per key, or for more detailed reading, see
        https://docs.python.org/2/library/cgi.html and
        http://python.about.com/od/cgiformswithpython/ss/pycgitut1_3.htm#step-heading, each element has the
        
        Note that body, when supplied, MUST be the result of 
        getbody(environ). Note also that not specifying any body will call getbody. If the latter has to 
        be stored, better call first getbody, and then pass it here
    """
    if body is None:
        body = getbody(environ)
        
    if environ['REQUEST_METHOD'].upper() != 'POST':
            raise Exception("POST request method needed, found %s", environ['REQUEST_METHOD'].upper())
    
    
    # History of posts: basically, one uses a cgi.FieldStorage object FS with first argument the request body B, where B = environ['wsgi.input']. 
    # FS is a dict like object documented in https://docs.python.org/2/library/cgi.html#using-the-cgi-module 
    # (python2, replace '/2/' with '/3/' in the link above for Python 3) or, for a short descriptions, see:
    # http://python.about.com/od/cgiformswithpython/ss/pycgitut1_3.htm 
    # Two examples not really helpful (either old, or too 'naive') but good for giving an idea are:
    # http://wsgi.readthedocs.org/en/latest/specifications/handling_post_forms.html?highlight=post (2006)
    # and
    # http://stackoverflow.com/questions/530526/accessing-post-data-from-wsgi
    #
    # Given that, there are issues, namely: 
    # 1) Creating FS(B,...) when environ['CONTENT_TYPE'] is 'multipart/form-data' 
    # (which needs to be specified from client FORMS for file uploads, contrarily to the default 'application/x-www-form-urlencoded')
    # raises an error, not well documented and roughly explained in http://stackoverflow.com/questions/14544696/python-simple-wsgi-file-upload-script-what-is-wrong
    # Basically, we must convert B to a TempraryFile T and then call FS(T,...). WebFrameworks such as bottle.py and WebOP catch this issue
    # by converting B to a ByteIO or BufferedReader object, probably because temporary files are not really performant. 
    # We do the same here. The second optional argument body should in fact be a ByteIO object, 
    # which if missing will be module level function getbody(environ) which returns a ByteIO object OR a TemporaryFile
    # (if data is too large), along the lines of bottle.py
    #
    # 2) All web frameworks try to convert FS into a dict object for faster and easier accessibility. this makes the code much more
    # complex to read (possibly because there are several things to check) therefore in this micro-micro framework we pass the FS object.
    # The user will then read the doc given above
    #
    # 3) Any file object inf the FS returned object is READABLE ONLY ONCE in python 3.4. See issue here:
    # http://bugs.python.org/issue18394#msg207958
    # Actually, from bottle.py it seems that the problem is addressed for python 3.1x by using a TextIOWrapper extension
    # which overrides its close method. WebOp seems not to trat the subject, or its code is too complex to see where they handle it. 
    # Anyway, because of this confusion and for sake of simplicity here we don't bother. 
    # Just be aware of that
    #
    # 4) All web frameworks parse the fieldstorage into a custom dictionary. This is necessary for alleviating the pain 
    # of several potential problems:
    # filename encoding, file names or path separators (bottle.py), defining an uniform data type, e.g. unicode (not default in python2 for strings),
    # handling content-transfer-encoding (for emails) etcetera. 
    # Do we have to care here?
    # Well, first of all, from a test done with charset=utf-8 in the web page, and this module as web app,
    # WE FIRST SEE THAT IN BOTH PYTHON 2X AND 3X THE VALUES OF THE FIELDSTORAGE ARE STRINGS. IE BYTE STRINGS IN PY2 AND UNICODE IN PY3
    # The choice they make in WebOp is to transform everythin in unicode. As this is the default choice of json.loads (dict keys are unicode)
    # and unicode is the standard in PY3, we do the same here
    
    # Note that the last loop below does basically two things: 
    # Checks for form[key].type_options.get('charset', default_charset) and performs an ecnode-decoding if PY3
    # Otherwise does nothing. If PY2, as the choice is to return unicode, a decode is always performed (without charset test)
    #
    # 2)It checks the field headers content transfer encoding, accessible via field.headers.get('Content-Transfer-Encoding', None)
    # Transfers encoding refers mainly to email transfer, so we do not bother here, again. For clarity, if needs to be implemented, 
    # see WebOp multidict.py's from_fieldstorage method (but btw, they seem not to handle the case where a form field value is a list), 
    # However, therein they 'catch' two transfer encoding:
    # Base64 (http://en.wikipedia.org/wiki/Base64) and
    # Quoted-printable (http://en.wikipedia.org/wiki/Quoted-printable)
    
    
    # Now, bottle.py parses the body as if it was a query string via a kind of parse_qs method (the one used for GET data)
    # Probably because it returns immediately a dict object. WebOp calls the FieldStorage object.
    # We follow the second strategy for code readability
    
    #back to our BytesIO (or TempFile):
    body.seek(0)
            
    fs_environ = environ.copy() #bottle.py copies JUST some elements, it is surely more performant but for the moment we keep things
    #simple (copy all). IF WE HAD TO STORE SOME CUSTOM KEY IN environ (e.g., the body itself), THEN THIS MIGHT BE HARMFUL
    #IF WE DO NOT DO A CHECK BEFORE
    
    # FieldStorage assumes a missing CONTENT_LENGTH, but a
    # default of 0 is better:
    fs_environ.setdefault('CONTENT_LENGTH', '0')
    #From http://wsgi.readthedocs.org/en/latest/specifications/handling_post_forms.html?highlight=post
    #This must be done to avoid a bug in cgi.FieldStorage:
    #(any example found does this)
    fs_environ['QUERY_STRING'] = ''
    if PY3: # pragma: no cover
        fs = cgi.FieldStorage(
            fp=body,
            environ=fs_environ,
            keep_blank_values=True,
            encoding='utf8')
        #vars = MultiDict.from_fieldstorage(fs)
    else:
        fs = cgi.FieldStorage(
            fp=body,
            environ=fs_environ,
            keep_blank_values=True)
        #vars = MultiDict.from_fieldstorage(fs)
    
    #Code copied and modified from WebOp:
    
    supported_tranfer_encoding = {
            'base64' : binascii.a2b_base64,
            'quoted-printable' : binascii.a2b_qp
    }
    
    for field in fs.list or (): # fs.list can be None when there's nothing to parse
        charset = field.type_options.get('charset', 'utf8')
        transfer_encoding = field.headers.get('Content-Transfer-Encoding', None)

        #returns unicode strings. Note that we HAVe strings, which means unicode in PY3 and bytes in PY2
        decode = None
        if PY3: # pragma: no cover
            if charset != 'utf8': #otherwise is the same charset, so we should return the same (unicode) string
                decode = lambda b: b.encode('utf8').decode(charset) #different charset: encode as byte string (with old charset) and decode as unicode string, with the new charset
        else:
            decode = lambda b: b.decode(charset) #regardeless of the charset, convert byte string to unicode

        if field.filename:
            if decode is not None:
                field.filename = decode(field.filename)
        else:
            value = field.value
            if transfer_encoding in supported_tranfer_encoding:
                if PY3: # pragma: no cover
                    # binascii accepts bytes
                    value = value.encode('utf8')
                value = supported_tranfer_encoding[transfer_encoding](value)
                if PY3: # pragma: no cover
                    # binascii returns bytes
                    value = value.decode('utf8')
            elif decode is None:
                continue
                
            field.value = value if decode is None else decode(value)
    
    return fs
    
#TODO: get post encoding (and how too set fieldoption from the client, those that we use here)
#TODO: check FileWrapper in PY3 (validator is the cause? guess not)
#TODO: check avoid body re-calculation (store variables somewhere?)

def fs_writefile(fs, destination=None, overwrite=False, chunk_size=2**16):
    """
        Writes a FieldStorage (fs) file to disk.
        Parameters:
        destination: the destination file (If missing or None it defaults to fs.filename) 
            in the current direcctory (but I didn't check, it's a guess). Absolute paths are obviously valid. 
            If it denotes a directory, then os.path.join(destination, fs.filename) will be used as destination file.
            Otherwise it is a file pointer (e.g., resulting from open() builtin function)
        overwrite: when False, and destination file exists (which can be only checked if destination is string), 
            raises an IOError. Otherwise overwrites the existing file
        buffer_size: the size of the chunk of data to be written at within each loop 
    """
    sourcefile = fs.file
    if sourcefile is None:
        raise Exception('{0} value is not an uploaded file'.format(fs.name))

    def copy_file(destfilep, _chunk_size=chunk_size):
#            sourcefile = self.getfile(key)
        offset = sourcefile.tell()
        while 1:
            buf = sourcefile.read(_chunk_size)
            if not buf: break
            destfilep.write(buf)
        sourcefile.seek(offset)

    if destination is None or isinstance(destination, string_class): # should be not the file-likes case here
        if destination is None:
            destination = fs.filename
        elif os.path.isdir(destination):
            destination = os.path.join(destination, fs.filename)
        if not overwrite and os.path.exists(destination):
            raise IOError('File exists.')
        with open(destination, 'wb') as f_destination:
            copy_file(f_destination, chunk_size)
    else:
        copy_file(destination, chunk_size)
        
        
def getget(environ):
    #The get stuff is the most obscure: WebOp and bottle do their custom parsing, and it's hard to understand why, 
    #giving that there is the parse_qsl function. Then, there is the big problem of encoding, which is still 
    #difficult to understand. MAYBE compatibility with PY3.1 or 3.2, I don't know, maybe encoding issues, however
    #I tried with some urls and parse_qsl works fine, just need to decode as unicode in PY2
    # I'm sure this code does not take into account the whole spectrum of possibilities, but I'm also 
    #sure that, if I don't get errors even when I try to get them, then the code is at least quite robust.
    #Good link (to read better): 
    #Otherwise, the only thing available is a bunch of outdated examples, e.g. (just to have an idea):
    #http://webpython.codepoint.net/wsgi_request_parsing_get
    #which still uses parse_qs from cgi module, i guess
    #The line below seems redundant (it is) but I leave it cause parse_qsl in PY3 accepts an encoding 
    #argument (default 'utf-8') which might be needed to be set sometime in future

    d = parse_qsl(environ['QUERY_STRING'], keep_blank_values=True, strict_parsing=False) if not PY3 else \
                parse_qsl(environ['QUERY_STRING'], keep_blank_values=True, strict_parsing=False) 

    charset = 'utf-8'

    ret = OrderedDict()

    for k in d:
        kk = k if PY3 else (k[0].decode(charset), k[1].decode(charset))
        key = kk[0]
        val = kk[1]
        if key in ret:
            ret[key].append(val)
        else:
            ret[key] = [val]

    #check why WebOp uses parse_qsl, and why it differentiates between PY2 and PY3...

    return ret

#Notes on json module: from http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
#The json module accepts strings and returns UNICODE strings, which means:
#PY2: accepts BYTES and returns UNICODE (decoded how? utf-8? see )
#PY3: accepts STRINGS and returns STRINGS (no need for encoding / decoding)
#The server takes BYTEs, and the body from which we read is made of bytes (see getbody function)
#In py2, it is 'safe' in that py2 uses byte strings, but then problem arise when we combine unicode + str (if there is unencodable/decodable bytes/unicodes)
#In py3, it is not sa

def getjson(environ):
    """
        Gets the json object inside environ, a dict variable passed to a Server response
        Note that elements are unicode strings, which is not the default in Python 2x
    """
    #copied from WSGI + jQuery example
    request_body_size = int(environ["CONTENT_LENGTH"])
    request_body = environ["wsgi.input"].read(request_body_size) #FIXME: closes the stream? Theoretically, in python2 no! check
    if PY3: #convert to unicode, which is the default string type. Otherwise it complains that it has byte strings
        #(py2 does not complain because byte strings are the default)
        request_body = request_body.decode('utf-8')
    event = json.loads(request_body) 
    #event contains unicode data now (default in json module)
    return event

def tojson(python_obj):
    """
        Returns a python object representing the json request to be sent from the server, 
        converting the python_obj argument into unicode strings (the default in PY3). 
        If the returned value has to be passed to a response body, the wsgi app will handle conversion
        to byte strings according to the repsonse charset (if set, otherwise utf-8)
    """
    return [json.dumps(python_obj, separators=(',',':'))]

def getbody(environ):
    """
        returns the environ['wsgi.input'] data in form of a ByteIO or TemporaryFile
    """

    #Code copied and modified from Bottle.py, having a look in Request.py in WebOP

    #def a function for iterate over the body. Note:
    #in bottle.py this function is implemented differently according to 
    #whether there is Chunked transfer encoding or not. This is a subject we don't master yet
    #therefore we keep things simple here

    content_length = int(environ.get('CONTENT_LENGTH') or -1)

    def body_iterable(read, bufsize):
        maxread = max(0, content_length)
        while maxread:
            part = read(min(maxread, bufsize))
            if not part: break #FIXME: WARN DEBUG MESSAGE?
            yield part
            maxread -= len(part)

    read_func = environ['wsgi.input'].read
    body = BytesIO()
    body_size = 0
    is_temp_file = False
    #: Maximum size of memory buffer for body property (in bytes). FIXME: MAKE PUBLIC?
    MEMFILE_MAX = 102400

    for part in body_iterable(read_func, MEMFILE_MAX):
        body.write(part)
        body_size += len(part)
        if not is_temp_file and body_size > MEMFILE_MAX:
            body = TemporaryFile(mode='w+b')
            tmp = body
            body.write(tmp.getvalue())
            del tmp
            is_temp_file = True
    body.seek(0)
    return body

#@decoratorFunctionWithArguments("hello", "world", 42)
#def sayHello(a1, a2, a3, a4):


    
#Old object in use. Leave comment here although not used anymore
#Code taken from http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
#We want to just collect a bunch of stuff together, 
#naming each item of the bunch; a dictionary's OK for that, but a small do-nothing class is even handier, and prettier to use:
#class Bunch(object):
#    def __init__(self, **kwds):
#        self.__dict__.update(kwds)

#FIXME3: Check the usage of wsgi Handlers object

class Request(object):
    """
        A Request is an object representing a server request: it is an environ variable wrapper with methods and utilities. 
        Given a wsgi App and a route binding url -> f (where url is a path -string or regexp - and f is a function f returning a response body. 
        See route decorator for details) an object r = Request() is always internally associated to that binding and is passed as 
        first argument to f when f needs to be called. f may (potentially modify r.environ, but 
        there is no such need for the moment, maybe in the future) and query r for:
        
        
        The Response is dict-like in that, given r = Response(), the following operations are possible:
        
        r.environ           # get environment dict of the request
        r.charset       `   # returns the request charset, if any (otherwise 'utf-8')
        r.get               # returns a FieldStorage (dict-like object) of the 
        r.post              # returns a FieldStorage (dict-like object) of the 
        r.body              # returns the Request body of the environ dict
        r.url               # returns the Request url name
        r.urlbody           # returns the Request url file content (if points to an existing file) in str format (unicode in PY<3)
        r.json              # returns the Request json dict, if any
        
    """
    def __init__(self):
        self.__environ = None
        self.__body = None
        self.__charset = None
        
    @property
    def environ(self):
        return self.__environ
    
    @environ.setter
    def environ(self, value):
        self.__environ = value
        if not self.__body is None:
            if hasattr(self.__body, "close"): self.__body.close()
            self.__body = None
        self.__charset = None
    
    @property
    def charset(self):
        if self.__charset is None: #lazily create it
            self.__charset = getcharset(self.__environ, 'CONTENT_TYPE') 
        return self.__charset
    
    @property
    def get(self):
        """
            Calls the module level function getget(self.environ)
        """
        return getget(self.__environ)
    
    @property
    def post(self):
        """
            Calls the module level function getpost(self.environ)
        """
        return getpost(self.__environ) #, self.body) #FIXME: INEFFICIENT, WE LOAD BODY EVERY TIME. BUT IT WORKS. WARN USERS
    
    @property
    def url(self):
        """
            Calls the module level function geturl(self.environ)
        """
        return geturl(self.__environ)
    
    @property
    def urlbody(self):
        """
            Calls the module level function geturl(self.environ)
        """
        return geturlbody(self.__environ, self.charset)
    
    @property
    def body(self):
        """
            Calls the module level function getbody(self.environ)
        """
        if self.__body is None:
            self.__body = getbody(self.__environ)
        return self.__body
    
    @property
    def json(self):  
        """
            Calls the module level function getjson(self.environ)
        """
        return getjson(self.__environ)
    
class Response(object):
    """
        A Response is an object representing a server response: it is  a dict-like object of response headers 
        and has a read/write property 'status'. 
        Given a wsgi App and a route binding url -> f (where url is a path -string or regexp - and f is a function f returning a response body. 
        See route decorator for details) an object r = Response() is always internally associated to that binding and is passed as 
        second argument to f when f needs to be called. f may then modify r.headers and r.status from within its function body. 
        When f returns the response body B, the App forwards the (potentially modified) response by calling start_response(r.headers, r.status) 
        before eventually returning B 
        
        A Response is a dict taking an optional dict of default values: every time f needs to be called, r headers is set to that default values 
        and r status is set to OK, before calling f with r as second argument. Note also that an attempt to set r 'Content-Type' is made, if 
        the latter is unspecified (see mimetypes module)
        
        The Response is dict-like in that, given r = Response(), the following operations are possible:
        
        r['Content-'Type']              # get the value of a key
        r['Content-Type'] = 'text/html' # set the value of a key
        for k in r:                     # iterate over values
        del r['key']                    # key deletion 
        len(r)                          # number of headers pairs
        
        Also: 
        
        r.headers                       # sets/get the headers. NOTE: response headers are stored internally as dict. 
                                        # As a getter (e.g. v = r.headers) this method 
                                        # RETURNS a LIST of 2-element tuples (key, value), as this is the format which needs to be passed to 
                                        # the web application start_response function.
                                        # As a setter (e.g., r.headers = something), then something can be either a list or a dict
        
        r.status                        # sets/gets the status. Import http.client (or httplib for Python <3) for a list of status to be set
                                        # (e.g., r.status = httplib.OK). Usually, you can supply either a string or an integer. Passing valid integers 
                                        # however will send to the wsgi app start_response function the status together with its repsonse string, if found
                                        # in httplib.responses (e.g. status = httplib.NOT FOUND = '404 Not Found')
        
        r.tojson(obj, set_ctype)        #Returns a list wrapping a json-formatted string of obj. A second argument (true by default), 
                                        #sets also self['Content=Type'] to 'application/json'
                                        
        headers needs to be set as strings. It is apparently safe to use the python string class (for both PY2 and PY3, although they 
        are of different type. See http://legacy.python.org/dev/peps/pep-0333/#unicode-issues and http://bugs.python.org/issue11968)
    """
    def __init__(self, headers=None):
        self.__default_headers = {} if not isinstance(headers, dict) else headers.copy()
        #self.__charset = None
        
    def reinit(self, url): #environ is used just for the url
        self.__status = httplib.OK #httplib.NOT_FOUND
        self.__headers = self.__default_headers.copy()
    
    
    #implementing the dict / iterator interface: __iter__ and next (__next__ in py3):
    def __getitem__(self, key):
        return self.__headers[key]
    
    def __delitem__(self, key):
        del self.__headers[key]
    
    def __setitem__(self, key, value):
        if value is None:
            del self.__headers[key]
        elif not isinstance(value, string_class):
            value = str(value) #this is safe in both python 2 and 3, apparently both needs netive strings (str func should be byte strings in PY2, unicode strings in PY3)
            
        self.__headers[key] = value
    
    def __iter__(self):
        return self.__headers.__iter__
    
    if PY3:
        def __next__(self): 
            return self.__headers.__next__()
    else:
        def next(self): 
            return self.__headers.next()

    def __len__(self):
        return len(self.__headers)
    
    def __contains__(self, key):
        return key in self.__headers
    #done----------------------------------------------------------------------
    
    @property
    def charset(self):
        #lazily create it. NO! we could change the charset
#        if self.__charset is None: self.__charset = getcharset(self.__headers, 'Content-Type')
#        return self.__charset
        return getcharset(self.__headers, 'Content-Type')
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        self.__status = value
    
    @property
    def headers(self):
        # Apparently, in python3 the header needs to be native strings, see
        # http://bugs.python.org/issue11968
        # The following works also for python 2, so we write the simple line below, 
        # which takes into account items and iteritems differences only, and not str vs unicode differences
        return list(self.__headers.items()) if PY3 else list(self.__headers.iteritems()) 
    
    @headers.setter
    def headers(self, value):
        """
            Sets the headers which must be either a dict (which will NOT be copied) or a list/tuple. In the latter case
            both ['key', 'value',...] and [('key', 'value'),...] lists are valid (same for tuples)
        """
        d = {}
        if type(value) in (list, tuple):
            for i in _range_(len(value)):
                key = value[i]
                if type(key) in (tuple, list):
                    val = key[1]
                    key = key[0]
                else:
                    i+=1
                    val = value[i]
                d[key] = val
        elif type(value)==dict:
            d = value
        else:
            raise Exception("Only list/tuples or dict of strings can be set as headers")
        self.__headers = d
    
    def tojson(self, python_obj, set_content_type=True):
        """
            Returns the module-level function tojson(python_obj), setting also 
            by default the content type of this response (self['Content-Type'] = 'application/json'
            Pass a second variable as False to prevent content type being set
        """
        if set_content_type and (not 'Content-Type' in self or self['Content-Type']!='application/json'): self['Content-Type'] = 'application/json'
        return tojson(python_obj)

def needsencode(var, strict = True):
    """
        Utility function returning True if var is unicode string, False if var is byte string (bytes in PY3).
        Raises an exception (TypeError) if not string (basestring in PY2 and str inPY3) and the second arg. strict is True (default)
        Otherwise returns False for all non-string objects (meaning that in some way they do not need encoding)
    """
    if isinstance(var, bytes): return False
    elif isinstance(var, string_class): return True
    if not strict: return False
    raise TypeError('{0} cannot be encoded/decoded: not a string'.format(str(type(var))))
    
class App(object):
    """
        (Web) Application, i.e. the function which handles
        the requests from and to the server. 
    """
    
    def __init__(self, main_dir=""): #, environ, start_response, url):
        """ 
            Initializes a default App. the argument main_dir is self-explanatory 
            and represents the main index.html (or whatever is the main page) dir.
            It is used only for urls mapped explicitly via the App.route decorator.
            Example: 
            Both
            
            @App.route
            def a_post(request, response): ...
            
            @App.route(url='a_post')
            def whatever_func_name_you_want(request, response): ...
            
            map the string 'a_post' to the following body function. Problem is, 
            a page makes requests according to its path (determined e.g., the run 
            global function: if the file argument is 'some_dir/index.html' and from therein
            we post a request to 'a_post', then 'some_dir/a_post' is scanned in the 
            added routes keys, see __call__ function of this class)
            Specifying a main_dir makes it possible, if the request url starts with 
            main_dir, to scan also for the remaining string in the reoutes map.
            This avoids to re-type the url argument of the @App.route decorator 
            if we change the paths of the main page
            
            Note that main_page does not need to end with a slash, it will automatically appended
        """
        self._routes = {
            re.compile(r"\.(?:jpg|jpeg|bmp|gif|png|tif|tiff|js|css|xml)$", re.IGNORECASE) : (Request(), Response(), App.getfile)
        }
        
        self.__main_dir = main_dir+"/" if len(main_dir) and main_dir[-1]!='/' else (main_dir or "")
        
    @property
    def main_dir(self):
        return self.__main_dir
    
    @main_dir.setter
    def main_dir(self, value):
        self.__main_dir = value
    
    # decorator function to add a route. 
    # For info on decorators, see http://stackoverflow.com/questions/5929107/python-decorators-with-parameters (2nd or 3rd post):
    # REMEBER THAT ALL DECORATORS ARE FUNCTIONS RETURNING FUNCTIONS
    # ------------------------------+
    # @decorator                    |
    # def foo(*args, **kwargs):     |
    # ------------------------------+                              
    # Translates to
    # ------------------------------+
    # foo = decorator(foo)          |
    # ------------------------------+
    # WITH ARGUMENTS, THE DECORATOR IS A FUNCTION RETURNING A DECORATOR FUNCTION
    # ------------------------------+
    # @decorator(arg)     |
    # def foo(*args, **kwargs):     |
    # ------------------------------+
    # translates to
    # ------------------------------+
    # foo = decorator(arg)(foo)     |
    # ------------------------------+
    
    # @app.route (means a single arg, the callback)
    # @app.route(headers)
    # @app.route(url)
    # @app.route(url, headers)
    # @app.route(url=..., headers=...)
    _retype = type(re.compile(""))
    
    def route(self, *args, **kwargs):
        """
            route decorator. Assuming an app=App(), typical usage is:
                
                @app.route
                body_func(request, response)
                
            where body_func is assumed to return a body response 
            (string, bytes, file-like object, iterable of string/bytes)
            
            The route decorator may take an url (regexp or string) denoting the route at which to execute the 
            decorated function from within the wsgi application __call__ method, and a dict of default headers 
            for the response passed as argument of body_func.
            
            All arguments are optional. When no url is specified, it defaults to body_func.__name__ (the name of the body function, 
            i.e. "body_func" in the example above). When no default headers are specified, they default to {}. Examples:
            
            @app.route          
            @app.route(headers), @app.route(url) or @app.route(url, headers)
            @app.route(url = ...), @app.route(headers = ...) or @app.route(url = ..., headers = ...)
            
            
        """
        
#        print("*args has length {:d}:".format(len(args)))
#        for v in args:
#            print("args: {0} {1}".format(str(v), str(type(v))))
#        print("**kwargs has length {:d}:".format(len(kwargs)))
#        for k in kwargs:
#            v = kwargs[k]
#            print("kwarg: {0} {1}".format(str(k), str(v), str(type(v))))
#        print("\n\n")
        
        len_args = len(args) if args else 0
        len_kwargs = len(kwargs) if kwargs else 0
        
        if ((len_args and len_kwargs) or (not len_args and not len_kwargs)): raise TypeError("Invalid route decorator arguments") #should never be the case
        
        url=None
        headers={}
        
        if len_args: 
            url = args[0]
            if len_args == 2:
                headers = args[1]
            elif len_args > 2:
                raise TypeError("Invalid route decorator arguments")
            
            if hasattr(url, "__call__"):
                self.add_route(url.__name__, url, headers)
                return url
            
        if len_kwargs:
            if 'url' in kwargs: url = kwargs['url']
            if 'headers' in kwargs: headers = kwargs['headers']
            
        if not url is None and not (isinstance(url,string_class) or type(url) == App._retype):
            raise TypeError("Invalid route url argument")
        
        if not type(headers) == dict:
            raise TypeError("Invalid route headers argument")
        
        def wrap(body_function): #this f is our user-defined getbody. Executed immediately

            #Previously, I bound the method to a new ResponseHandler
            #Leave refs here:
            #see http://www.tryolabs.com/Blog/2013/07/05/run-time-method-patching-python/
            #and http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object
            
            #if url is none, bind the function name:
            self.add_route(body_function.__name__ if url is None else url, body_function, headers)
            return body_function
        
        return wrap
    
    def add_route(self, url, body_func, headers={}):
        self._routes[url] = (Request(), Response(headers), body_func)
        
    def __call__(self, environ, start_response): 
        
        url = geturl(environ)
        route_map = self._routes
        response = None
        request = None
        body_func = None
        
        if(url in route_map): #FIXME: strings have apparently an hash, regexp ALSO. NEEDS REF
            request, response, body_func = route_map[url]
        elif self.__main_dir and isinstance(url, string_class) and url.find(self.__main_dir)==0:
            #handle the case where we provided no url (or a string) AND appending the main_dir (if given) 
            #matches some file
            url = url[len(self.__main_dir):]
            if(url in route_map): 
                request, response, body_func = route_map[url]
        
        if response is None:
            for k in route_map:
                if(isinstance(k, string_class)):
                    continue
                if(k.search(url)): #FIXME: search or matches is faster??
                    request, response, body_func = route_map[k]
                    break;

        status = httplib.OK #httplib.NOT_FOUND
        body = [] #["Server error: %s not found" % url]
        headers = [] #[("Content-Length",len(body[0]))]

        if(response is None): #FIXME: HANDLE THIS!!!
            request = Request()
            response = Response()
            body_func = self.getfile
            route_map[url] = (request, response, body_func) #append (for next time...)

        request.environ = environ
        response.reinit(request.url)
        
        try:
            body = body_func(request, response)
            body = self.cast(environ, body, response)
        except Exception as _error_:
            body = self.handle_exc(response, environ, _error_)

        status = response.status
        headers = response.headers
        #body = data.body

        #make_server apparently already prints 
        if _DEBUG_ : debug("\nServing {0} ({1})".format(url,str(headers)))
        
        try:
            status_tmp = '{:d} {:s}'.format(status , httplib.responses[status])
            status = status_tmp
        except:
            status = str(status)
        
        if not 'Content-Type' in response and body and _DEBUG_ : debug("WARNING: '{0}' has no 'Content-Type'".format(str(url)))
        
        start_response(status, headers) 

        return body
   
    def handle_exc(self, response, environ, _error_):
        """ 
            Handles an exception in a body function, returnign the new body response wrapping the exception message
        """
        
        body = []
        
        #NOTE: content-length does not seem to be mandatory, see
        #http://www.techques.com/question/1-6919182/Is-Content-length-the-only-way-to-know-when-the-HTTP-message-is-completely-received
        #As it involves more calculation, we omit if it is not retriavable without the risk  of performance loss

        if _DEBUG_: traceback.print_exc()
        
        #re-init the dict
        response.headers = {'Content-Type': 'text/plain'}
#        response['Content-Type'] = 'text/plain'
        
        strlen=0
        if environ["REQUEST_METHOD"] != "HEAD":
            
            if PY3:
                from io import StringIO
            else:
                from StringIO import StringIO
                
            output = StringIO()
            output.write(str(_error_)) #message copied from what I got in in the browser in case of unexpected error
            #traceback.print_exc(file=output)
            #get string value (this is the part which has the best benefits over performances compared to strings):
            output_str = output.getvalue()
            #wrap the error message, set content length, go on...:
            body = [output_str]

            if type(body[0]) != bytes: #see notes below in cast for info 
                body[0] = body[0].encode(response.charset) #FIXME: request or response charset?

            strlen = len(body[0])

        response['Content-Length'] = str(strlen)
        #change status only if it is not already set as error (>=400)
        if response.status < 400: #httplib.BAD_REQUEST
            response.status = httplib.INTERNAL_SERVER_ERROR
        
        return body
        
    def cast(self, environ, body, response):
        """
            Casts the body returned from getbody to a suitable response output.
            See 
            Supported types are byte strings, file-like objects, lists and tuples
        """
        
        #FIXME: Add support for HTTPResponse, HTTPError?
        
        #Following code is along the line of bottle.py:
        
        if not body or response.status in (100, 101, 204, 304)\
            or environ['REQUEST_METHOD'] == 'HEAD':
                if hasattr(body, 'close'): body.close()
                response['Content-Length'] = "0"
                return []

        # Encode unicode strings
        #WARNING: unicode does not exist in PY3, Use not PY3 so that only if true executes the test with unicode
#        if (PY3 and isinstance(body, string_class)) or (not PY3 and isinstance(body, unicode)): #string_class is str in PY3, i.e. unicode in PY2
        if needsencode(body, strict=False):    
            body = body.encode(response.charset)
            #Now we will fall into the byte string case below
            
        # Handling byte strings: 
        # The 'Bible' is here: http://nedbatchelder.com/text/unipain.html (relative long reading)
        # For the case at hand
        # (from :http://stackoverflow.com/questions/5901706/the-bytes-type-in-python-2-7-and-pep-358
        # and https://docs.python.org/3/library/functions.html#bytes):
        # The bytes type was introduced in Python 3 as an immutable sequence of integers in the range 0 <= x < 256
        # In Python 2 bytes is just an alias for str to aid forward compatibility
        # After the encode above (if we entered there) we have str in python2 (i.e., bytes) or bytes in python 3
        # So it's safe to do this to just assure that we have a properly encoded byte string:
        if isinstance(body, bytes): 
            if 'Content-Length' not in response:
                response['Content-Length'] = str(len(body))
            return [body]
        
        # File-like objects. Lists and tuples do not have a read attribute so we won't fall in here, in case
        # An (outdated) lecture is here:
        # http://legacy.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling
        # However, having a look at boottle.py and https://docs.python.org/2/library/wsgiref.html#wsgiref.util.FileWrapper:
        if hasattr(body, 'read'):
            #Copied from http://legacy.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling
            if 'wsgi.file_wrapper' in environ:
                return environ['wsgi.file_wrapper'](body)
            else: #if not hasattr(body,"__iter__"):
                #THERE IS A FILEWRAPPER CLASS IN wsgiref which seems to do what we want:
                #see https://docs.python.org/2/library/wsgiref.html#wsgiref.util.FileWrapper
                return FileWrapper(body)
        
        #Ok, if it is an iterator neither list nor tuple, just return that iterator without specifying the content-length
        #which is possible. See http://legacy.python.org/dev/peps/pep-3333/#handling-the-content-length-header
        #We do not convert into list because the assumption is that, if we provided a custom iterator maybe memory matters, and list
        #would load all content into memory
        #The drawback is that we cannot be aware of the conversion. So either we create a custom iterator, or we just display a warning
        #assuming one knows what is doing. Warn the user anyway
        _type_ = type(body)
        if _type_ not in (list, tuple):
            try: #See also http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
                if not hasattr(body, "__iter__"): raise Exception() #falls in the case below
                if _DEBUG_: debug("Warning: returning an iterator from the response body which must yield strings or bytes (any other element will not be sent)")
                #return a generator expression, see https://docs.python.org/2/reference/expressions.html#generator-expressions
                #A generator has __iter__ and __next__ in PY3, so it should be OK
                emptyvar = b'' if PY3 else ''
                #Note: round brackets return a GENERATOR! not a tuple. See
                #https://docs.python.org/3/reference/expressions.html#generator-expressions
                #(holds also for PY2, just replace 3 with 2 in the url above)
                return (line if isinstance(line, bytes) else (line.encode(response.charset) if needsencode(line, strict=False) else emptyvar) for line in body)
                
            except:
                raise Exception("Unable to send {0} as response body (strings, bytes or iterators of string/bytes possible)".format(str(_type_)))
    
        #tuples or lists handled here
        #return the same element if tuple or list, and no element needs encode, this avoids copy the object when unnecessary
        #To achieve this, loop until the first element which MUST be encoded
        j=0
        needs_encode = False
        length = 0
        for v in body:
            try:
                needs_encode = needsencode(v)
                if needs_encode: break
                length += len(v)
                j+=1
            except Exception as e: raise Exception('{0} (iterable element at position {:d})'.format(str(e), str(j)))

        if needs_encode:
            ret = list(body) if _type_ == tuple else body
            l = len(ret)
            #this element needs encode:
            ret[j] = ret[j].encode(response.charset)
            length += len(ret[j])
            for i in _range_(j+1, l):
                try:
                    if needsencode(ret[i]): ret[i] = ret[i].encode(response.charset)
                except Exception as e: raise Exception('{0} (iterable element at position {:d})'.format(str(e), str(j)))
                length += len(ret[i])
            body = ret
        
        response['Content-Length'] = str(length)
        return body
        
    
    @staticmethod    
    def getfile(request, response):
        
        environ = request.environ
        
        url = request.url
        if not os.path.exists(url):
            response.status = httplib.NOT_FOUND
            raise Exception('{0} not found'.format(url))
        
        
        #from bottle.py. Sets content-type and content-encoding
        
        #Originally, the code was copied and modified from WSGI+jQuery example (on Stackoverflow)
        #and static.py file (https://bitbucket.org/luke/static/raw/b0a7c7b4991d3e9f16e2eb7fb57afa0df786f375/static.py)
        #The "modified-status" check is still from the link above, although it should be IMPROVED. The rest from bottle.py
        
        #Note that rfc822 is deprecated, so we need to replace rfc822.parsedate and formatdate with email.utils methods
        file_not_modified = False

        mtime = os.path.getmtime(url) #returns a number in seconds since the epoch, see https://docs.python.org/2/library/os.path.html#os.path.getmtime
        #old code: os.path.stat(url).st_mtime (which is called by getmtime according to this (2nd post): http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
        etag, last_modified = str(mtime), email.utils.formatdate(mtime) #FIXME: CHECK TIME ZONES!!!!!

        check_if_modified = environ.get('HTTP_IF_MODIFIED_SINCE')
        if check_if_modified and (email.utils.parsedate(check_if_modified) >= email.utils.parsedate(last_modified)): 
            #Note: parsedate above returns tuples. Tuples have order (so > works) FIXME: NEEDS_REF
            file_not_modified = True
        else:   
            check_if_none_match = environ.get('HTTP_IF_NONE_MATCH')
            if check_if_none_match and (check_if_none_match == '*' or etag in check_if_none_match):
                file_not_modified = True

        #=================================================================

        if file_not_modified:
            if 'Content-Type' in response: del response['Content-Type'] #remove content type (validators -defined in manage.py - complains otherwise)
            response.status = httplib.NOT_MODIFIED #'304 Not Modified'
            if _DEBUG_ : debug("    content not modified, returning 304")
            return [] #return empty iterable

        #add headers, now:
        response['Date'] = email.utils.formatdate(time.time())
        response['Last-Modified'] = last_modified
        response['ETag'] = etag
        
        #Check this line here...
        if request.environ["REQUEST_METHOD"] == 'HEAD': return [] #http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
        
        #handle the file. In PY2, as strings are byte strings, everything is fine.
        #In py3, we should check whether it is text or bytes
        if not "Content-Type" in response:
            #We should have set the content type in response reinit, but for safety we do it also here
            c_type, encoding = guess_mimetype(url, default_type=None)
            if c_type: response["Content-Type"] = c_type
            if encoding and not 'Content-Encoding' in response: response['Content-Encoding'] = encoding
                
        #this is passed to cast, just return the file
        #return file(url,'r')
        #file removed from py3, use open which is already present in PY2
        return open(url,'rb')
    
    def __str__(self):
        #FIXME: optimize
        s = "wsgi.App{\n"
        retype = type(re.compile('')) #to get the type of regexp object. Is there a nicer way?
        for k in self._routes:
            kstr = "re({0})".format(k.pattern) if type(k) == retype  else str(k)
            val = self._routes[k]
            val = "("+str(val[2]) + ", headers=" + str(val[1]._Response__default_headers)+")"
            s+="\t" + kstr + ": " + val + "\n"
        s += "}"
        return s


def guess_mimetype(url, default_type = "text/plain", default_charset= "UTF-8"):
    """
        Along the lines of mymetypes.guess_type, guess the type of a file based on its filename or URL, given by url. 
        The return value is a tuple (type, encoding) where type is a string (in the form 'type/subtype') 
        usable for a MIME content-type header. 
        If the type can’t be guessed (missing or unknown suffix), then the default_type argument is used (it defaults to 'text/plain' if missing) 
        If the type is in the form 'text/subtype', then it is transformed in the form 'text/subtype;charset=default_charset' as  
        specified in the default_charset argument (which defaults to 'UTF-8' if missing)
    """
    import mimetypes
    c_type, encoding = mimetypes.guess_type(url) 
    
    c_type = c_type or default_type
    
    if not c_type is None and c_type[:5] == 'text/' and default_charset and 'charset' not in c_type:
        c_type += '; charset={0}'.format(default_charset)
    
    return c_type, encoding

def_app = None
#the function below (with proeprty decorator) should make the function documentable
#on the other hand, module vars are not

def route(*args, **kwargs):
    """
        route decorator for the module level def_app. Typical usage is:

            @miniwsgi.route
            body_func(request, response)
        
        And then call miniwsgi.def_app to have access to the routed wsgi App.
            
        where body_func is assumed to return a body response 
        (string, bytes, file-like object, iterable of string/bytes)

        The route decorator may take an url (regexp or string) denoting the route at which to execute the 
        decorated function from within the wsgi application __call__ method, and a dict of default headers 
        for the response passed as argument of body_func.

        All arguments are optional. When no url is specified, it defaults to body_func.__name__ (the name of the body function, 
        i.e. "body_func" in the example above). When no default headers are specified, they default to {}. Examples:

        @app.route          
        @app.route(headers), @app.route(url) or @app.route(url, headers)
        @app.route(url = ...), @app.route(headers = ...) or @app.route(url = ..., headers = ...)


    """
    
    global def_app
    #here build the ResponseHandler, and set it to REQUEST_MAP
    if def_app is None:
        def_app = App()
        
    return def_app.route(*args, **kwargs)
    
    
#copied from WebOb request.py:

_CHARSET_RE = re.compile(r';\s*charset=([^;]*)', re.I)

def getcharset(obj, dict_list_key=None, default="UTF-8"):
    """
        detects charset from  obj. If the latter is
        A dict/list/tuple, then deict_list_key specifies the key whose value has to be parsed (e.g., 'CONTENT_TYPE' for requests, 'Content-Type' for responses)
        A string, then obj itself is the value to be parsed, and dict_list_key is ignored
        
        In any unmatching case (e.g., unparsed / empty values, or dict_list_key None and obj dict/list/tuple) the returned charset 
        will default to the default argument ('UTF-8')
    """
    ctype = None
    #added by be: catch cases where we pass lists or 
    if type(obj)==dict:
        if dict_list_key is not None and dict_list_key in obj:
            ctype = obj[dict_list_key]
    elif type(obj) in (tuple,list):
        if dict_list_key is not None:
            for i in _range_(len(obj)-1):
                if obj[i] == dict_list_key:
                    ctype = obj[i+1]
                    break
    
    if isinstance(ctype, string_class):
        m = _CHARSET_RE.search(ctype)
        if m:
            ret = m.group(1).strip('"').strip()
            if len(ret) > 0:
                return ret
    
    return default
   
def run(app, file="index.html", openbrowser=True, port=8080):
    """
        Runs the given application app at the address:
            http://localhost:port/file
        where the function argument file defaults to "index.html" if missing
        and the function argument port defaults to 8080 if missing
        If openbrowser is True, opens autonatically the system default web browser at the 
        given address. Otherwise, the user must manually open a web browser and 
        manually go at the given address (or refresh the page 
        if already showing)
    """
    from wsgiref.validate import validator
    from wsgiref.simple_server import make_server
    
    #host = "localhost/file"
    print("Starting server on 'http://localhost:{0}/{1}'".format(port, file))
    
    #setting main dir
    idx = file.rfind('/')
    if idx>-1:
        app.main_dir = file[:idx+1]
        print("Setting main dir to '{0}'".format(app.main_dir))
        
    #bug with validator in python3?
    httpd = make_server("localhost", port, validator(app)) #validator(wsgi.def_app)) #FIXME: check how to write a proper import
    
    if openbrowser:
        import threading #for thread in open_browser
        import webbrowser
        # Start a browser after waiting for half a second
        #When used with start_server below (see main code at the bottom of the page)
        #as start_server start_server blocks execution of remaining code, this method must be 
        #run before start_server but needs server to run. That is why the thread workaround
        def _open_browser(file,port):
            webbrowser.open('http://localhost:{0}/{1}'.format(port, file))
        thread = threading.Timer(0.6, _open_browser, [file, port])
        thread.start()

    httpd.serve_forever()
    
    
    
if __name__ == '__main__':
    quit()
    #min_dist(7, 15, 5, 20)
#    event = {u'longitude':74.2344, u'latitude':'42.8', u'depth':'15    4 6', u'strike':0, u'ipe':2, u'magnitude':6.8}
#     print(encode(('a', 'asd', '©')))
#     print(encode(['a', 'asd', '©']))
#     print(encode('©'))
    
