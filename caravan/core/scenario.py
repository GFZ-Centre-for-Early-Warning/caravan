#! /usr/bin/python
"""
Module which handles the creation of a Caravan Scenario, an object representing a 
Caravan input event. Scenario stems from the name used in the database to indicate a seismic input event.

The module uses globals.py (glb in the module) to cast and check each new value added to a Scenario, for 
which its key matches a particular parameter defined in globals.py

Moreover, a Scenario can write to a database its values (using a special function to calculate an unique hash
from its values) 

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Sep 26, 2014 3:18:42 PM$"


from __builtin__ import hash as builtin_hash
import caravan.settings.globals as glb
from gmpes.gmpes import getgmpe
import caravan.settings.globalkeys as gk
import mcerp
import caravan.parser as prs

def hash(value):
    """
        returns the hash of value BUT accepts lists (which are converted to tuples in case) and dicts
        So hash([[1,2], "a" , {}, (4,)]) works
    """
    def is_mutable(value, opt_value_type=None): #is just a hint, returns True if value is dict, list, or tuple containing (recursive search) a dict or list
        t = type(value) if opt_value_type is None else opt_value_type
        if t == list or t==dict:
            return True
        elif t == tuple:
            has_mutable_children = False
            len_ = len(value)
            i=0
            while i<len_ and not has_mutable_children:
                has_mutable_children = is_mutable(value[i])
                i+=1
            return has_mutable_children
        else:
            return False
        
    def convert(value):
        t = type(value)
        if t == list or (t == tuple and is_mutable(value, t)):
            len_ = len(value)
            k = [None]*len_ #initialize a list
            for i in xrange(len_):
                k[i] = convert(value[i])
            return tuple(k)
        elif t == dict:
            k = [None]*2*len(value) #initialize a list
            i=0
            for key in value:
                k[i] = convert(key)
                k[i+1] = convert(value[key])
                i+=2
            return tuple(k)
        return value
    
    return builtin_hash(convert(value))
 
_scenario_name = 'scenario_name' #FIXME: is public. Good choice?

def scenario_hash(dict_):
    """
        Returns the hash of dict_ (a dict) according to s=glb.scenario_db_cols
        Builds a list L of N None values, where N = len(s). Then, for any key of dict_ 
        which is found in s, takes the relative index and puts L[index] = dict_[key]
        Returns the hash of L (as tuple, which is hashable)
    """
    params = glb.params
    
    dbindices = glb.scenario_db_cols
        
    dblen = len(dbindices)
    dbarray = [None]*dblen
    
    for k in dict_:
        if not k in params:
            continue
        param = params[k]
        if _scenario_name in param:
            column_name = param[_scenario_name]
            if column_name in dbindices:
                col_index = dbindices[column_name]
                dbarray[col_index] = dict_[k]
    
    return hash(dbarray)

def val_sc(pkey, p, value):
    """
        Returns the scenario value of the value argument, already casted according to p=glb.params[pkey]
    """
    
    if pkey == gk.IPE:
        return glb.def_gmpes[value]
    
    if pkey == gk.SOF:
        return glb.sof[value]
    
    isdistrib = 'distrib' in p
    if isdistrib:
        dist_name = p['distrib'].lower().title()
        if not prs.isscalar(value): #note that UncertainFunction is NOT scalar, 
            #but here we should have only numbers or array of numbers (according to params in glb)
            
            #try build a distribution with the given value(s)
            return mcerp.__dict__[dist_name](*value)
        
    return value

def val_db(pkey, p, value):
    """
        Returns the scenario value of the value argument, already casted according to p=glb.params[pkey]
    """
    isdistrib = 'distrib' in p
    if isdistrib:
        dist_name = p['distrib'].lower().title()
        if prs.isscalar(value):
            #value is scalar, define how to set db value:
            if dist_name == "Uniform" :
                return [value, value]
            elif dist_name == "Normal":
                return [value, 0]
            else:
                raise Exception("{0} distribution not implemented in cast function (scenario.py). Please contact the administrator".format(dist_name))
                
    return value

def tostr(dict, html=True):
    n = "\n" if not html else "<br>"
    s = "  " if not html else "&nbsp;&nbsp;"
    return "{{{0}{1}{0}}}".format(n, ',{0}'.format(n).join("{0}{1} = {2}".format(s, k, str(dict[k])) for k in dict))

#from collections import OrderedDict
#class Scenario(OrderedDict):
class Scenario(dict):
    
    def __init__(self, *args, **kwargs):
        super(Scenario, self).__init__() #<-- HERE call to super __init__. Useless if extending dict, necessary if extending OrderedDict
        self.__db = {}
        self.__dbhash = None
        self.update(*args, **kwargs) #note: pass args as positional arguments, not as (single) list owning those arguments
        
    def __setitem__(self, key, value):
        
        params = glb.params
        
        k_low = key.lower()
        if k_low in params:
            p = params[k_low]
            
            value = glb.cast(p, value)
            
            #cast to db_val:
            if _scenario_name in p:
                self.__db[k_low] = val_db(k_low, p, value)
                self.__dbhash = None
                
            #cast for scenario (self):    
            value = val_sc(k_low, p, value)
            
        super(Scenario, self).__setitem__(k_low, value)
              
    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("Scenario.update expected at most 1 arguments, got {:d}" .format (len(args)) )
            #if a scenario, don't check:
            if isinstance(args[0], Scenario):
                self.__dbhash = None #lazily initialized. In this case we don't call __setitem__ thus we need to call it here
                self.__db = args[0].__db.copy()
                for key in args[0]:
                    super(Scenario, self).__setitem__(key, args[0][key])
            else: #normal method:
                other = dict(args[0])
                for key in other:
                    self[key] = other[key] #calls __setitem__
                    
        for key in kwargs:
            self[key] = kwargs[key] #calls __setitem__
        
    
    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value #calls __setitem__
        return self[key]
    
    #from here:http://stackoverflow.com/questions/1436703/difference-between-str-and-repr-in-python
    #repr for developers, str for users
    #but should be worth a read, it's apparently a long story...
#     def __repr__(self):
#         return tostr(self)
    
    def dbstr(self):
        return tostr(self.__db)
    
    @property
    def gmpe(self):
        """
            Returns the gmpe used for this scenario. NOTE THAT INTERNALLY THE GMPE IS THE TUPLE 
            (gmpe_class_name, gmpe_dbase_index) (see cast function)
        """
        #REPLACE PARAMETERS WITH GMPE PARAMS. FIXME: VERY "DIRTY", DO SEOMTHING BETTER?
        d = {}
        d['m'] = self[gk.MAG]
        d['lat'] = self[gk.LAT]
        d['lon'] = self[gk.LON]
        d['depth'] = self[gk.DEP]
        
        if gk.SOF in self:
            d['sof'] = self[gk.SOF]
            d['strike'] = self[gk.STR]
            d['dip'] = self[gk.DIP]
        
        #FIXME: this adds also unnecessary arguments to the gmpe, including the GMPE name itself!
        #leave it like this??!!
        return self[gk.IPE](**d)
    
    def dbhash(self):
        if self.__dbhash is None: #lazily calculate it (it is set to None at startup and any time a key which has a 
        #parameter in glb.params p is found (and p must have the key _scenario_name)
            self.__dbhash = scenario_hash(self.__db)
        return self.__dbhash
    
    def writetodb(self, dbconn):
        """
            Writes this scenario to database returning the tuple scenario_id, isNew
            where the first item is an integer (serial key to access the scenario again) 
            and the second argument is a boolean indicating whether the scenario has been written to database 
            (true) or an already existing scenario with the same the hash as the cuirrent scenario has been found 
            (false): in that case scenario_id is the already existing sceenario id
            Raises excpetions if there are more than one scenarios with the same hash
        """
        scenario_hash = self.dbhash()
        
        
        scenarios = dbconn.fetchall("select * from processing.scenarios where hash=%s;" , (scenario_hash,))
        
        #the line above returns list objects. To return dict objects see
        #https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
        #cursor.close()
        
        #check if exists:
        if len(scenarios) > 1:
            raise Exception("{:d} scenarios with hash={:d}: database error, please contact the administrator".format(len(scenarios), scenario_hash));
        elif len(scenarios) == 1:
            return scenarios[0][0], False
        
        params = glb.params
    
        dbkeys = ['hash']
        dbvals = [scenario_hash]
        
        for k in self.__db:
            if not k in params: continue #for safety
            p = params[k]
            if _scenario_name in p: #for safety, again
                dbkeys.append(p[_scenario_name])
                dbvals.append(self.__db[k])
            
        dbkeys_str = ','.join([k for k in dbkeys])
        db_str = ",".join(["%s" for _ in dbkeys])

        arg1 =  """INSERT INTO processing.scenarios ({0}) VALUES ({1});""" .format (dbkeys_str, db_str) 
        arg2 = tuple(dbvals)
        
        dbconn.execute(arg1, arg2)
        dbconn.commit()
        
        scenarios = dbconn.fetchall("select * from processing.scenarios where hash=%s;" , (scenario_hash,))
        return scenarios[0][0], True
        
        
# if __name__ == '__main__':
#    
#     from __future__ import print_function
# #    from  collections import OrderedDict
# 
#     #min_dist(7, 15, 5, 20)
#     event = {'longitude': '74.2354 0.5', 'latitude':42.8, 'depth':15, 'strike':0, 'ipe':2, 'magnitude':6.8}
#     db = Scenario(event)
#     
#     print(str(db))
#     
#     print(scenario_hash(event))
    