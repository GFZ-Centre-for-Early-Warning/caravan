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
from __future__ import print_function

__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="$Jun 23, 2014 1:15:27 PM$"

import json
import traceback
from cgi import parse_qs, escape #for parsing get method in main page (address bar)

import time
import caravan.settings.globals as glb
CARAVAN_DEBUG = glb._DEBUG_; #debug variable, as of Juli 2014 it controls whether exceptions in ResponseHandler should throw the traceback or simply an error message


import os
import miniwsgi
import sys

#todo: check parser dim
#todo: impolement html module to be clear where to write in the html page?
#todo: implement globals.params type for casting?

from caravan.core.core import caravan_run as run
from caravan.core.runutils import RunInfo
import mcerp
import caravan.settings.globalkeys as gk
import caravan.fdsnws_events as fe
import json, re
CaravanApp = miniwsgi.App()

#@CaravanApp.route(url='caravan/static/index.html', headers={'Content-Type':'text/html; charset=UTF-8'}) #url='caravan/static/index.html', 
#re.compile(r"\.(?:jpg|jpeg|bmp|gif|png|tif|tiff|js|css|xml)$", re.IGNORECASE)
@CaravanApp.route(url='index.html', headers={'Content-Type':'text/html; charset=UTF-8'}) #url='caravan/static/index.html', 
def caravan_mainpage(request, response):
    return request.urlbody
    
    
@CaravanApp.route(url='fdsn_query.html', headers={'Content-Type':'text/html; charset=UTF-8'}) #url='caravan/static/index.html', 
def fdsn_query(request, response):
    
    #when this is not a post request, print anyway the table. Therefore:
    try:
        query_url = ""
        try:
            form = request.post
            s = []
            catalog = ''
            for key in form.keys(): 
                l = form.getlist(key)
                if key == 'catalog':
                    catalog=l[0]
                else:
                    par = glb.params[key]
                    fdsn_name = par['fdsn_name']
                    istime = key == gk.TIM
                    
                    if istime:
                        vmin = glb.cast(par,l[0])
                        vmax = glb.cast(par,l[1], round_ceil=True)
                        
                        #fdsn format: 2014-12-07T01:22:03.2Z. Let's conver it
                        vmin = "start{0}={1:04d}-{2:02d}-{3:02d}T{4:02d}:{5:02d}:{6:02d}.{7:d}Z".format(fdsn_name,vmin.year, vmin.month, vmin.day, vmin.hour, vmin.minute, vmin.second,vmin.microsecond)
                        vmax = "end{0}={1:04d}-{2:02d}-{3:02d}T{4:02d}:{5:02d}:{6:02d}.{7:d}Z".format(fdsn_name,vmax.year, vmax.month, vmax.day, vmax.hour, vmax.minute, vmax.second,vmax.microsecond)
                    else:
                        vmin = "min{0}={1}".format(fdsn_name, str(glb.cast(par,l[0],dim=-1))) #-1: needs scalar
                        vmax = "max{0}={1}".format(fdsn_name, glb.cast(par,l[1],dim=-1)) #-1: needs scalar
                    
                    s.append('{0}&{1}'.format(vmin, vmax))
            query_url = fe.FDSN_CATALOG[catalog]+ ('&'.join(s))         
        except:pass   
        
        #define here the ORDER of the columns!
        cols = ("EventLocationName","Time","Latitude","Longitude", "Depth", "Magnitude") #, "EventId")
        submittable_keys = {"Latitude": gk.LAT,"Longitude": gk.LON, "Depth": gk.DEP, "Magnitude": gk.MAG} #numeric are also submittable
    
        value = ""
    
        def esc(s, quote=True): return miniwsgi.escape(s, quote)
        
        def parse_depth(val):
            try:
                if val[0] is not None : val[0] /= 1000
                #if val[1] is not None : val[1] /= 1000 #depth uncertainty SEEMS in km!!!
            except:
                pass
            
        value = [] if not query_url else fe.get_events(query_url, _required_=fe.DEF_NUMERIC_FIELDS, _callback_={fe.F_DEPTH: parse_depth}) #getCaravanEvents(xmlurl)
        
        vals = StringIO()
        vals.write(request.urlbody)        
        vals.write("<table class='fdsn'><thead class='title'><tr>\n")
        vals.write(''.join("<td data-sort='{0}'>{1}</td>".format('num' if v in submittable_keys else 'str', esc(v)) for v in cols))
        vals.write('\n</tr>\n</thead>')
        vals.write("<tbody>")

        for v in value:
            vals.write('<tr>')
            unc = {} if not 'Uncertainty' in v else v['Uncertainty']
            for k in cols:
                tdval = v[k]
                tdstr = str(tdval) if k!="Time" else str(tdval).replace("T"," ").replace("Z","")
                tdsubmit_value = tdstr
                tdsubmit_key = None
                if k in submittable_keys:
                    tdsubmit_key = submittable_keys[k]
                    if k in unc:
                        tdstr+=" &plusmn; " + str(unc[k])
                        pr = glb.params[tdsubmit_key]
                        if 'distrib' in pr:
                            dstr = pr['distrib'].lower()
                            tdsubmit_value = str(tdval) + " " + str(unc[k]/2) if dstr == 'normal' else str(tdval - unc[k]) + " " + str(tdval + unc[k])
                
                vals.write('<td')
                vals.write(' data-value="{}"'.format(esc(tdstr)))
                if tdsubmit_key: vals.write(' data-submit-key="{}" data-submit-value="{}"'.format(esc(tdsubmit_key), esc(tdsubmit_value)))
                vals.write('>{}</td>'.format(tdstr))
            vals.write('</tr>')
        vals.write("</tbody></table>") 
        value = vals.getvalue()
        vals.close()
        
    except Exception as e:
        value = "<span class=error>"+esc(str(e))+"</span>"
        if CARAVAN_DEBUG:
            traceback.print_exc()
    
    s = StringIO()
    s.write(value)
    s.write("\n</body>\n</html>")
    v = s.getvalue()
    s.close()
#         if p == 'catalog':
#             s= cat[p].value + s
#         else
    return v        

#self._default_headers['Content-type']= 'application/json'
#FIXME: CHECK INLINE IMPORT PERFORMANCES!!!

RUNS ={} #stores the runs


@CaravanApp.route(headers={'Content-Type':'application/json'})
def run_simulation(request, response):
    
    jsonData = request.json
    #parse advanced settings:
    
    
    #DO IT HERE, NOW PRIOR TO ANY CALCULATION!!!!
    #FIXME: HANDLE EXCEPTIONS!!!!!
    key_mcerpt_npts = gk.DNP
    mcerp.npts = glb.mcerp_npts if not key_mcerpt_npts in jsonData else glb.cast(key_mcerpt_npts, jsonData[key_mcerpt_npts])
    
    
    runinfo = RunInfo(jsonData)
    
    ret= {}
    if runinfo.status()==1: #running, ok
        runinfo.msg("Process starting at {0} (server time)".format(time.strftime("%c")))
        
        run(runinfo)
        RUNS[runinfo.session_id()] = runinfo #should we add a Lock ? theoretically unnecessary...
        ret = {'session_id':runinfo.session_id(), 'scenario_id':0}
    else:
        ret = {'error': runinfo.errormsg or "Unknown error (please contact the administrator)"}
    
    return response.tojson(ret)

@CaravanApp.route(headers={'Content-Type':'application/json'})
def query_simulation_progress(request, response):
    event = request.json
#     try:
    ret= {}
    if event['session_id'] in RUNS:
        runinfo = RUNS[event['session_id']]

        if event['stop_request']:
            runinfo.stop()

        status = runinfo.status()
        
        done = 100.0 if status > 1 else runinfo.progress()
        ret = {'complete': done}
        msgs = runinfo.msg()
        
        if msgs is not None and len(msgs):
            ret['msg'] = msgs

        #NOTE THAT THE STATUS MIGHT CHANGE IN PROGRESS< AS IT MIGHT SET AN ERROR MSG
        #INSTEAD OF RE_QUERYING THE STATUS, WE QUERY THE ERROR
        if runinfo.errormsg: #status == 3:
            ret['error'] = runinfo.errormsg

    else:
        ret = {"error":"query progress error: session id {0} not found".format(str(event['session_id']))}
#     except:
#         import traceback
#         from StringIO import StringIO
#         s = StringIO()
#         traceback.print_exc(s)
#         s.close()
#         ret = {"error":s.getvalue()}
        
    return response.tojson(ret)


@CaravanApp.route(headers={'Content-Type':'application/json'})
def query_simulation_data(request, response):
    event = request.json
    session_id = event['session_id']
    #print("session id"+str(session_id))
    conn = glb.connection(async=True)
    #query:
    #note: ::json casts as json, not as jason-formatted string
    #::double precision is NECESSARY as it returns a json convertible value, otherwise array alone returns python decimals
    #which need to be converted to double prior to json dumps

    data = conn.fetchall("""SELECT 
ST_AsGeoJSON(ST_Transform(G.the_geom,4326))::json AS geometry, GM.geocell_id, GM.ground_motion, risk.social_conseq.fatalities_prob_dist, risk.econ_conseq.total_loss
FROM 
processing.ground_motion as GM
LEFT JOIN 
risk.social_conseq ON (risk.social_conseq.geocell_id = GM.geocell_id and risk.social_conseq.session_id = GM.session_id)
LEFT JOIN 
risk.econ_conseq ON (risk.econ_conseq.geocell_id = GM.geocell_id and risk.econ_conseq.session_id = GM.session_id)
LEFT JOIN 
exposure.geocells as G ON (G.gid = GM.geocell_id)
WHERE 
GM.session_id=%s""",(session_id,)) 

    #conn.conn.commit()
    conn.close()
    
    #HYPOTHESES:
    #1) The query above returns a table T whose header (columns) are:
    #    | geometry | geocell_id | ground_motion | fatalities_prob_dist | total_loss
    #
    #2) a single T row (R) corresponds to a geojson feature F:
    #{
    #    type: 'Feture', //geojson standard string (see doc)
    #    geometry : dict, //associated to geometry column
    #    id: number_or_string, //associated to geocell_id column
    #    properties:{
    #       gk.MSI: {data: usually_array, value:numeric_scalar}, //associated to ground_motion column
    #       gk.FAT: {data: usually_array, value:numeric_scalar}, //associated to fatalities_prob_dist column
    #       gk.ECL: {data: usually_array, value:numeric_scalar}  //associated to total_loss column
    #    }
    #}   
    # gk.MSI, gk.FAT and gk.MSI.ECL refer to globalkeys global variables. They are just strings 
    # but defined globally for multi-purpose usage
    # 3) EACH PROPERTIES FIELD HAS TWO VALUES, DATA AND VALUE. WHICH WILL BE CALCULATED FROM ANY DATABASE ROW IN 
    # THE FUNTION process DEFINED BELOW. DATA IS MEANT TO BE AN ARRAY OF DATA TO BE VISUALIZED WHEN MOUSE IS
    # OVER THE RELATIVE GEOCELL ON THE MAP, WHEREAS VALUE IS THE VALUE TO BE VISUALIZED BY MEANS OF E.G. A COLOR
    # FOR A PARTICULAR GEOCELL. Example: given a set of data bins representing the distribution at some values, e.g. [0.2, 0.5, 0.3],
    # then properties.data is that array, and value might be e.g., the median, or the max, or the index of max, or whatever
    # (the important thing is that JavaScript side one knows what are data and value in order to display them on the map)
    
    #NOW we define the columns to be set as properties (excluding geometry):
    #Each column here corresponds to a leaflet Layer in JavaScript
    #associating each of them to a table column index (see 1) in comment above):
    captions = {gk.MSI:2, gk.FAT:3, gk.ECL: 4} 
    
    #THIS IS THE MAIN FUNCTION
    def process(name, row, row_index):
        try:
            data = row[row_index]
            if name == gk.MSI: #return the median
                #pop last element, which is the median according to core.py
                m = data.pop() #removes and returns the last index
                return data, m
            elif name == gk.FAT: #return INDEX OF max value
                remVal = 1
                max = 0
                ind_of_max = 0
                i = 0
                for n in data:
                    if n > max: 
                        max = n
                        ind_of_max = i
                    remVal -= n
                    if remVal < max: break #< not <=: priority to higher value, if two or more are equal
                    i += 1

                return data, ind_of_max
            elif name == gk.ECL: #economic losses, to be implemented
                pass
        except: pass #exception: return None, None below
        #elif ... here implement new values for newly added names
        return None, None
    
    dataret = {"type": "FeatureCollection", "features": None, "captions": {k:"" for k in captions}}
    features = [] #pre-allocation doesn't seem to matter. See e.g. http://stackoverflow.com/questions/311775/python-create-a-list-with-initial-capacity
    
    #set set of empty layers. As soon as we have a valid data 
    #for a geocell g and a layer name N in the loop below, remove N from the 
    #set defined below. This might be used JavaScript side to know immediately if a layer is empty
    #or not, avoiding consuming memory 
    empty_layers = {k for k in captions} #do a cpoy
    
    for row in data:
        cell = {'geometry': row[0], 'id':row[1], 'type':'Feature', 'properties':{}}
        for name in captions:
            index = captions[name]
            data, value = process(name, row, index)
            #remove the empty layers key if data is valid:
            if name in empty_layers and not (data is None and value is None): empty_layers.remove(name)
            property = {'data': data, 'value': value}
            cell['properties'][name] = property

        features.append(cell)
    dataret['features'] = features
    dataret['emptyLayers'] = {k:True for k in empty_layers}

    return response.tojson(dataret)

#.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:
# FROM HERE ON FUNCTIONS FOR CREATING THE MAIN HTML PAGE AND THE DICTIONARY.JS JAVASCRIPT FILE
# ALL THIS CODE WILL BE EXECUTED ONLY IF the global debug variable is False, which is always True unless
# you dind't run this file from within manage.py
# THE MAIN PAGE AND THE DICTIONARY JS FILE ARE CREATED IF THERE IS THE NEED TO DO THEM, I.E. SOME FILES 
# HAVE BEEN MODIFIED OR ADDED
#.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:

def _mtime(file, files):
    "returns the modification time of file according to files. None means file needs not to be updated acccording to files"
    r = 3; #round number for modification time (see belo)
    t = (round(os.path.getmtime(filename),r) if os.path.exists(filename) else None for filename in files)
    tmax = None
    for tt in t:
        if tt is None: continue
        if tmax is None or tt>tmax: tmax = tt 
        #we need to round mtimes cause apparently thy are difference even if they "aren't"
    if tmax is None: #equal to tmax so that if we modified fileout itself, it rebuilds it
        return None
    
    if not os.path.exists(file): return tmax
    
    t0 = round(os.path.getmtime(file),r)
    return None if t0==tmax else tmax


def needs_update(file, files):
    return _mtime(file, files) is not None

def set_mtime(file, files):
    mt = _mtime(file, files);
    if mt is None: return
    os.utime(file, (os.path.getatime(file), mt))
    
from StringIO import StringIO #needs update to Python3!!!!
def create_main_page(): #FIXME: check compatibility with io in python3
    
    source = "caravan/static/index_template.html"
    dest = "caravan/static/index.html"
    
    check_sources = [source, "caravan/settings/globals.py", "caravan/settings/user_options.py"]
    if not needs_update(dest, check_sources): return
    
    if CARAVAN_DEBUG: print("Updating {}".format(dest))
    f = open(source,'r')
    k = f.read()
    s = StringIO()
    f.close()
    import re
    
    r = re.compile("\{\%\\s*(.*?)\\s*\%\}",re.DOTALL)
    
    lastidx = 0
    for m in r.finditer(k,lastidx):
        if m.start() > lastidx:
            s.write(k[lastidx: m.start()])
        
        ztr = m.group()
        if m is not None and len(m.groups())==1:
            val = glb.get(m.group(1))
            ztr = "" if val is None else str(val)
        
        s.write(ztr)
        lastidx = m.end()
    
    l = len(k)
    if lastidx < l:
        s.write(k[lastidx: l])
        
    f = open(dest,'w')
    k = f.write(s.getvalue())
    s.close()
    f.close()
    
    set_mtime(dest, check_sources)

import imp
from importlib import import_module
from types import ModuleType
# import lang.default as lang_default
def create_dict_js(): #FIXME: check compatibility with io in python3
    DEFAULT_LANG = "en" #move from here?
    dict_dir = "caravan/settings/lang"
    files = [ os.path.join(dict_dir,f) for f in os.listdir(dict_dir) if os.path.splitext(f)[1].lower() == '.py' ] #os.path.isfile(os.path.join(dict_dir,f)) ]
    
    dest = "caravan/static/libs/js/lang_dict.js"
    
    #print(str(files)+ " "+str(needs_update(dest, files)))
    source = "caravan/static/libs/js/lang_dict_template.js"
    
    check_sources = list(files)
    check_sources.append(source)
    if not needs_update(dest, check_sources): return
    
    if CARAVAN_DEBUG: print("Updating {}".format(dest))
    
    fout = StringIO()
    fout.write('{\n');
    first = True
    
#     gks = set()
#     for d in dir(gk):
#         if len(d)>1 and d[:1] == "_": continue #len(d)<4 or not (d[:2] == "__" and d[-2:] == "__"):
#         gks.add(gk.__dict__[d])
    
#     print(str(gks))

    _quote_ = glb.dumps
    
    gmpez = {g.__name__ : g for g in glb.def_gmpes.values()}
    
    for f in files:
        mod_name,file_ext = os.path.splitext(os.path.split(f)[-1])

        if mod_name.lower() == "__init__" or file_ext.lower() != '.py' or not os.path.isfile(f): continue #for safety (should not be the case
        
        
        full_name = os.path.splitext(f)[0].replace(os.path.sep, '.')
#         print("{0} full path: {1}".format(mod_name, full_name))
        
        py_mod = import_module(full_name)
        
#         print("modname: "+py_mod.__name__)
        
        py_mod_dir = dir(py_mod)
#         print("dir: "+str(py_mod_dir))

        if first: first=False
        else: fout.write(",\n")
        
        fout.write(mod_name)
        fout.write(" : {")
        
        ffirst = True
        
        for k in py_mod_dir: # gks:
            if len(k)>1 and k[:1] == "_": continue
            
            val = py_mod.__dict__[k]
            if isinstance(val, ModuleType): continue
            
            if ffirst: ffirst = False
            else: fout.write(",\n")
            
            
            #handle gmpes (ipes):
            if k in gmpez and "_ipe_dist_bounds_text" in py_mod.__dict__ and "_ipe_mag_bounds_text" in py_mod.__dict__:
                ge = gmpez[k]
                val = val+"<br>"+py_mod.__dict__["_ipe_mag_bounds_text"] + str(list(ge.m_bounds))+"<br>"+py_mod.__dict__["_ipe_dist_bounds_text"] + str(list(ge.d_bounds))+("<br><i>"+ge.ref+"</i>" if ge.ref else "")
            
            var  = _quote_(val)
            
            #"[{}]".format(','.join(_quote_(str(v)) for v in val)) if hasattr(val, "__iter__") else '""' if val is None else _quote_(str(val))

            
            fout.write(k)
            fout.write(" : ")
            fout.write(var)
        
        fout.write("}\n")
        
    fout.write("};")
    
    sourcen = open(source, 'r')
    sn = sourcen.read()
    sourcen.close()
    sn = sn.replace("{% DICT %}",fout.getvalue())
    sn = sn.replace("{% DEFAULT_LANG %}", DEFAULT_LANG)
    fout.close()
    
    fout = open(dest,'w')
    fout.write(sn)
    fout.close()
    set_mtime(dest, check_sources)


#execute files:
#but only if in debug mode
if CARAVAN_DEBUG:
    #first change the current dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_main_page()
    create_dict_js()
    print(str(CaravanApp))  
