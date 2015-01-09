#! /usr/bin/python

"""
Base class implementing a Caravan WSGI application and utilities related to 
server-client requests and responses

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/
"""

__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="$Jun 23, 2014 1:15:27 PM$"

import os
import json
#import os.path
import sys
import traceback
import re
from cgi import parse_qs, parse_qsl, escape #for parsing get method in main page (address bar)

import mimetypes
#import rfc822
import email.utils
import time
#import string
from os import path, stat
#from wsgiref import util
#from wsgiref.headers import Headers
#from wsgiref.simple_server import make_server
#from optparse import OptionParser


CARAVAN_DEBUG = True; #debug variable, as of Juli 2014 it controls whether exceptions in ResponseHandler should throw the traceback or simply an error message

#To implement classes, we should start a server with a given application(environ, start_response), with an iterable class 
#(which implements the __iter__(self) method, or with a class which implements the __call__(environ, start_response) method
#See http://legacy.python.org/dev/peps/pep-0333/#the-application-framework-side (quite confusing in my opinion)
#and the second answer to this topic: http://stackoverflow.com/questions/21059640/wsgiref-error-attributeerror-nonetype-object-has-no-attribute-split

#Reads the file pointed by the given url (relative path can be given) and returns a list of each line, and None on FileNotFound
def _read_lines(url):
    """
        Reads lines of the given url, returning a list where each element is a file line.
        Returns None if file is not found
    """
    if os.path.exists(url): 
        file_obj = open(url, 'r') 
        response_lines = file_obj.readlines() 
        file_obj.close() 
        #start_response('200 OK', [('Content-Type', content_type)]) 
        
        return response_lines 
    else: 
        return None;
    
#Reads the file pointed by the given url (relative path can be given) and returns its content as string, or None on FileNotFound    
def _read(url):
    """
        Reads the content of the given url, returning a string
        Returns None if file is not found
    """
    if os.path.exists(url): 
        file_obj = open(url, 'r') 
        file_body = file_obj.read() 
        file_obj.close() 
        #start_response('200 OK', [('Content-Type', content_type)]) 
        
        return file_body 
    else: 
        return None;

#TERMINOLOGY:
#Request : From Client to Server
#Response: From Server to Client
#Server: Receive Request and Send Response
#Client: Send Request and Receive Response

def main_app(environ, start_response): 
    """
        Main Caravan (Web) Application, i.e. the function which handles
        the requests from and to the server. It makes use of REQUEST_MAP and ResponseHandler class
        (see in the code)
    """
    
    url = environ['PATH_INFO'] 
    if(url):
        url = url.lstrip("/")
    
    response_handler = None
    
    if(url in REQUESTS_MAP): #FIXME: strings have apparently an hash, regexp not. NEEDS REF
        url = REQUESTS_MAP[url]
        
    for k in REQUESTS_MAP:
        if(isinstance(k, basestring)):
            continue
            
        if(k.search(url)): #FIXME: search or matches is faster??
            response_handler = REQUESTS_MAP[k]
            break;
        
    if(response_handler is None):
        response_handler = ResponseHandler()
        
    if CARAVAN_DEBUG:
        print "\nServing " + url 
    
    response_handler.run(url, environ)
    
    if CARAVAN_DEBUG:
        print "\tresponse headers: " + str(response_handler.headers)
    
    start_response(response_handler.status, response_handler.headers) 
    
    return response_handler.body    
    

#FIXME1: file mod time
#FIXME2: Check wsgi FileWriter and see if MainPageResponseHandler can extend StaticPageRH
#FIXME3: Check the usage of wsgi Handlers object
#FIXME4: Return a 501 status on exception? In general, handle exceptions

class ResponseHandler(object):
    """A class which processes an http response. It holds three fields which by 
    default are:
    self.headers = {...} #custom HTTP headers or empty dict (see below)
    self.body = []
    self.status = ResponseHandler._status404
    These fields will be read by a WSGI application calling this class run method.
    
    A new object of this class is initialized with an optional list of zero or 
    more custom HTTP headers (key, value) pairs 
    (see http://en.wikipedia.org/wiki/List_of_HTTP_header_fields). 
    A WSGI Application must simply call this object run() method with the 
    application environ dictionary and a given url (usually, but it needs not to be, 
    environ['PATH_INFO']) as arguments: run(url, environ). 
    
    The run method, which should NOT be overridden, first "restores" default 
    settings (i.e., the three object fields defined above) and then calls 
    _process(url, environ) 
    The latter acts as a sort of abstract method where the internal class 
    fields are modified and manipulated according to this object needs. In the 
    base class, _process does nothing, meaning that a status 404 response will be 
    returned by default.
    
    Subclasses shall therefore implement the _process method to perform 
    custom operations and eventually set-up the fields self.status (string), 
    self.body (iterable) and self.headers (dictionary of string both in key and 
    values). Note that the latter is a dictionary, whereas the start_response 
    function of WSGI applications needs a list of tuples, because a dict has a more 
    flexible and user firendly syntax and allows keys replacement without the need 
    of a linear search for already existing keys. The user does not need any 
    dict to list conversion as it will be done automatically by the run() method 
    after the _process call. Note also that there exist an HTTPHeaders library, 
    but it does not seem to implement remarkable benefits which would overcome 
    our simple and clear dict implementation
    """
    
    _status404 = "404 Not Found"
    _status304 = "304 Not Modified"
    _status500 = "500 Unexpected server error"
    _status200 = "200 OK" 
    
    def __init__(self, *default_headers): #, environ, start_response, url):
        """ 
        Initializes a new ResponseHandler with the given headers, which is a 
        variable even length sequence of key_1, value_1, ..., key_N, value_N 
        elements which will populate the default response headers dict prior to 
        each _process(url, environ) method
        """
        self._default_headers={}
        leng = len(default_headers)
        leng -= leng % 2
        for i in range(0,leng,2):
            self._default_headers[default_headers[i]] = default_headers[i+1]
        #self.reset()
    
    def _reset(self, url=None):
        """Resets the internal fields: body is set to the empty list, status to the 404 status string and headers to a dict of the 
        headers passed in the constructor (__init__ method). This method is called from within the run method before calling self._process"""
        self.headers = self._default_headers.copy() #shallow copy. Before was: list(self._default_headers) #copy the list
        self.body = []
        self.status = ResponseHandler._status404
        if not url is None:
            if not "Content-Type" in self.headers:
                import mimetypes
                contentType =  mimetypes.guess_type(url)[0] or 'text/plain'
                self.headers["Content-Type"] = contentType
        
    def run(self, url, environ):
        """ 
        Method to be called by a WSGI application. It calls _process(url, environ). 
        After this call, the internal fields self.headers, self.status and 
        self.body are set. 
        The former two can be passed to the application start_response function 
        which is supposed to eventually return the third (self.body)
        """
        self._reset(url)
        try:
            self._process(url,environ)
            #environ.__iter__(4) #hack: test function to fall into the execpt below (for testing purposes)
            
#            if(isinstance(self.body, basestring)):
#                self.body = [self.body];
#            else:    
#                try:
#                    iterator = iter(self.body)
#                except TypeError:
#                    # not iterable
#                    return [""]
#                #else:
#                    # iterable: do nothing
        except:
            #NOTE: content-length does not seem to be mandatory, see
            #http://www.techques.com/question/1-6919182/Is-Content-length-the-only-way-to-know-when-the-HTTP-message-is-completely-received
            #As it involves more calculation, we omit if it is not retriavable without the risk  of performance loss
            if CARAVAN_DEBUG:
                traceback.print_exc()
            self.headers = {} #re-init the dict
            self.headers['Content-Type'] = 'text/plain'
            strlen=0
            if environ["REQUEST_METHOD"] == "HEAD":
                self.body = [""]
            else:
                
                import StringIO
                output = StringIO.StringIO()
                output.write("A server error occurred.") #message copied from what I got in in the browser in case of unexpected error
                if CARAVAN_DEBUG:
                    output.write("\n")
                    traceback.print_exc(file=output)
                    #get string value (this is the part which has the best benefits over performances compared to strings):
                output_str = output.getvalue()
                #wrap the error message, set content length, go on...:
                self.body = [output_str]
                strlen = len(output_str)
                
            self.headers['Content-Length'] = str(strlen)
            self.status = ResponseHandler._status500;
        
        
        self.headers = list(self.headers.items()) #update headers into a list of tuples. Note that there exists the wsgiref.Headers class but it doesn't seem to be great...
        #Note on line above: Python3 converts to list the dict items(), which the new view of the dictionary's items ((key, value) pairs))
        #In python <3, copies the list the dict items(), which is already a list of (key, value) pairs.
        #The method above, although not entirely efficient in Python <3 (the list part could be removed) assures compatibility between Python versions.
            
        
    def _process(self,url,environ):
        return

class StaticFileResponseHandler(ResponseHandler):
    def _process(self, url, environ):
        #This code is copied and modified from WSGI+jQuery example (on Stackoverflow)
        #and static.py file (FIXME: add url)
        if os.path.exists(url): 
            #code copied and modified from https://bitbucket.org/luke/static/raw/b0a7c7b4991d3e9f16e2eb7fb57afa0df786f375/static.py
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
                self.headers.pop('Content-Type',None) #remove content type (validators -defined in manage.py - complains otherwise)
                self.status = ResponseHandler._status304 #'304 Not Modified'
                if CARAVAN_DEBUG:
                    print "\tcontent not modified, returning 304"

                return
            
            #add headers, now:
            self.headers['Date'] = email.utils.formatdate(time.time())
            self.headers['Last-Modified'] = last_modified
            self.headers['ETag'] = etag
            
            self.status = ResponseHandler._status200
            
            body = self.get_content(url, environ)
            if isinstance(body, basestring):
                self.body = [body]
                return
            
            #Copied from http://legacy.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling
            if 'wsgi.file_wrapper' in environ:
                self.body = environ['wsgi.file_wrapper'](file(url,'r'))
            else:
                #return iter(lambda: filelike.read(block_size), '') #FIXME: does it close the file? Where? to be sure, for the moment I use:
                #LINE HERE BELOW COMMENTED... NO RETURN! SET self.body (FIXME: check!)
                #return [_read(url)] or [""]; 
                self.body = [_read(url)] or [""];
        
    
    def get_content(self, url, environ):
        """
            Returns the content of the requested page in string format. 
            Any other return object (e.g., None) will perform the custom server operation 
            (returning a file_like object of url) along the line of
            http://legacy.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling
            
            By default, this method returns None. Subclasses might override this method to perform, e.g., dynamic page service
        """
        return None
        

import globals

class MainFileResponseHandler(StaticFileResponseHandler):
    def get_content(self, url, environ):
        data = _read(url)
        
        gmpes = globals.def_gmpes
        



        
        #FIXME: string concat and string escape! CHECK!!!
        #FIXME: option disabled on not defined function!
#        str=""
#        for v in gmpes:
#            val = gmpes[v]
#            str += "<option value="+v+" data-description="+val['description']+">"+val['name']+"</option>"
        
        #this seems to be the fastest way to concat strings,
        #see http://www.skymind.com/~ocrow/python_string/
        str = ''.join(["<option value=\"%d\" data-description=\"%s\"%s>%s</option> " \
        % (k,escape(v['description'],True)," disabled" if v["function"] is None else "",escape(v['name'],True)) for k,v in gmpes.iteritems()])
        
        if CARAVAN_DEBUG:
            print "ipes:"
            print str
        
        #TWO OPTIONS: STRING REPLACE VS REGEX REPLACE
        #USE STRINGS (MAYBE FASTER?) BECAUSE WE DO NOT NEED TO EXPLOIT REGEXP FEATURES
        
        data = data.replace("{% GMPES %}", str)
        
        #import re
        #reg = re.compile("\{% GMPES %\}") #{% GMPES %}
        #data = reg.sub(str, data)
        
        return data
        
class QueryEventsResponseHandler(ResponseHandler):
    def _process(self, url, environ):
        
        if environ["REQUEST_METHOD"] != "POST":
            raise Exception("Request needs to be called via a POST method, '"+environ["REQUEST_METHOD"]+"' found")
        
        
        
        import fdsnws_events as fe 
        
        #copied from WSGI + jQuery example: http://stackoverflow.com/questions/12365970/wsgi-jquery-example
        request_body_size = int(environ["CONTENT_LENGTH"])
        request_body = environ["wsgi.input"].read(request_body_size)
        
        parsed_body = parse_qs(request_body)
        #from https://docs.python.org/2/library/urlparse.html#urlparse.parse_qs:
        #-----
        #parse_qs returns a dictionary: the dictionary keys are the unique query variable names 
        #and the values are lists of values for each name.
        #-----
        #The dictionary is returned by parsing a query string given as a string argument (data of type application/x-www-form-urlencoded.
        #In our case, e.g., 'url=http%3A%2F%2Fwww.seismicportal.eu%2Ffdsnws%2Fevent%2F1%2Fquery%3Fminmagnitude%3D6.8%26maxmagnitude%3D6.8'
        #just write print str(request_body) to check it)
        
        xmlurl = parsed_body['url'][0]  #DO NOT ESCAPE, IT IS AN URL!!! 
        #FIXME: is it ok to pass urls? maybe I should pass parameters, escape them, and then build here the url?
        #escape(parsed_body['url'][-1]) #-1: last list element. Always escape user input to avoid script injection
        
        
        
        #NEVER throw exceptions: when querying events, we need to return the source url
        #so that the browser knows if we clicked meanwhile nother request
        try:
            
            def parse_depth(val):
                try:
                    if val[0] is not None : val[0] /= 1000
                    if val[1] is not None : val[1] /= 1000
                except:
                    pass
            value = fe.get_events(xmlurl, _required_=fe.DEF_NUMERIC_FIELDS, _callback_={fe.F_DEPTH: parse_depth}) #getCaravanEvents(xmlurl)
            value = {'url':xmlurl, 'events':value}
        except Exception as e:
            value = {'url':xmlurl, 'error': str(e)}
            if CARAVAN_DEBUG:
                traceback.print_exc()
#        str_=""
#        for event in value:

#            str_+=str(event)+"\n"
            
        self.status = ResponseHandler._status200
        #self.headers['Content-type'] = 'application/json'
        self.body = [json.dumps(value, separators=(',',':'))]

#        self.headers['Content-length'] = str(len(value))
        

RUNS ={}
#from random import choice as random_choice
#def new_session_id():
#    """
#        Generates a random ID number. It is the concatenation of 
#        T + '_' + R
#        where T is the string value of an approximation of the current time (in milliseconds)
#        and R is a string of 10 random alpha numeric characters
#    """
#    #get current time:
#    millis = str(int(round(time.time() * 1000)))
#    
#    #generate a alphanumeric random string of N characters
#    #Example taken and modified from:
#    #http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/2257449#2257449
#    N=10
#    suffix = ''.join(random_choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(N))
#    #Notes on the function above:
#    #_ It's just a variable name, and it's conventional in python to use it for throwaway variables. 
#    #It just indicates that the loop variable isn't actually used.
#    #see here: http://stackoverflow.com/questions/5893163/underscore-in-python
#    #The argument to random.choice might also be string.ascii_uppercase + string.digits, but we should 
#    #import string for just one line of code (which btw is also more readable as it is)
#    #random_choice is random.choice, imported above
#    #the join function is the same as JavaScript join: left hand function is the separator, 
#    #and right hand is a list of elements to be joined with the given separator
#    return "%s_%s" % (millis, suffix)

class JsonResponseHandler(ResponseHandler):
    def __init__(self, *default_headers): #, environ, start_response, url):
        """ 
        Initializes a new JsonResponseHandler. Calls the super constructor and 
        overrides the header 'Content-Type' to be always 'application/json'
        """
        super(JsonResponseHandler, self).__init__(default_headers)
        self._default_headers['Content-type']= 'application/json'
        
    def _process(self, url, environ):
        value={'error': "Request needs to be called via a POST method, '"+environ["REQUEST_METHOD"]+"' found"}
        try:
            if environ["REQUEST_METHOD"] == "POST":
                #copied from WSGI + jQuery example
                request_body_size = int(environ["CONTENT_LENGTH"])
                request_body = environ["wsgi.input"].read(request_body_size)

                
                
                event = json.loads(request_body) 
                #using parse_qs and parse_qsl does not work with JSON
                #The best approach (which seems to be inefficient to me)
                #is encoding a javascript plain object to string client side
                #and parsing to python dict server side (here)
                #googling a bit might reveal some better solutions, for the moment
                #I found this one
                
                #dict(parse_qsl(request_body)) #parse_qsl returns a list, dict converts into list
                #note that WE SUPPOSED request body to be a dict of UNIQUE keys
                #For more info, see: http://stackoverflow.com/questions/1024143/how-to-stop-python-parse-qs-from-parsing-single-values-into-lists
                #SECOND ANSWER
                
                if CARAVAN_DEBUG:
                    print "json: "+ str(event)+" from within "+str(url)
                
                    
                
                #event = parsed_body['event'][0]  

                #call caravan_run

                #return session_id and scenario_id

                value = self.processjson(event, url, environ)
        except Exception as e:
            if CARAVAN_DEBUG:
                traceback.print_exc()
            value = {'error': "Server error (url: "+url+"): "+str(e)}

            
        self.status = ResponseHandler._status200
        #self.headers['Content-type'] = 'application/json'
        self.body = [json.dumps(value, separators=(',',':'))]

    def processjson(self, jsonData, url, environ):
        """
            Returns a python object representing the repsonse of a given json data
        """
        raise Exception("Abstract class JsonResponseHandler cannot be instantiated")


from core import caravan_run as run
from runutils import RunInfo
        
class RunSimulationResponseHandler(JsonResponseHandler):
    
    def processjson(self, jsonData, url, environ):
        if CARAVAN_DEBUG:
            print "jsonData ("+self.__class__.__name__+"):\n"+ str(jsonData)+"\n\n"
        #FIXME: CHECK INLINE IMPORT PERFORMANCES!!!
        runinfo = RunInfo(jsonData)

        if runinfo.status()==1: #running, ok
            #session_id = new_session_id()
            #RUNS[session_id] = runinfo #should we add a Lock ? theoretically unnecessary...
            runinfo.msg("Process started at "+time.strftime("%c"))
            run(runinfo)
            RUNS[runinfo.session_id()] = runinfo #should we add a Lock ? theoretically unnecessary...
            return {'session_id':runinfo.session_id(), 'scenario_id':0}
        else:
            #if CARAVAN_DEBUG:
            return {'error': "Run simulation error: "+str(runinfo)}


class QuerySimulationProgressResponseHandler(JsonResponseHandler):
    def processjson(self, jsonData, url, environ):
        
        event = jsonData
        
        if event['session_id'] in RUNS:
            runinfo = RUNS[event['session_id']]
            
            if event['stop_request']:
                runinfo.stop()
            
            status = runinfo.status()
            
            done = 100.0 if status > 1 else runinfo.progress()
            ret = {'complete': done} #int(done)}
            msgs = runinfo.msg()
            
            if msgs is not None and len(msgs):
                ret['msg'] = msgs
            
            #NOTE THAT THE STATUS MIGHT CHANGE IN PROGRESS< AS IT MIGHT SET AN ERROR MSG
            #INSTEAD OF RE_QUERYING THE STATUS, WE QUERY THE ERROR
            if runinfo.errormsg(): #status == 3:
                ret['error'] = runinfo.errormsg()
                
            return ret
        else:
            return {"error":"query progress error: session id %s not found" % str(event['session_id'])}
        
import globals

class QueryGMPEResponseHandler(JsonResponseHandler):
    def processjson(self, jsonData, url, environ):
        event = jsonData
        session_id = event['session_id']
        print "session id"+str(session_id)
        conn = globals.connection(async=True)
        #query:
        #note: ::json casts as json, not as jason-formatted string
        #::double precision is NECESSARY as it returns a json convertible value, otherwise array alone returns python decimals
        #which need to be converted to double prior to json dumps
        
        #NOTE: the columns below refer to the GEOJSON OBJECT AND NEED TO BE MODIFIED AS SOON AS WE MODIFY THE QUERY BELOW
        #FIXME: NEEDS MAYBE IMPROVEMENT (THIS IS NOT OPTIMAL)
        captions = ['geom', 'id','fatalities_prob_dist',  'fatalities_perc','gmpe_perc'] #FIXME: REMOVE THIS IS UGLY!!!!
        data = conn.fetchall(
"""SELECT 
    ST_AsGeoJSON(ST_Transform(G.the_geom,4326))::json AS geometry, GM.geocell_id, risk.social_conseq.fatalities_prob_dist::double precision[], risk.social_conseq.est_fatalities, ARRAY[GM.gm_q5,GM.gm_q25,GM.gm_q50,GM.gm_q75,GM.gm_q95]::double precision[] as gmp
FROM 
    processing.ground_motion as GM
INNER JOIN 
    risk.social_conseq ON (risk.social_conseq.geocell_id = GM.geocell_id and risk.social_conseq.session_id = GM.session_id)
INNER JOIN 
    exposure.geocells as G ON (G.gid = GM.geocell_id)
WHERE 
    GM.session_id=%s""",(session_id,)) #(session_id,))
        
        #conn.conn.commit()
        conn.close()
        
        #HYPOTHESES:
        #1) The query above returns a table T.
        #2) A geojson feature F has the fields
        #{type: 'Feture', gemoetry : dict, properties:dict}
        #3) a single T row (R) corresponds to a geojson feature F
        #4) each R contains AT LEAST the field 'geometry' AT INDEX 0 (see query above)
        #5) Any other column of R is set into the field 'properties' of F
        dataret = {"type": "FeatureCollection", "features": None}
        features = [] #pre-allocation seems not to matter. See e.g. http://stackoverflow.com/questions/311775/python-create-a-list-with-initial-capacity
        feature_str = 'Feature'
        #features length:
        feat_len = len(data)
        #pre-allocate row length
        row_len = 0 if feat_len<=0 else len(data[0])
        
        for i in xrange(feat_len):
            row = data[i]
            
            cell = {'geometry': row[0], 'type':feature_str, 'properties':{}}
            for j in xrange(1, row_len):
                cell['properties'][captions[j]] = row[j]
            
            features.append(cell)
        dataret['features'] = features
        dataret['percentiles_caption'] = [5,25,50,75,95]
        
        
        #FIXME: it returns a list of 1-element lists!!!
        #highly inefficient. For the moment we parse it to a geojson object
        #(see http://geojson.org/geojson-spec.html#examples)
#        dataret = {"type": "FeatureCollection", "features": None}
#        features = []
#        for i in xrange(len(data)):
#            cell = data[i][0]
#            cell['geometry'] = json.loads(cell['geometry'])
#            
#            features.append(cell)
#        dataret['features'] = features
#        dataret['percentiles_caption'] = [5,25,50,75,95]
        
#        print"===================="

#        print"===================="
        return dataret
       

#==============================================================================
#DICT BELOW NEEDS TO BE AT THE REAL END OF THE MODULE!!!!
#==============================================================================

#A Map of Request which will be used from the main application
#keys can be strings or regular expressions.
#values can be ResponseHandlers or string
#The idea is that strings might be associated to other strings to emulate "redirect" or faster ResponseHandlers (R) retrieval
#The algorithm in main_app to retrieve an R from a given url is: 
#   1) if that url is in REQUESTS_MAPS:
#       - if its value is a string, replace url with value and go to 1)
#       - otherwise, R is set as its value
#   2) otherwise, loop through all
REQUESTS_MAP = {\
    "caravan" : "index.html", \
#    re.compile(r"^stop_simulation*$", re.IGNORECASE) : StopSimulationResponseHandler('Content-type', 'application/json','Accept', 'text/plain'), \
    re.compile(r"^query_gmpe*$", re.IGNORECASE) : QueryGMPEResponseHandler(), #'Content-type', 'application/json'), #,'Accept', 'text/plain'), \
    re.compile(r"^query_simulation_progress*$", re.IGNORECASE) : QuerySimulationProgressResponseHandler(), #'Content-type', 'application/json'), #,'Accept', 'text/plain'), \
    re.compile(r"^run_simulation*$", re.IGNORECASE) : RunSimulationResponseHandler(), #'Content-type', 'application/json'), #,'Accept', 'text/plain'), \
    re.compile(r"^query_events*$", re.IGNORECASE) : QueryEventsResponseHandler(), #'Content-type', 'application/json'), #,'Accept', 'text/plain'), \
    re.compile(r"^index.html*$", re.IGNORECASE) : MainFileResponseHandler('Content-Type',"text/html; charset=UTF-8"), \
    re.compile(r"\.css$", re.IGNORECASE) : StaticFileResponseHandler('Content-Type',"text/css"), \
    #re.compile(r"\.html*$", re.IGNORECASE) : StaticFileResponseHandler('Content-Type',"text/html; charset=UTF-8"), \
    re.compile(r"\.js$", re.IGNORECASE) : StaticFileResponseHandler('Content-Type',"text/javascript"), \
    re.compile(r"\.xml$", re.IGNORECASE) : StaticFileResponseHandler('Content-Type',"text/xml"), \
    #re.compile(r"^query_catalog$", re.IGNORECASE) : StaticFileResponseHandler('Content-Type',"application/json"),
    re.compile(r"\.(?:jpg|jpeg|bmp|gif|png|tif|tiff)$", re.IGNORECASE) : StaticFileResponseHandler(), \
}

#FIXME: NOT YET IMPLEMENTED -- Static http headers list. There are tons of Python modules regarding MIME types but 
#I did not find any python module which incorporated in a clear way these fields
#See http://en.wikipedia.org/wiki/List_of_HTTP_header_fields



if __name__ == '__main__':
    #min_dist(7, 15, 5, 20)
    event = {u'longitude':74.2344, u'latitude':'42.8', u'depth':'15    4 6', u'strike':0, u'ipe':2, u'magnitude':6.8}
    print str(event)
    print str(pre_parse(event))
  

#OLD STUFF = TO BE REMOVED:

#def main_app_old(environ, start_response): 
##    show_environ = 0
##    if(show_environ):
##        response_headers = [('Content-Type', 'text/html')] #,
##                       #('Content-Length', str(len(response_body)))]
##
##        # Send them to the server using the supplied function
##        start_response('200 OK', response_headers)
##        
##        list=[]
##        for k in environ:
##            list.append("<br> %s: %s" % (k, environ[k]))
##        return list
#    
#    #url = environ['PATH_INFO'] #util.request_uri(environ) 
#    
#    
#    #url = url.lstrip("/") ##remove leading slash
#    #if(url == 'caravan'):
#        #url = 'index.html'
#    
#    
#    url = _getUrl(environ)
#    
#    for k in CONTENT_TYPES:
#        
#        if(k.search(url)): #FIXME: search or matches is faster??
#            content_type = CONTENT_TYPES[k]
#            
#            
#            response_lines = _read(url);
#            if(not response_lines is None):
#                start_response('200 OK', [('Content-Type', content_type)]) 
#
#                return response_lines
##            if os.path.exists(uri): 
##                file_obj = open(uri, 'r') 
##                response_lines = file_obj.readlines() 
##                file_obj.close() 
##                start_response('200 OK', [('Content-Type', content_type)]) 
#
##                return response_lines 
#            else: 
#                break;
#                #start_response('404 Not Found', []) 
#                #return []
#    start_response('404 Not Found', []) 
#    return [environ['PATH_INFO'] + " Not found"]


#=========================================================================

#def main_app(environ, start_response): 
#    """Main Caravan (Web) Application, i.e. the function which handles
#    the requests from and to the server. It makes use of REQUEST_MAP and RequestProcessor class
#    (see in the code)
#    """
#    
#    
#    url = environ['PATH_INFO'] 
#    if(url):
#        url = url.lstrip("/")
#    
#    request_processor = None
#    
#    if(url in REQUESTS_MAP):
#        
#        url = REQUESTS_MAP[url]
#        
#    for k in REQUESTS_MAP:
#        if(isinstance(k, basestring)):
#            continue
#            
#        if(k.search(url)): #FIXME: search or matches is faster??
#            request_processor = REQUESTS_MAP[k]
#            break;
#                #start_response('404 Not Found', []) 
#                #return []
#    
#    if(request_processor is None):
#        request_processor = RequestProcessor()
#    
#    request_processor.update(url, environ)
#    start_response(request_processor.status, request_processor.response_headers) 
#    
#    return request_processor.response_body    
#    
#
#
#class RequestProcessor(object):
#    _status404="404 Not Found"
#    def __init__(self, *response_headers): #, environ, start_response, url):
#        self._default_response_headers=[]
#        leng = len(response_headers)
#        leng -= leng % 2
#        for i in range(0,leng,2):
#            self._default_response_headers.append((response_headers[i], response_headers[i+1]))
#        self.reset()
#        
#    def reset(self):
#        self.response_headers = list(self._default_response_headers) #copy the list
#        self.response_body = []
#        self.status = RequestProcessor._status404;
#        
#    def update(self, url, environ):
#        self.reset()
#        try:
#            self.process(url,environ)
#        except:
#            excError = "Unexpected Python error: (type" + str(sys.exc_info()[0].__name__) + ")"
#            self.response_headers = [('Content-Type', 'text/plain'),
#                   ('Content-Length', str(len(excError)))]
#            
#            #raise
#            traceback.print_exc()
#            self.response_body = [excError]
#            self.status = RequestProcessor._status404;
#        #return
#        #return []
#        
#    def process(self,url,environ):
#        return
#
#class FileContentRequestProcessor(RequestProcessor):
#    def process(self, url, environ):
#        file_body = _read(url);
#        
#        if(not file_body is None):
#            self.status = '200 OK'
#            self.response_body = [file_body] #needs to be an iterable or a list
#            self.response_headers.append(('Content-Length', str(len(file_body))));
#        else: 
#            self.response_body = [url + " Not found"]; #FIXME handle not found as exception in order to set content type etcetera
#            return;
#        
##    def process(self, url, environ):
##        #file_body = _read(url);
##        file_lines = _readLines(url);
##        
##        #if(not file_body is None):
##        if(not file_lines is None):
##            
##            self.status = '200 OK'
##            self.response_body = file_lines #[file_body] #needs to be an iterable or a list
##            #needs the whole lengh, therefore:
##            totlen=0
##            for k in range(len(file_lines)):
##                totlen += len(file_lines[k]) 
##            self.response_headers.append(('Content-Length', str(totlen)));
##        else: 
##            self.response_body = [url + " Not found"];
##            return;
#
#class MainPageRequestProcessor(FileContentRequestProcessor):
#    def process(self, url, environ):
#        #call super method
#        super(MainPageRequestProcessor, self).process(url, environ)
#        file_body = self.response_body #= [file_body] #needs to be an iterable or a list
#        
#        
#        
#        getenv = environ['QUERY_STRING']
#        jsScript = ""
#        
#        if getenv:
#            
#            #return
#        
#            #Code copied from http://webpython.codepoint.net/wsgi_request_parsing_get
#            # Returns a dictionary containing lists as values.
#            #From https://docs.python.org/2/library/urlparse.html#urlparse.parse_qs:
#            #Parse a query string given as a string argument (data of type application/x-www-form-urlencoded). 
#            #Data are returned as a dictionary. 
#            #The dictionary keys are the unique query variable names and the values are lists of values for each name.
#            d = parse_qs(getenv)
#            jsScript = "var element;var $=jQuery; //initialize once jQuery\n"
#            for key in d:
#                val = escape(d[key][-1]) #-1: last list element. Always escape user input to avoid script injection
#                jsScript += "\t\telement = $('#%s'); if(element.length && element.attr('value')){element.val(%s);}\n" % (key,val)
#            
#        
#        self.response_body = [file_body[0] % jsScript]
#        #replace the content-length header:
#        self.response_headers[1] = ('Content-Length', str(len(self.response_body[0])));


#class MainPageResponseHandler(ResponseHandler):
#    """Implements a REsponse handler which parses get and substitutes them in the page. 
#    DEPRECATED, NOT USED, LEFT FOR TEST PURPOSES"""
#    def _process(self, url, environ):
#        
#        file_body = _read(url);
#        if file_body is None:
#            return
#        self.status = ResponseHandler._status200
#        
#        #FIXME: use django-like variables like {{% VARNAME %}} ??
#        #FIXME: use StringIO (faster) for concatenating strings
#        #FIXME: skip if get is empty??
#        
#        #Read query string, if any:
#        getenv = environ['QUERY_STRING']
#        jsScript = ""
#        
#        if getenv:
#            #Code copied from http://webpython.codepoint.net/wsgi_request_parsing_get
#            # Returns a dictionary containing lists as values.
#            #From https://docs.python.org/2/library/urlparse.html#urlparse.parse_qs:
#            #Parse a query string given as a string argument (data of type application/x-www-form-urlencoded). 
#            #Data are returned as a dictionary. 
#            #The dictionary keys are the unique query variable names and the values are lists of values for each name.
#            d = parse_qs(getenv)
#            jsScript = "var element;var $=jQuery; //initialize once jQuery\n"
#            for key in d:
#                val = escape(d[key][-1]) #-1: last list element. Always escape user input to avoid script injection
#                jsScript += "\t\telement = $('#%s'); if(element.length && element.attr('value')){element.val(%s);}\n" % (key,val)
#            
#        #replace content: 
#        self.body = [file_body % jsScript]
#        #update the content-length header:
#        self.headers['Content-Length'] = str(len(self.body[0]));