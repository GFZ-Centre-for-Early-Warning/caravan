#! /usr/bin/python

"""
A module which holds global variables/objects for the Caravan application
Makes use of user_options.py and dbutils.py.

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Oct 28, 2014 12:46:44 PM$"

_DEBUG_=False #SET TO TRUE IF DEVELOPMENT VERSION, TO FALSE OTHERWISE!!!

import sys
_PY3 = True if sys.version_info.major == 3 else False

if _PY3:
    from io import StringIO
    def isstr(var):
        return isinstance(var, str)
else:
    from StringIO import StringIO
    def isstr(var):
        return isinstance(var, basestring)
    
import user_options as opts
import globalkeys as gk
import caravan.dbutils as dbutils
from caravan.core.gmpes.gmpe_utils import SOF as styleoffaulting #"AS" IS !ESSENTIAL!: IT AVOIDS CONFLICTS WITH PARAMS SOF (see get function)
import caravan.parser as parser
import caravan.core.gmpes.gmpes as gmpes

#TODOLIST:
#    Visualizzare prob. dist
#    controllare process delay before progressbar starts
#    controllare bug on ground motion only
#    css of table fdsn event query
#    check focus problems on help and language
#    think about re-organizing the code (html.py etcetera). Think and document how to write html {% TAG %} in data-label and data-doc
#    clean code, python, js, css and remove unused libraries
#    gmpe display in the run panel (string not showing, remove unicode u"")
#    mouse over sull'epicentro saying "epicenter"
#    think about how NOT to remove previously calculated cells
#    remove writing folder when calculating
#    check print statement and debug flags
#    add last log button
#    handle m=distrib and bounds check in gmpes
#    Handle pickable stuff AND implement in globals function for converting mcerp -> floats numpy etcetera
#    ground motion only should NOT return the fatalities. Does it? (I guessno...)

#tessellation ids:
tess_ids = opts.tess_ids #Other values (7,6,3,2,1)

#intensity refence (magnitude), to restrict the calculation area for intenisties higher than this value:
aoi_i_ref = opts.aoi_i_ref
#step radius for calculating Intensity higher than I-ref in core calculations
aoi_km_step = opts.aoi_km_step

#distributions npts (might be modified according to percentiles, see below):
mcerp_npts = opts.mcerp_npts #10000 is the default

#percentiles for calculation in core. 
percentiles = tuple(sorted(opts.percentiles))

#default calculate ground motion only
gm_only = opts.gm_only

try: import simplejson as json #see http://stackoverflow.com/questions/712791/what-are-the-differences-between-json-and-simplejson-python-modules
except ImportError: import json

def dumps(obj):
    """
    Alias as json.dumps: Serialize obj to a JSON formatted str using this conversion table:
    https://docs.python.org/3/library/json.html#py-to-json-table
    This includes quoting strings for instance
    """
    return json.dumps(obj)

def fdsncatalogs():
    from caravan.fdsnws_events import FDSN_CATALOG as cat
    return ''.join('<a href=# data-value="{0}">{0}</a>'.format(k) for k in cat)

def glbkeys():
    return {k:v for k,v in gk.__dict__.iteritems() if k[0]!='_'}

def glbkeyss():
    return dumps(glbkeys())

def imgpath():
    return 'imgs/'

#default connection class:
def connection(host=opts.DB_HOST, dbname=opts.DB_NAME, user=opts.DB_USER,  password=opts.DB_PSWD, async=opts.DB_ASYNC):
    return dbutils.Connection(host, dbname, user, password, async)

#gmpes:
#Note that the value will affect also the param ipe interval (see below)
#Ideally, we could just query the database, so that database changes need NOt to be synchronized also here
#The typical request would be (as of October 2014): 'select * from hazard.gmpes', which returns a table in which each column is a dict field here below
#However, this might mean to have a database-connection per url-connection, which makes for the moment much easier to implement the dict here below 

#NOTE2: November 2014 implementation is better suited to simply implement new gmpes 
#and just query gmpes.getgmpes(*modules) which would also leave the possibility to load gmpes from 
#new modules. However, the database owns indices for every gmpe, and as we should hard-code here 
#that index, we just hard-code everything, as before. The only difference is that we just pass the classes
def_gmpes ={
    1 : gmpes.GlobalWaRup,
    2 : gmpes.GlobalWaHyp,
    3 : gmpes.CentralAsiaEmca
}

sof={
    1: styleoffaulting.REVERSE,
    2: styleoffaulting.NORMAL,
    3: styleoffaulting.STRIKE_SLIP,
    4: styleoffaulting.UNKNOWN
}

#the names of additional modules to get gmpes from
additional_gmpes_modules = []

#tessellations ids. HArd coded better maybe to check the dbase?
tessellations = {
    1 : "urbanstructures_voronoi",
    2 : "bishkek_grid_1km",
    3 : "ca_cvtess_bishkek",
    4 : "bishkek_grid_2km",
    5 : "grid_kemin_5000",
    6 : "belovodsk_grid_2000",
    7 : "cvt_regional"
}
#scenario columns associated to the relative index (indices are used in Scenario to calculate the hash of a scenario query)
#We leave also the dbase value type commented, who knows if it is of help for some future release
#Same considerations as above: avoid db connections to retrieve the dict below, this dict isn't worth a database connection each time 
#(db command in any case, would be:
#SELECT column_name, ordinal_position, data_type
#FROM information_schema."columns"
#WHERE "table_name"='scenarios'
#)
scenario_db_cols = {
    "gid":1, #;"bigint"
    "hash":2, #;"bigint"
    "name":3, #;"character varying"
    "gmpe_id":4, #;"integer"
    "fault_style":5, #;"integer"
    "mag":6, #;"ARRAY"
    "epi_lat":7, #;"ARRAY"
    "epi_lon":8, #;"ARRAY"
    "ipo_depth":9, #;"ARRAY"
    "fault_strike":10, #;"ARRAY"
    "fault_dip":11, #;"ARRAY"
    "min_rupture_depth":12, #;"ARRAY"
    "type":13, #;"integer"
    "description":14, #;"text"
    "the_geom":15, #;"USER-DEFINED"
}

#parameters (input parameters for simulation query, event query etcetera)
#Last in the module because it makes use also of other module-level variables (gmnpes for instance)
#the infos stored in the following items will be used throughout the code
#
#Small GUIDE:
#
#decimals causes a parse to num:
#   decimals==-1: int (no float allowed)
#   decimals <-1: float (no nan allowed) 
#   decimals = None: smart guess, either int or float depending on value. If value already int or float, it is returned
#   decimals >=0 float rounded to decimals decimal digits (0 means returning floats with zero decimal digits, not ints)
#
#interval indicates the possible values range
#specifying interval without decimalss is in most cases meaningless. However, it works  
#for al param values which support ordering and equality, such as numbers but also strings). It can be:
#   a tuple denotes an open interval
#   a list a closed interval
#   a callback which accepts a value and returns True or False
#
#dim takes the same values as interval, but it is applied on the input value after parsing. E.g. "1 2, 3" is parsed into [1,2,3], and if 
#   dim is e.g., [1,2], an error is raised (dim([1,2,3])=3 not in [1,2]).
#   As for interval, a scalar value (e.g., dim=3) is equivalent to dim= [3,3]
#   Note: dim=0 means scalar only, 1 means either scalar or 1-length array. 
#   Examples:    dim     string      
#                0       "56" : OK, "2 3.4": NO, "[56]": NO (brackets denote the will to input an array)
#                1       "56" : OK, "2 3.4": NO, "[56]": OK 
#
#   If "distrib" is specified, usually dim is useless for checking the well formation when starting a simulation, 
#   as if the number of arguments does not match 
#   the mcerp dictribution, then an ecxeption is raised
#
#default is not used but might be used in future releases
#
#
#scenario_name is used for database communication: if present, the param value will be stored using the given name
#
#distrib is the distribution name built from the given parameters. Supported distributions are "Uniform" and "Normal" (case insensitive)
#

#FIXME: MOVE decimals as scenario type (e.g., scenario = ('name', decimals)) and implement a type 'n':number, 'f' float, 'b' boolean, 'i' integer, 
#'d' date 't' time
params ={
    gk.LAT : {
    'default': 42.87,
    'parse_func': parser.parsefloat,
    'parse_opts': {'interval':[-90,90], 'decimals': 3},
    'distrib':'normal',
    'scenario_name':'epi_lat', 
    'fdsn_name': 'latitude',
    },
    
    gk.LON : {
    'default': 74.6,
    'parse_func': parser.parsefloat,
    'parse_opts': {'interval':[-180,180], 'decimals': 3},
    'distrib':'normal',
    'scenario_name':'epi_lon', 
    'fdsn_name': 'longitude',
    },
    
    gk.DEP : {
    'default': 15,
    'parse_func': parser.parsefloat,
    'parse_opts': {'interval':[0.001,660], 'decimals': 3},
    'distrib':'uniform',
    'scenario_name':'ipo_depth', 
    'fdsn_name': 'depth',
    },
    
    gk.MAG : {
    'default': 6.8,
    'parse_func': parser.parsefloat,
    'parse_opts': {'interval':[0.1,12], 'decimals': 2},
    'distrib':'uniform',
    'scenario_name':'mag', 
    'fdsn_name': 'magnitude',
    },

    gk.IPE : {
    'default': 2,
    'parse_func': parser.parseint,
    'parse_opts': {'interval': [min(def_gmpes,key=int),max(def_gmpes,key=int)]},
    'scenario_name':'gmpe_id',
    'html': lambda: " ".join("<a data-value={0:d} data-sourcetype={1:d} data-doc=\"{2}\" >{2}</a>" \
      .format(idx, g.sourcetype if g.sourcetype or g.sourcetype==0 else "", g.__name__) for idx, g in def_gmpes.iteritems())
    },

    gk.TIM : {
    'default': '2014',
    'parse_func': parser.parsedate,
    'fdsn_name': 'time',
    #'dim': lambda d: [-1,3]
    },

    gk.STR: {
    'default': 0,
    'parse_func': parser.parsefloat,
    'parse_opts': {'interval':[0,360], 'decimals': 0},
    'distrib':'uniform',
    'scenario_name':'fault_strike',
    },

    gk.DIP: {
    'default': 0,
    'parse_func': parser.parsefloat,
    'parse_opts':{'interval':[0,360], 'decimals': 0},
    'distrib':'uniform',
    'scenario_name':'fault_dip',
    },

    gk.SOF: {
    'default': 0,
    'parse_func': parser.parseint,
    'parse_opts' : {'interval': [min(sof,key=int),max(sof,key=int)]},
    'scenario_name':'fault_style',
    'html': lambda: " ".join(["<a data-value={0:d} data-doc=\"{1}\">{2}</a>".format(i,gk.SOF, v) for i,v in sof.iteritems()])
    },

    gk.GMO: {
    'default':'', #Note: either empty or 'checked', ot is for an input of type checkbox. FIXME: better handling of the value? (should be boolean here)
    'parse_func': parser.parsebool,
    },

    gk.DNP: {
    'default': lambda: mcerp_npts, #cause mcerp_npts might have been modified in init()
    'parse_func': parser.parseint,
    },
    
    #default and interval set on init below
    gk.TES: {
    'default': tess_ids,
    'parse_func': parser.parseint,
    'parse_opts' : {'dim':[1, len(tessellations)], 'interval':[1, len(tessellations)]},
    'html': lambda: " ".join(["<a {0} data-value={1:d} data-doc=\"{2}\">{3}</a>".format("class=\"selected\"" if i in tess_ids else "",i, gk.TES, v) for i,v in tessellations.iteritems()])
    },

    gk.AOI: {
    'default': None,
    'parse_func': parser.parsefloat,
    'parse_opts' : {'dim': 4},
    },

    gk.AIR: {
    'default': lambda: aoi_i_ref,
    'parse_func': parser.parsefloat,
    'parse_opts' : {'dim': -1},
    },

    gk.AKS: {
    'default': lambda: aoi_km_step,
    'parse_func': parser.parseint,
    'parse_opts' : {'dim': -1},
    },
}

def get(string):
    """
        Gets the param value according to string, which can be:
        The string denoting a global key defined in globalkeys (e.g., 'LAT') in that case it returns the string value of the param (e.g., 'lat')
        The comma-separated field of the param identified by string (e.g., 'LAT.default'), in that case it returns 
        the corresponding key value defined here in params (e.g., 78)
    """
    if(string in globals()):
        ret = globals()[string]
    else:
        pv = string.split('.')
        l = len(pv)
        if l!=1 and l!=2: return None
        g = globals()
        if not pv[0] in gk.__dict__: return None
        par = gk.__dict__[pv[0]]
        if l==1: return par
        par = g['params'][par]
        if not pv[1] in par: return None
        ret = par[pv[1]]
    if hasattr(ret, "__call__"): ret = ret() #is callable? then call it
    return ret
#class definition used in cast below, when the argument is not string it MUST be 
#a _Param type
class _Param(dict):
    pass

def cast(param, value, **options):
    """
        Global function which casts value according to param, which must be either  
        a key defined in globalkeys (e.g., globalkeys.LAT) for which there is a mapping in the module level params dict, or a parameter 
        itself (e.g., globals.params[globalkeys.P_LAT])
        If the given param has no key 'parse_func', then value is returned.
        Otherwise, 'parse_func' is the function F used to cast, and it will be called 
        in order to return the 'casted' value of the value argument.
        Additional arguments of F are specified in the param 'parse_opts' key. If some of those 
        keys needs to be overridden (or added to the default), provide a custom set of options in the dict-like 
        argument list **options, 
        Examples: 
            cast('lat', "33.4493") #returns '33.449', assuming params['lat']['parse_opts']['decimals']=3
            cast('lat', "33.4493", decimals=2) #returns '33.45', regardless of whether params['lat']['parse_opts']['decimals'] is set or not
            
    """
    p = param if isinstance(param,_Param) else params[param]
    
    if not 'parse_func' in p: return value
    
    func = p['parse_func']
    
    optz = dict(p['parse_opts']) if 'parse_opts' in p else {}
    optz.update(options)
    
    return func(value, **optz)

def discretepdf(dist, ticks):
    """
        Returns the (discrete) probability density functions of dist (either 
        distribution, or scalar) at the given bins represented by the ticks 
        argument (list or tuple or iterable)
        More precisely, returns a generator yielding at each iteration the 
        probability of ticks[i]:
        
        dist < ticks[0]
        ...
        (dist < ticks[i]) - (dist < ticks[i-1])
        ...
        dist >= ticks[len(ticks)-1]
        
        Therefore, this method yields N+1 values, where N = len(ticks)
        
        By definition, the sum of all yielded values is 1. Note that dist does not need 
        to be a distribution (mcerp.UncertainFunction):
        scalar values (python numeric values) are also valid and will result in a 
        generator yielding 1 for the bin where the dist argument falls, 
        and 0 for all remaining N values
    """
    prev = 0;
    t=0
    for t in ticks:
        tmp = dist < t
        yield tmp-prev #this converts boolean to numbers in case
        prev=tmp
    yield (dist >= t)-0 #this converts boolean to numeric in case dist is scalar
    
def isnumpyscalar(val):
    return hasattr(val,"item")

def isdist(val):
    return isinstance(val, mcerp.UncertainFunction)
#:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.
#:.:.:.:. DO NOT MODIFY THE CODE BELOW :.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.
#:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.

def init():
    #remember that ACCESSING global variables is ok,
    #MODIFYING global variables needs the declaration "global varname"
    
    for k in params:
        params[k] = _Param(**params[k])
        
    #Also re-set mcerp_npts to be the minimum required for percentiles:
    #the number of  points N must satisfy N >= 2*min, where min is the minimum
    #between min(percentiles) and 1-max(percentiles), assuming all percentiles in ]0,1[
    minpts = max(1.0/percentiles[0], 1.0/(1.0-percentiles[len(percentiles)-1]))
    int_minpts = int(minpts)
    minpts = 2*(int_minpts+1) if int_minpts != minpts else 2*int_minpts
    
    global mcerp_npts
    if mcerp_npts < minpts:    
        mcerp_npts = minpts
    
    
init() #execute the code above

#TODO LIST. NOTE: WILL BE REMOVED!
#TO DO:
#CHECK deletion of previous sessions, scenarios etcetera. It's a mess...
#check why I got failed/done mismatch (maybe add a log on the failed sub-processes?)
#change percentiles in dbase gmpe, both in write and read
#use wsgi
