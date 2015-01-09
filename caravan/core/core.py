#! /usr/bin/python

"""
Core process definition of the caravan app
     
(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

from __future__ import print_function


__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Aug 21, 2014 2:41:56 PM$"

import multiprocessing
# IS THIS NOTE STILL USEFUL? -> We must import this explicitly, it is not imported by the top-level
# multiprocessing module.
# See http://stackoverflow.com/questions/6974695/python-process-pool-non-daemonic
from datetime import datetime
import mcerp
import gmpes
import caravan.core.gmpes.gmpe_utils as gmpe_utils
from runutils import RunInfo
import caravan.settings.globalkeys as gk


#README!!!! TO INSTALL PSGYCOMP2 FIRST:
#sudo apt-get install libpq-dev python-dev
#sudo pip install psycopg2
#SEE NOTES ON: 
#http://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python
#AND
#http://initd.org/psycopg/install/

import caravan.settings.globals as globals
import risk_calc

_DEBUG_= 1
#mcerp.npts = globals.mcerp_npts
import os
import random
# import threading
# gmpe_lock = threading.Lock()

_intensity_labels = (4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5)

#def geocell_run(gmpe_func, lat_sta, lon_sta, percentiles, target_id, geocell_id, ground_motion_only, scenario_id, session_id, logdir = None ):
def geocell_run(intensity, lat_sta, lon_sta, percentiles, target_id, geocell_id, ground_motion_only, scenario_id, session_id, logdir = None ):
    """
        Performs a ground motion calculation given the above arguments. Writes to database the percentiles
    """
    
    def val(value):
        #value should be either a scalar number or a numpy.ndarray element. Check below is WEAK, because it checks only if 
        #len(value) can be called, but it avoids importing numpy etcetera
        return mcerp.UncertainFunction(value) if hasattr(value, '__len__') else float(value)
    
    try:
        
       
        #intensity = gmpe_func(val(M), val(lat_hyp), val(lon_hyp), val(depth_hyp), lat_sta, lon_sta)
        #intensity = gmpe_func(lat_sta, lon_sta)
        
        #INTENSITY IS EITHER A SCALAR OR A UNCERTAINFUNCTION.MCERP ARRAY (NUMPTY ARRAY)
        intensity = val(intensity)
        
#        _p = intensity.percentile(percentiles) if isinstance(intensity, mcerp.UncertainFunction) else len(percentiles)*[intensity]
        _dist = [v for v in globals.discretepdf(intensity,_intensity_labels)]
        _dist.append(intensity.percentile(0.5) if isinstance(intensity, mcerp.UncertainFunction) else intensity)
        #write to dbase
           
        
        arg1 =  """INSERT INTO processing.ground_motion (target_id, geocell_id, scenario_id, session_id, ground_motion) VALUES (%s, %s, %s, %s, %s);""" 
        arg2 = (target_id, geocell_id, scenario_id, session_id, _dist) 
        
#        arg1 =  """INSERT INTO processing.ground_motion (target_id, geocell_id, scenario_id, session_id, percentiles, ground_motion) VALUES (%s, %s, %s, %s, %s, %s);""" 
#        arg2 = (target_id, geocell_id, scenario_id, session_id, _p, _dist) 
        
        conn = globals.connection()
        conn.execute(arg1, arg2)
        conn.close()
        
        #do risk calculation (risk is Michael source, modified by me)
        if not ground_motion_only:
            risk_calc.calculaterisk(intensity, percentiles, session_id, scenario_id, target_id, geocell_id)

    except Exception as run_exc:
    
        if _DEBUG_:
            import traceback
            traceback.print_exc()
        
        #connect to the database and write the failed number:
        conn = globals.connection()
        conn.execute("UPDATE processing.sessions SET num_targets_failed = num_targets_failed + 1 where gid=%s",(session_id,))
        conn.close()
        
        #         log dir must be passed as argument problems when declaring global var (maybe multiprocess?)
        if _DEBUG_:
            if logdir is not None:
                try:
                    folder = logdir
                    if os.path.exists(folder):
                        name = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10)) if geocell_id is None else str(geocell_id)
                        file = os.path.join(folder, name+".log")
                        output = open(file,'w')
                        traceback.print_exc(file=output)
                        output.close()
                except:
                    traceback.print_exc()
        #raise run_exc
        

def caravan_run(input_event):
    """
        Performs a gorund motion calculation of the Caravan application
    """
    
    conn = None
    exception = None
    
    try:
        #Note: we pass a runinfo object actually, does this is necessary? how to handle if runinfo is already stopped? 
        #should not be the case, however... 
        runinfo = input_event.start() if isinstance(input_event, RunInfo) else RunInfo(input_event) #.start() harmless if already started
        
        scenario = runinfo.scenario() 
        
        #NOTE: MCERP NPTS (params.DNP) CANNOT BE SET HERE CAUSE IT NEEDS TO BE SET PRIOR TO ANY CALCULATION, 
        #EVEN THE SCENARIO CREATION (WHICH). MOVED TO CARAVAN_WSGI RUN_SIMULATION
        
        gmpe_func = scenario.gmpe 
        
        #Connect from within the process:
        conn = globals.connection(async=False)
        
        scenario_id , isnew = scenario.writetodb(conn)
        
        if not isnew:
            #arg1 = """DELETE FROM processing.ground_motion WHERE scenario_id=%d """ % scenario_id
            arg1 = """DELETE FROM processing.ground_motion WHERE scenario_id=%s"""
            
            #From see http://www.postgresql.org/docs/9.1/static/sql-delete.html:
            #we could write "DELETE FROM processing.ground_motion WHERE scenario_id=%d RETURNING COUNT(*)""" % scenario_id
            #and then: conn.execute(arg1)
            #but that gives me (first command, postgres error): "aggregate functions are not allowed in RETURNING"
            #googling there are solutions (BUT starting from postgres9.1):
            #http://stackoverflow.com/questions/6577823/how-can-i-insert-the-return-of-delete-into-insert-in-postgresql
            #Therefore, skip that solution
            
            #ANOTHER NICER EXAMPLE found here: http://stackoverflow.com/questions/2251567/how-to-get-the-number-of-deleted-rows-in-postgresql
            #AS LONG AS THE CONNECTION IS NOT IN ASYNC MODE (we can switch it to sync here. It must be async inside each apply_async call below only)
            #USES psycopg2 cursor class and is preferable. Therefore:
            cursor = conn.cursor(arg1, (scenario_id,))
            conn.commit() #NOTE: in async mode does nothing
            rows_deleted = cursor.rowcount
            cursor.close()
            #this works because (psycopg2 cursor doc) a QUERY was executed in execute(). Now, delete seems not a query to me,
            #however it seems to work
            
            runinfo.msg("Using already stored Scenario (hash={0:d}), deleted {1:d} previously calculated cells" .format(scenario.dbhash(),rows_deleted))
        else:
            runinfo.msg("Written new scenario to databse (hash={0:d}):<br>Scenario = {1}".format(scenario.dbhash(),scenario.dbstr()))
                
        runinfo.msg("Scenario id: {:d}".format(scenario_id))    
        
        #define function to get value from scenario
        def scalar(key):
            val = scenario[key]
            
            if isinstance(val, mcerp.UncertainFunction):
                return val.mean #NOTE: not mean() !! it is a @property!!
            else:
                return float(val) #parse to float to be sure
        
        #CALCULATE RADIUS OF INTEREST
        key_a_ref = gk.AOI
        a_ref = scenario[key_a_ref] if key_a_ref in scenario else None
        
        ref_d = None
        
        #GET TESSELLATIONS:
        key_tess_ids = gk.TES
        tess_ids = globals.tess_ids if not key_tess_ids in scenario else scenario[key_tess_ids]
        
        tess_id_str = " or ".join([("t.tess_id={:d}".format(t)) for t in tess_ids])
        runinfo.msg("Tessellation id(s): {}".format(', '.join(["{:d}".format(tid) for tid in tess_ids])))
        
        if a_ref is not None: 
            lon1, lat1, lon2, lat2 = a_ref
            targets = conn.fetchall("""select t.gid as target_id, t.geocell_id as geocell_id, st_X(t.the_geom) as lon, 
        st_Y(t.the_geom) as lat from exposure.targets as t where ("""+tess_id_str+""") 
        and st_within(t.the_geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326));""", (lon1, lat1, lon2, lat2))

            runinfo.msg("Area: map rectangle ("+key_a_ref+" parameter [lon1, lat1, lon2, lat2], see above)") #str should place dot or not automatically

        else:
            key_i_ref = gk.AIR
            key_i_ref_km_step = gk.AKS
            
            I_ref = scenario[key_i_ref] if key_i_ref in scenario else globals.aoi_i_ref
            ref_dist_km_step = scenario[key_i_ref_km_step] if key_i_ref_km_step in scenario else globals.aoi_km_step #ref_dist_km_step

            ref_d = ref_dist(gmpe_func, I_ref, ref_dist_km_step)
            runinfo.msg("Area(I &ge; {:.2f}) radius: {:.1f} Km" .format(I_ref, ref_d)) #str should place dot or not automatically

            if ref_d < ref_dist_km_step:
                msg = "Epicentral intensity smaller than intensity reference = {:.2f} mw".format(I_ref)
                if _DEBUG_:
                    print(msg)
                raise Exception(msg)
            
            #GET TESSELLATION POINTS (GEOCELLS):
            key_lat = gk.LAT #"latitude"
            key_lon = gk.LON #"longitude"


            targets = conn.fetchall("""select t.gid as target_id, t.geocell_id as geocell_id, st_X(t.the_geom) as lon, 
            st_Y(t.the_geom) as lat from exposure.targets as t where ("""+tess_id_str+""") 
            and st_dwithin(geography(st_point(%s, %s)), geography(t.the_geom), %s);""" , (scalar(key_lon), scalar(key_lat), ref_d * 1000))
        #conn.commit()
        
        subprocesses = len(targets)
        num_malformed = 0
        
        if subprocesses:
            #targets is a table of columns:
            #target_id, geocell_id, lat, lon
            #with length the number of geocells
            #Note that geocell_id might be missing
            #Do a check Now? YES!
            def formwell(t):
                try: 
                    #t is a tuple, we cannot assign to it.
                    #Simply do a check and preserve old values
                    #Note that the check below is fine also if elements are numeric strings
                    #the drawback of instantiating a new list is however too much effort
                    #as data should be numeric
                    _,_,_,_ = int(t[0]), int(t[1]), float(t[2]), float(t[3])
                except: 
#                    import traceback
#                    traceback.print_exc()
                    return None
                return t
                
            for i in range(subprocesses):
                t = targets[i]
                twf = formwell(t)
                if twf is None: 
                    num_malformed+=1
                    targets[i] = twf
                


        else:
            msg = "No target cells found (zero cells)"
            raise Exception(msg)        
        
        if num_malformed >= subprocesses:
            msg = "All target cells are malformed (missing or non-numeric values)"
            raise Exception(msg) 
        elif num_malformed > 0:
            runinfo.warning("{:d} of {:d} target cells found (skipping {:d} malfromed cells, containing missing or NaN values)".\
                        format(subprocesses - num_malformed, subprocesses, num_malformed))
        else:
            runinfo.msg("{:d} target cells found".format(subprocesses))
            
        
        #WRITE session_id in processing.sessions
        
        #see https://docs.python.org/2/library/datetime.html#datetime.datetime.now (we use utcnow instead of now)
        #and http://initd.org/psycopg/docs/usage.html#adaptation-of-python-values-to-sql-types
        session_id = None
        while True:
            session_timestamp = datetime.utcnow() #returns a datetime object, which is converted to timestamp in psycopg2
            session_rows = conn.fetchall("SELECT COUNT(*) FROM processing.sessions WHERE session_timestamp=%s;", (session_timestamp,))
            if session_rows[0][0] == 0:
                #NOTE: do NOT run immediately num_malformed, otherwise the progressbar and time counter have invalid data
                #just set subprocesses-num_malformed as the cells to be done: 
                cursor = conn.cursor("INSERT INTO processing.sessions (scenario_id, session_timestamp, num_targets, num_targets_failed) \
                VALUES(%s, %s, %s, %s) RETURNING gid;", (scenario_id, session_timestamp, subprocesses-num_malformed, 0,))
                
                #Note returns works because of RETURNING string in dbase execute command. execute() can return elements without return 
                #explicitly written as long as (psycopg2 cursor doc) a QUERY was executed in execute(). Now, insert is not a query, 
                #but for instance (see few lines above) DELETE it is
                conn.commit() #note: in async mode does nothing
                ret = cursor.fetchall()
                
                session_id = ret[0][0] #gid (serial number) of the newly added row
                cursor.close()
                break
        
        if session_id is None:
            raise Exception("Unable to get session_id. Internal server error")
        
        runinfo.msg("Session id: {:d}".format(session_id), "Starting main process (might take a while...)")
        
        #CREATE A PROCESS and a Pool of processes. For info see:
        
        #For info: http://stackoverflow.com/questions/25071910/multiprocessing-pool-calling-helper-functions-when-using-apply-asyncs-callback
        P = multiprocessing.Pool()
        runinfo.setprocess(P, session_id)
        #NOTES:
        #ARGUMENTS TO APPLY_ASYNC MUST BE PICKABLE, AS WELL AS THE FUNCTION (FIRST ARGUMENT).
        #SEE https://docs.python.org/2/library/pickle.html#what-can-be-pickled-and-unpickled
        #THIS MEANS THAT DISTRIBUTIONS MUST BE CREATED EACH TIME INSIDE OUR TARGET FUNCTION 
        #NOTE ALSO THAT FOR DEBUG WE SHOULD USE APPLY OR MAP, the COUNTERPART OF APPLY_ASYNC AND MAP_ASYNC, cause the latter
        #do not raise exceptions
        #See also https://github.com/tisimst/mcerp/blob/master/mcerp/__init__.py
        
        logdir = None
        if _DEBUG_:
            folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../_tmp/runerrors/{:d}".format(session_id))
            if os.path.exists(folder):
                print("EMPTYING DIR {0}".format(str(folder)))
                for the_file in os.listdir(folder):
                    file_path = os.path.join(folder, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception: pass
            elif os.path.exists(os.path.dirname(folder)):
                try:os.mkdir(folder)
                except: pass
                
            if os.path.exists(folder): logdir = folder
            
                
        #'opposite' to scalar defined above: returns a numpy.ndarray if the value represents an mcerp distribution,
        #otherwise the float value. Note that numpy.ndarray seems to be PICKABLE ('passable' as multiprocess.Pool argument)
        def val(value):
            #value = scenario[key]
            
            if isinstance(value, mcerp.UncertainFunction):
                return value._mcpts #this is a numpy.array element WHICH IS PICKABLE, SO IT CAN BE PASSED TO multiprocess.Pool
            else:
                return float(value) #parse to float to be sure
        
        #close the connection NOW?
        conn.commit()
        conn.close()
        conn = None
        
        #set percentiles. Note that any mcerp distribution raises error if percentiles are outside 
        #the number of points. Thus a distribution with 10 pts cannot calculate percentiles at, e.g., 0.05 and 0.95
        #we therefore need to set the mcepr npts here
        percentiles = globals.percentiles

        key_gm_only = gk.GMO
        gm_only = scenario[key_gm_only] if key_gm_only in scenario else globals.gm_only
        
        #gmpe's might contain uncertain functions defined in mcerp WHICH ARE NOT PICKABLE!
        #Given the fact that making them pickable seems to be a mess for our case
        #(examples found in the internet deal with easy to use cases), we FIRST 
        #calculate the intensity distribution, then we pass ITS ARRAY (a numpy array, which IS pickable)
        #to our geocell_run function
        #Drawback: we are not calculating intensity in a separate process, which means
        #we therefore do not take 100% advantages of the multiprocess pool
        
        for t in targets:
            if t is None: continue
            intensity = gmpe_func(t[3], t[2])
            
            #geocell_run(gmpe_func, t[3], t[2], percentiles, t[0], t[1], gm_only, scenario_id, session_id, logdir)
            P.apply_async(geocell_run, [val(intensity), t[3], t[2], percentiles, t[0], t[1], gm_only, scenario_id, session_id, logdir])
            #P.apply_async(geocell_run, [gmpe_func, t[3], t[2], percentiles, t[0], t[1], gm_only, scenario_id, session_id, logdir],kwds={})
            
        P.close()
            
    except Exception as e:
        exception = e
        if _DEBUG_:
            import traceback
            print(traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()
        if exception is not None:
            runinfo.stop(e)
            
        return runinfo

from math import sqrt
def ref_dist(gmpe_func, I_ref, km_step):
    """
        Given an epicenter with given magnitude M and depth depth_hyp, 
        returns the distance D in Km such that 
        I >= I_ref
    """
    max_percentile = globals.percentiles[len(globals.percentiles)-1]
    def val(value):
        return value.percentile(max_percentile) if isinstance(value, mcerp.UncertainFunction) else value
    
        
    k = 0
    lat_hyp = gmpe_func.lat #might be dist
    lon_hyp = gmpe_func.lon #might be dist
    lat_sta = lat_hyp
    lon_sta = lon_hyp
    
    D = 0.001 #0.0 #AVOIDS ROUND ERRORS IN GMPE DISTANCE OUT OF BOUNDS
    
    #define functions in all directions (n w s e and ne nw se sw):
    #Note: from index 3 on, we need to divide by sqrt(2)
    funcz = (
        lambda d: (lat_hyp + d, lon_hyp),
        lambda d: (lat_hyp, lon_hyp + d),
        lambda d: (lat_hyp - d, lon_hyp),
        lambda d: (lat_hyp, lon_hyp - d),
        lambda d: (lat_hyp + d, lon_hyp + d),
        lambda d: (lat_hyp - d, lon_hyp + d),
        lambda d: (lat_hyp - d, lon_hyp - d),
        lambda d: (lat_hyp + d, lon_hyp - d),
    )
    
    
    gmpe_maxd = float(gmpe_func.d_bounds[1])-0.001 #AVOIDS ROUND ERRORS IN GMPE DISTANCE OUT OF BOUNDS
    
    #Set min_d = D and max_d = gmpe's d_bounds[1], then perform a kind of binary 
    #serarch algrithm (O(logN) instead of O(N)), until we find the closest interval <= km_step 
    #such as I_ref >= I(min_d) and I_ref < max_d. If such distances are found,
    #set D = max_d if max_d > D. 
    #Note that the interval of search is "restricted" from second iteration on, which 
    #should further speed up the process
    
    def latlon0(func, dist_in_km):
        return func(gmpe_utils.km2deg(dist_in_km))
    
    sqrt_2 = sqrt(2)
    def latlon1(func, dist_in_km):
        return func(gmpe_utils.km2deg(dist_in_km/sqrt_2))
    
    l = len(funcz)
    for i in range(l):
        f = funcz[i]
        
        latlon = latlon0 if i<=3 else latlon1
        min_d = D
        max_d = gmpe_maxd
        
        
        
        I_min_d = val(gmpe_func(*latlon(f,min_d)))
        I_max_d = val(gmpe_func(*latlon(f,max_d)))
        
        isin = I_max_d < I_ref and I_min_d >= I_ref
        while isin:
            if max_d - min_d <= km_step: break
            mid_pt = (max_d+min_d)/2
            I = val(gmpe_func(*latlon(f,mid_pt)))
            if I < I_ref: 
                max_d = mid_pt
                I_max_d = I
            elif I >= I_ref: 
                min_d = mid_pt
                I_min_d = I
        

        
        if isin: 
            if max_d > D : D = max_d
        elif I_max_d >= I_ref: 
            D = gmpe_maxd
            break
        #else: #I_min_d < I_ref
            
    
    return D
    
#    I = gmpe_func(lat_sta, lon_sta)
#    
#    #FIXME: optimize calls to km2deg and deg2km?? 
#    
#    #define greater or equal than:
#    working_with_distributions = isinstance(I, mcerp.UncertainFunction)
#    if working_with_distributions:
#        #Note: returning I > I_ref returns the PERCENTAGE of data in the ditribution which is greater or equal than I_ref
#        #thus, False only if ALL distribution data is higher than I_ref. Which might be what we want, but need to be discussed
#        #For the moment we consider the mean
#        #min_percentile = globals.percentiles[0] 
#        max_percentile = globals.percentiles[len(globals.percentiles)-1]
#        def ge(I, I_ref): return I.percentile(max_percentile) >= I_ref #(I > I_ref) > min_percentile #
#    else:
#        def ge(I, I_ref): return I > I_ref
#        
#    while ge(I, I_ref):
#        k = k + km_step
#        lat_sta = lat_hyp + gmpe_utils.km2deg(k) #works also for uncertainfunctions
#        lon_sta = lon_hyp
#        I = gmpe_func(lat_sta, lon_sta)
#    
#        
#    #calc_percentiles(intensity, percentiles, target_id, geocell_id, scenario_id)
#    #return 16
#    ret_distance = gmpe_utils.deg2km(gmpe_utils.distance(lat_hyp,lon_hyp,lat_sta,lon_sta))
#    
#    #ret_distance should be ALWAYS a python number as we do a database query according to this number
#    #It should be the case cause all arguments are NOT mcerp UncertainFrunction's
#    #however, they MIGHT be numpy numbers, as some gmpe_utils functions are imported by mcerp.umath and the latter
#    #do return EITHER mcerp.UncertainFunctions OR numpy numbers
#    #Therefore, do a check with the numpy method item
#    if hasattr(ret_distance,"item"): 
#        #numpy number, get python number:
#        ret_distance = ret_distance.item()
#
#    return ret_distance

if __name__ == '__main__':
    pass
    #min_dist(7, 15, 5, 20)
#    event = {'longitude':74.2344, 'latitude':42.8, 'depth':15, 'strike':0, 'ipe':2, 'magnitude':6.8}
#    check_event(event)

    
#     step=10
#     Iref=5
#     #dict =  {'m' : mcerp.Uniform(7.2,7.4),'depth' : 15.0, 'lon' : 74.2,  'str' : 0, 'lat':42.8, 'strike':0, 'dip':0, 'sof':'reverse'}
#     dict =  {'m' : 6.8,'depth' : 15.0, 'lon' : 74.2,  'str' : 0, 'lat':42.8, 'strike':90, 'dip':90, 'sof':'reverse'}
#     
# #    gmpes = [gmpes.GlobalWaRup(**dict), gmpes.GlobalWaHyp(**dict),  gmpes.CentralAsiaEmca(**dict)]
#     
#     for m in [6.8]: #[5,5.5,6,6.5,7,7.5]:
#         dict['m'] = m
#         gmpez = [gmpes.GlobalWaRup(**dict), gmpes.GlobalWaHyp(**dict),  gmpes.CentralAsiaEmca(**dict)]
#         print("")
#         for g in gmpez:
#             print(str([g]) + ", m={:f}, I_ref={:f}, distance={:f} km".format(g.m, Iref, ref_dist(g, Iref, step)))
#     