#! /usr/bin/python

"""
Web Service FDSN events (fdsnws-events) are events accessible from Web Services 
within the context of the International Federation of Digital Seismograph Networks 
(FDSN). This module implements a sibgle function to return a list of fdsnws events 
from a simple url query (for info, see http://www.fdsn.org/webservices/FDSN-WS-Specifications-1.1.pdf)
Each fdsn-event is a Python dictionary holding the specified fields and relative 
values. 

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)"
__date__ ="$Jun 13, 2014 3:26:27 PM$"

import urllib
from lxml import etree
#from types import *
from math import isnan as _isnan #prevents isnan to be displayed in pydoc
#import json
import re
from collections import OrderedDict


def _parse(value, except_value = float('NaN'), nan_is_numeric=True):
    """Returns value parsed to float (via the function float(value)) 
    with more freedom to control the returned value. 
    Parameters:
    - except_value (NaN by default) is the value returned on errors, e.g., when trying to parse dicts (float({})). 
    - nan_is_numeric tells whether nan values should be treated as numeric (this is the default) 
    or should be treated as errors (in this case nan values will return except_value)
    
    Note that this function is handy in that it can be used also to get if value is either 
    a number or a numeric string via, e.g.:
    
        if _parse(value, None, False) is not None
    """
    try:
        val = float(value)
        if not nan_is_numeric and _isnan(val):
            return except_value
        else:
            return val
    except: 
        return except_value
      
T_QUACKEML = 'quakeml'
T_EVENTPARAMS = 'eventParameters'
T_EVENT = "event"
T_UNCERTAINTY = "uncertainty"

F_ID =  "EventId"
F_TIME =  "Time"
F_LAT =  "Latitude"
F_LON =  "Longitude"
F_DEPTH =  "Depth"
F_AUT =  "Author"
#F_CAT =  "Catalog"
#F_CONTRIB =  "Contributor"
#F_CONTRIB_ID =  "ContributorId"
F_MAG_TYPE =  "MagType"
F_MAG =  "Magnitude"
F_MAG_AUT =  "MagAuthor"
F_LOC = "EventLocationName"
F_UNC = "Uncertainty"

PATHS = OrderedDict()
PATHS[F_ID] ='.[@publicID]'  
PATHS[F_TIME] ='./origin/time/value'
PATHS[F_LAT] ='./origin/latitude/value'
PATHS[F_LON] ='./origin/longitude/value'
PATHS[F_DEPTH] ='./origin/depth/value'
PATHS[F_MAG_TYPE] ='./magnitude/originID/type'
PATHS[F_MAG] ='./magnitude/mag/value'
PATHS[F_MAG_AUT] ='./magnitude/creationInfo'
PATHS[F_LOC] = "./description/text"

DEF_NUMERIC_FIELDS = [F_LAT, F_LON, F_DEPTH, F_MAG]
DEF_QUERY_FIELDS = [F_ID, F_TIME, F_LAT, F_LON, F_DEPTH, F_MAG, F_LOC]

FDSN_CATALOG = {
    'EMSC' : "http://www.seismicportal.eu/fdsnws/event/1/query?",
    'IRIS' : "http://service.iris.edu/fdsnws/event/1/query?",
    'INGV' : "http://webservices.rm.ingv.it/fdsnws/event/1/query?"
}
                            
def _read(url_or_etree):

    """
        Returns a tuple where the first element is the xml global namespace (or "" if no such namespace) and the second element 
        is an iterator over all XML elements denoting an FDSN event. The argument can be a string denoting the url of a valid 
        multi- or single-FDSN event query, or an etree, a Python object representing an HTML and XML elements. 
        The function returns None in case of failure and errors
    """
    exceptErr=None
    try:
        root = url_or_etree
        if isinstance(root, basestring):
            #if we are passing a string, we might expect exceptions from the catalog server
            #These exceptions are returned as string from the urlopen.
            #Therefore, first read the url (temporarily store it into exceptErr):
            exceptErr = urllib.urlopen(url_or_etree).read()
            #and then parse it. If we got an error (e.g.: too many events) exceptErr (a string) holds the error message therefore 
            #it won't be parsable by the function below:
            root = etree.fromstring(exceptErr) 
            #otherwise, if we are here, then everything is fine and we can re-set exceptErr to None
            exceptErr = None

        #do a check to see if it is a valid quackeml. Note that we have namespaces and things get a bit comples.
        #First check: element root has tag q:quackeml, where q is a namespace. Therefore the root tag will return {...}quackeml
        #For the moment, we just check that the tag is well formed
        reg = re.compile("(?:{.*})*"+T_QUACKEML)
        if reg.match(root.tag):
            namespacemap = root.nsmap
            #get global namespace, if any. This will modify ALL tags inside the root
            base_ns = namespacemap[None]
            eventsParameterTag = root[0]
            base_ns_str = "" if not base_ns else "{"+base_ns+"}"
            if eventsParameterTag.tag == base_ns_str+T_EVENTPARAMS:
                return (base_ns_str, root.iter(tag=base_ns_str+T_EVENT))
            #else:
                
        #else:
            

        return (None,None)
    except Exception as e:
        #in this case, return the 
        if isinstance(exceptErr, basestring):
            raise Exception(exceptErr)
        import traceback
        traceback.print_exc()
        raise e
        #return (None, None)
 
def get_events(root, *keys, **options):
    """
    
    Returns a Python list representing all FDSN events parsed from an FDSN event 
    query. Each event will be returned as a Python dictionary D which will hold 
    the user-specified keys (representing the FDSN event fields) and the relative 
    values.
    ____________________________________________________________________________
    From an FDSN event query in the following xml form
    
        <q:quakeml ...>
            <eventParameters publicID=...>
                <event publicID=...>...</event>
                <event publicID=...>...</event>
                ...
            </eventParameters>
        <q:quackeml>
    
    a dictionary D associated to each <event> element is created and populated 
    of keys K and relative values V by means of the *keys argument, a 
    comma-separated sequence of strings denoting one or more "default keys" such 
    as <m>.FDSN_KEY_LAT (='Latitude'), where <m> denotes this module name after 
    import in your python code. "F_" stands for event (F)ield.
    For each K in *keys, the value V of D[K] is retrieved by means of a path P 
    in string format associated to K and declared in the constant dict <m>.PATHS, 
    so that the <event> element descendants are scanned to get V. 
    We will always use K, P, V to denote a D key, path and value associated to 
    one of the *keys elements
    
    The user can also specify custom names or paths, by writing one of the 
    *keys element in the format "name=path". K as defined above will be 'name'  
    (part of the string preceeding '=') and P='path' will be then used as 
    custom path to get V.
    The path must be given in XPath format (e.g., "./event/magnitude/type" 
    will search the sub-element <type> and set V = <type>'s text, 
    "./event/magnitude/type[@attname]" will search the sub-element <type> with 
    attribute 'attname' and set V = <type>'s 'attname' value). Paths MUST be case 
    sensiitive (according to XML format) and do NOT have to account for namespaces, 
    which makes etrees displaying a tag name in the form "{namespace}tag" and 
    would worsen custom path implementation efforts: namespaces handling is 
    harcoded in the function. For details, see *keys parameter doc below
    
    For a *key element K whose path does not have a coorresponding xml element, 
    V will default to None (consequently D[K] = None). A dictionary D holding 
    None values might be considered not well formed and therefore undesirable:
    by default this function does not return such D's. 
    The user can anyway control this behaviour and relax some conditions 
    (see parameter "_required_" below). The user can also decide whether some 
    K is numeric (meaning that the relative V will be parsed to float. 
    See parameter "_numeric_" below). Numeric K's basically do two things: 
    1) Their associated V is parsed to float before asssignment, so D[K] = float(V) is 
        actually performed (if float function fails, then D[K] = None and the 
        case is treated as if P did not find the xml element)
    2) They perform a further scan in the <event> element to set their 
        uncertainty: if V=D[K] is a valid non NaN float, the function 
        takes P and scans also the P element siblings. If an xml 
        element with tag namee <m>.T_UNCERTAINTY ('uncertainty') is found and it 
        holds a valid number u, then U[K] = u is set, where 
        U = D[<m>.F_UNC] (<m>.F_UNC = "Uncertainty". U is first created if not in D). 
        Any exception involved in uncertainty scan will not add the corresponding 
        uncertainty key to U, so if the latter exists in D, it is a dictionary 
        holding at least one key associated to a valid (non-nan) value. This also 
        means that in most cases there is no need to specify any <m>.F_UNC in *keys
    ____________________________________________________________________________
    Function arguments:

    .: root: can be either a string denoting an url of the specified FDSN event 
        query, or an etree, a Python object representing an xml or html 
        document. By default, this function creates html documents from string 
        root arguments, being the html more easily processable. 

    .: keys: a list of arguments indicating the keys to be added to D. 
        The declaration order matters as it will be maintained in each D keys 
        (when e.g., looping thorugh them). 
        If missing it defaults to <m>.DEF_QUERY_FIELDS (again, <m> denoting 
        this module name): 
            <m>.F_ID =  "EventId"
            <m>.F_TIME =  "Time"
            <m>.F_LAT =  "Latitude"
            <m>.F_LON =  "Longitude"
            <m>.F_DEPTH =  "Depth"
            <m>.F_MAG =  "Magnitude"
            <m>.F_LOC = "EventLocationName"
        Otherwise, it is a list of strings whose syntax is either
            1) "name1", ..., "nameN" where each string denotes one of the 
                default keys: 
                <m>.F_ID = "EventId", 
                <m>.F_TIME =  "Time", 
                <m>.F_LAT ("Latitude"), 
                <m>.F_LON ("Longitude"), 
                <m>.F_DEPTH ("Depth"), 
                <m>.F_MAG_TYPE ("MagType"),
                <m>.F_MAG ("Magnitude"), 
                <m>.F_MAG_AUT = ("MagAuthor"), 
                <m>.F_LOC ("EventLocationName"), or    
            2) "name_1=path_1", ..., "name_N=path_N" where "name_1",..., "name_N" 
                denote custom keys and path_1,...,path_N the relative key path
                within the xml document. Paths in this case must follow the 
                XPath syntax ("e.g., ./element/subelement", where each path MUST
                start with ".", the dot denoting the <event> tag. See 
                http://www.w3.org/TR/xpath/). XPath is partially but sufficiently 
                supported by etree objects for the case at hand 
                (see https://docs.python.org/2/library/xml.etree.elementtree.html#supported-xpath-syntax). 
                If a path path_K points to a valid <event> xml sub-element, this 
                function returns as value for D['name_K'] the sub element text, 
                unless a path is of the form "./element/subelement[@attname]":
                In XPath syntax, the "[@attname]' can be present everywhere in 
                the path and denotes that an element with given attribute name 
                ('attname') must be selected. In this function, and only if 
                AT THE END of the path, an '[@attname]' string also indicates 
                that the sub-element given attribute value (instead of its text) 
                must be assigned to D['name_K']. To return the root "<event>" 
                attribute name A, specify ".[@A]"
        
        Note that for each D key which is numeric (by default, an attempt to read its 
        uncertainty, if any, is made. Uncertainties are stored in the dict 
        D[<m>.F_UNC], (<m>.F_UNC = 'Uncertainty') so there is no need to create 
        a special custom key for that.
        
    .: options: a list of variable length arguments controlling which D must be 
        returned. E.g.: 
            get_events(...,_numeric_ = <m>.F_LAT, _required_= None)
        
        options arguments can be 
        
        "_callback_", [dict of keys associated to functions] a dict of keys 
        (as specified above, e.g., <m>.F_ID) associated to callback functions for 
        custom-argument parsing, after the key has been found and parsed.
        The function takes a 2-ELEMENT LIST which represents as first element 
        the key parsed value and (if numeric and uncertainty is found) its 
        uncertainty as second element. 
        The list arguments are either strings, numbers (if key is specified as numeric, see below) 
        or None, meaning that the value has not been found. The function might 
        be never called if an exception has thrown before. The function may throw 
        itself exceptions. Obviously, if the key specified in _callback_ is not 
        parsed (either because is neither a default key nor is specified as function 
        argument) the callback will never be executed
        
        "_required_", [list|None|'*'] (see *note below), meaning that for 
        each D the given keys are required to be not None, otherwise D will not 
        be added to the returned event list. None values are by default set 
        when P does not point to an existing xml sub-element, but can also be set 
        for numeric *keys whose V is not parsable as float (see _numeric_ below).
        If missing, '_required_' defaults to: "*" (all given *keys are required)
        
        "_numeric_"=[list|None|'*'] (see *note below), meaning that for each D 
        the values of the keys given as _numeric_ need to be parsed and converted 
        to float before assignment to D. Unparsable values will be assigned as 
        None (D[k] = None). If missing, '_numeric_' defaults to: 
        [<m>.F_LAT, <m>.F_LON, <m>.F_DEPTH, <m>.F_MAG] (<m>.DEF_NUMERIC_FIELDS)
        
        *note: '*' or 'All' means: all given *keys, None is self-explanatory, 
        otherwise it must be a list of one or more *keys names. 
    ____________________________________________________________________________
    Examples
    
    #After importing this module such as
    
    import fdsnws_events as fe
    
    #and given an url variable such as
        url = "http://service.iris.edu/fdsnws/event/1/query?minmag=8.5&maxmag=9"
        
    #then
    
    ret = fe.get_events(url, _required_=None)
    
    #    will return a list of fdsn events. Each event E is basically of the form:
    #    
    #    D = {
    #        fe.F_ID:       [string|None], 
    #        fe.F_TIME:     [string|None], 
    #        fe.F_LAT:      [float|None], 
    #        fe.F_LON:      [float|None], 
    #        fe.F_DEPTH:    [float|None], 
    #        fe.F_MAG:      [float|None], 
    #        fe.F_LOC:      [string|None], 
    #        fe.F_UNC:      [dictionary]
    #    }
    #    
    #    where D keys are the default query keys: 
    #
    #    fe.DEF_QUERY_FIELDS = [
    #        fe.F_ID = "EventId", 
    #        fe.F_TIME = "Time", 
    #        fe.F_LAT = "Latitude",
    #        fe.F_LON = "Longitude", 
    #        fe.F_DEPTH = "Depth", 
    #        fe.F_MAG = "Magnitude", 
    #        fe.F_LOC ="EventLocationName"
    #    ]
    #
    #    Note that fe.F_UNC = "Uncertainty" might not exist as key 
        
    ret = fe.get_events(url)
    
    #    will return the same list as above, but each D cannot have None as 
    #    value (being in this case '_required_' omitted, therefore each key is 
    #    required to be not None by default)
        
    ret = fe.get_events(url, _required_=fe.F_MAG)
    
    #    will return the same list as above but for each D only the key
    #    'Magnitude' is assured to be not None
    
    ret = fe.get_events(url, fe.F_MAG, fe.F_LAT)
    
    #    will return the same list as above but with only keys 
    #    'Magnitude' and 'Latitude'. '_required_' is not specified and defaults 
    #    to the given keys. Therefore, D will have those keys values not None
    
    ret = fe.get_events(url, fe.F_MAG, fe.F_LAT, _numeric_=None)
    
    #    (more relaxed case) will return the same list as above but the keys will 
    #    be strings. If there where cases in the previous example for which a D 
    #    had a key whose value resulted in NaN after parsing, it wasn't added 
    #    there but will be added here as None. Also, the key D[fe.F_UNC] 
    #    will NOT be present as everything is string (fe.F_UNC='Uncertainty')
        
    ret = fe.get_events(url, fe.F_MAG, fe.F_LAT, _numeric_=None, _required_=None)
    
    #    (even more relaxed case) will return the same list as above but 
    #    the keys will not need to be required. If there where cases in the 
    #    previous example of <events> without a specified path for FDSN_KEY_MAG 
    #    or FDSN_KEY_LAT, the relative D wasn't added there but will be added 
    #    here with relative value None. As in the previous case, the key 
    #    D[fe.F_UNC] will NOT be present
        
    ret = fdsn_wget(url, 'MagAuthor=./origin/originID')
    
    #    will return a list of events D with only one key, 'MagAuthor', which is 
    #    assured to be not None, as it is required by default. 
    #    The key D[fe.F_UNC] will NOT be present as 'MagAuthor' is not 
    #    marked as numeric
    
    ret = fdsn_wget(url, 'MagAuthor=./origin/originID', _numeric_='MagAuthor', _callback_ = {'MagAuthor'=lambda val: val[1]=1})
    
    #    will return the same list as above, but each D['MagAuthor'] value 
    #    is assured to be a valid non nan float. Moreover (silly, but is just 
    #    an example, the MagAuthor uncertainty (second val element) is always set to 1. 
    #    This way, the the key D[fe.F_UNC] which MIGHT have been present being the 
    #    key numeric, it will always be present
        
    """
    
    ret = []
    
    (namespace, root) = _read(root)
    
    if root is None:
        return ret
    
    keys = OrderedDict() #preserves insertion order
    
    #first get if we specified required and numeric keys:
    required = options["_required_"] if "_required_" in options else "*"
    #remove all keyword and set it to '*'
    if required == 'all' or required == 'All' or required == 'ALL': required = '*' #Note required might be a list.
    #We could use lower BUT we need to see if it is a string. which is NOT PY2 PY3 compatible. So we leave it like this
    #with a 3times "or"
    numeric = options["_numeric_"] if "_numeric_" in options else DEF_NUMERIC_FIELDS
    callbacks = options["_callback_"] if "_callback_" in options else {}
    
    if not len(keys):
        if not len(PATHS):
            return ret
        else:
            keys = OrderedDict()
            for k in DEF_QUERY_FIELDS:
                keys[k] = PATHS[k]
    
    uncertaintyPath = "../"+T_UNCERTAINTY #defined as relative to the current parsed element
    
    
    
    #function to extract the value from an element
    #returns a 2element array V = [value, uncerntainty]
    #V[0] = None has to be interpreted as an error (according ro required: if True, the method is strict, otherwise relaxed and None is less likely to be returned)
    #V[1] = a number (not including NaN) or None (if numeric is False, it will be always None)
    def get_value(element, value, path, required, numeric, attr=None):
        #init value
        value[0] = None
        value[1] = None
        
        
        
        elm = element.find(path) #returns None if not found
        
        if elm is not None:
            if attr is None:
                value[0] = elm.text
            else:
                value[0] = elm.attrib.get(attr[1:]) 
            if numeric:
                value[0] = _parse(value[0], None, False)
            
        if value[0] is None:
            if required:
                return False
            else:
                return True
         
        if numeric: 
            #get uncertainty:
            elm = elm.find(uncertaintyPath)
            if elm is not None:
                
                value[1] = _parse(elm.text, None, False)
            
        return True
                            
    #build once the dict:
    re1 = re.compile('^(.*?)\\s*(?:=|:)\\s*(.*)$')
    re2 = re.compile('.*([^/]+)\[([^\]]+)\]$')
    #consider using namespace if present:
    re3 = re.compile('(/+)') #use a group as the group will be used in replace
    uncertaintyPath = re3.sub('\g<1>' + namespace, uncertaintyPath) #chnge uncerrtaintyPath according to namespace
    for k in keys:
        name = k
        
        path = None
        split = re1.match(name)
        if split:
            groups = split.groups()
            if len(groups)==2:
                name = groups[0]
                path = groups[1]
        
        if path is None:
            if k in PATHS:
                path = PATHS[name]
            else:
                if not path.startswith('./'):
                    if path.startswith('/'):
                        path = '.'+path
                    else:
                        path = None
            
        if path is None: 
            continue
        
        #rebuild the path if a namespace is given:
        if namespace:
            path = re3.sub('\g<1>' + namespace, path) #use \g<1> notation isnetead of \1 cause apparently \1{... does not work
            #and namespace starts with '{'
        
        num = numeric is not None and len(numeric) and name in numeric
        req = required == '*' or (required is not None and name in required)
        attr = None
        
        #find if there is an attribute:
        matchobj = re2.match(path)
        if matchobj:
            groups = matchobj.groups() #FIXME: check groups length!!! 
            if len(groups) == 2:
                attr = groups[1]
        
        if name in callbacks:
            
            _func = callbacks[name]
            def ret_func(element, value, p = path, r = req, n = num, a = attr):
                val = get_value(element, value, p, r, n, a)
                _func(value)
                return val
        else:
            def ret_func(element, value, p = path, r = req, n = num, a = attr):
                return get_value(element, value, p, r, n, a)

        keys[name] = ret_func
    
    #scan the element(s):
    value = [None,None] #buffer used in func bwloe
    for element in root:
        elm = OrderedDict() #preserves insertion order
        #declare an uncertainty dict as None, if not None AT THE END of the loop
        #add it to elm (so that it will be its last key)
        uncert = None
        for fekey in keys:
            
            name = fekey
            func_ = keys[name]
            
            assign_it = func_(element, value)
            
            if not assign_it: #value[0] is None:
                
                elm = None
                break;
                
            elm[name] = value[0]
                        
            if value[1] is None:
                continue
            #add uncertainty:    
            if uncert is None:
                uncert = {}
            uncert[name] = value[1]
        
        if not elm is None:
            if uncert is not None:
                elm[F_UNC] = uncert
            ret.append(elm)
            
    return ret

#def __jsonstr__(dict):
#    """Returns json.dump(self.data), i.e. a json (compact) formatted string representation of this object"""
#    return json.dumps(dict, separators=(',',':'))

#for debug (if executing from command line)
if __name__ == "__main__":
    url = [\
    #"http://service.iris.edu/fdsnws/event/1/query?minmagnitude=6.6&maxmagnitude=6.8",\
    #"http://comcat.cr.usgs.gov/fdsnws/event/1/query?minmagnitude=6.6&maxmagnitude=6.8",\
    "http://www.seismicportal.eu/fdsnws/event/1/query?minmagnitude=6.6&maxmagnitude=6.8",\
    #"http://webservices.rm.ingv.it/fdsnws/event/1/query?minmagnitude=6.6&maxmagnitude=6.8"\
    ]
    