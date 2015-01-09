#! /usr/bin/python
"""
Module holding GMPE's functions. Note: the arguments of the gmpe's can be scalars, vectors 
or distributions. They call, when necessary, umath functions (sin, sqrt, log etcetera) which 
check if the arguments are distributions or not, but in any case call back numpy relative functions
(for a detailed info about numpy universal functions, see http://docs.scipy.org/doc/numpy/reference/ufuncs.html and if you want more details, 
also numpy's array array object: http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html#numpy.ndarray)

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

from __future__ import print_function

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Aug 20, 2014 2:56:26 PM$"


#from math import exp, sqrt, log, log10
#NO! USE mcepr's umath
from mcerp.umath import exp, sqrt, log, log10
from gmpe_utils import distance as greatarc_dist, deg2km, chorddistance
import mcerp

def _threed_dist(lat1, lon1, depth1, lat2, lon2, depth2):
    """
        Returns the 3D distance from point1 to point2
    """
    return sqrt( (lat1-lat2)**2 + (lon1-lon2)**2 + (depth1-depth2)**2 )

def global_wa_hyp(M, lat_hyp, lon_hyp, depth_hyp, lat_sta, lon_sta):
    """
        Computed intensity prediction equation according to Wald & Allan, 2012
        
        Parameters:
            M magnitude
            lat_hyp, lon_hyp, depth_hyp: coordinates of the hypocenter (latitude, longitude, depth, respectively)
            lat_sta, lon_sta: coordinates of the station (latitude and longitude, respectively)
            
        Returns:
            a number
    """
    
    #defining constants:
    c0 = 2.085
    c1 = 1.428
    c2 = -1.402
    c4 = 0.078
    m1 = -0.209
    m2 = 2.042
    
    R_hyp = _threed_dist(lat_hyp, lon_hyp, depth_hyp, lat_sta, lon_sta, 0)
    
    R_M = m1 + m2 * exp(M-5)
    I = c0 + c1 * M + c2 * log(sqrt(R_hyp ** 2 + R_M ** 2));
    
    if R_hyp > 50:
        I = I + c4 * log(R_hyp/50)
    
    return I


def centralasia_emca_1(M, lat_hyp, lon_hyp, depth_hyp, lat_sta, lon_sta): #h=Depth, R=distanza in R2 tra epicentro e stazione. DISTANZE IN KM!!!!
    """
        Computed intensity prediction equation for central asia.
        
        Parameters:
            M magnitude
            lat_hyp, lon_hyp, depth_hyp: coordinates of the hypocenter (latitude, longitude, depth, respectively). depth must be positive
            lat_sta, lon_sta: coordinates of the station (latitude and longitude, respectively)
            
        Returns:
            a number
    """
    
    dist_epi_sta = deg2km(greatarc_dist(lat_hyp,lon_hyp,lat_sta, lon_sta))
    return _centralasia_emca_1(M, depth_hyp,dist_epi_sta)

def _centralasia_emca_1(M, depth, dist_epi_sta): #h=Depth, dist_epi_sta=distanza in R2 tra epicentro e stazione. DISTANCES IN KM!!!!
    """
        Computed intensity prediction equation for central asia
        given a Magnitude M, the hypocenter depth and the distance between epicenter and station
    """
#computed intensity for Central Asia
#Epicentral and EXtended distances;
#Input: mag,depth,distance values
#distance can be a vector
    xEP1 =1.0074538
    xEP2 = -2.0045088
    xEP3 = 3.2980663
    xEP4 = 2.6920855
    xEP5 = 4.2344195e-04
    
    return xEP1*M + xEP2*log10(depth) + xEP3 - xEP4*0.5*log10((dist_epi_sta/depth)**2 + 1) - xEP5*(sqrt(dist_epi_sta**2 + depth**2)-depth)


import inspect
import sys
    
def getgmpe(name):
    """
        Returns the CLASS of the given name, implemented in THIS MODULE
    """
    return sys.modules[__name__].__dict__[name] #__dict__[name]

def getgmpes(*module_names):
    """
        Returns all Gmpe's classes implemented in this module
    """
    return _get_subclasses(Gmpe, sys.modules[__name__], *module_names)
    
def _get_subclasses(cls, *modules):
    """
        Yields the classes in the given modules that inherit from ``cls``. From the same 
        module, mod should be sys.modules[__name__] (after importing sys) UNLESS this function is 
        run from __main__ (in that case __name__ is "__main__" and will not return any member)
        Returns the tuple name, obj (class name and class object)
        Copied from http://stackoverflow.com/questions/44352/iterate-over-subclasses-of-a-given-class-in-a-given-module
    """
    for mod in modules:
        if isinstance(mod, str): #note: not PY2 compatible!!!!

            try:
                mod = sys.modules[mod]
            except:
                continue
        for name, obj in inspect.getmembers(mod):
            if hasattr(obj, "__bases__") and cls in obj.__bases__:
                yield name, obj


class Gmpe(object):
    #Ideally, we might want to provide static properties for these two arguments, i.e., 
    #@property and #classmethods decorators. There is a possibility BUT does not work in PY3
    #(see http://stackoverflow.com/questions/128573/using-property-on-classmethods, 2ND ANSWER)
    #As long as these properties can be set and got, it is easier just to implement the static vars here
    #subclasses might define them, or if missing, they will devalut to these given values:
    doc = ""
    sourcetype = None
    
    """
        "Abstract" base class for gmpes (actually, ipe's). 
        A gmpe takes a dict-like series of arguments, also as mcerp dictricution, e.g.:
            g = MyGmpe(lat=mcerp.Normal(0,0.01),lon=75, depth=10, m=5, strike=40, dip=40, sof = gmpe_utils.SOF.REVERSE)
        and calculate the intensity in a given point (e.g., [lat =40, lon =30) by simply calling
            I = g(40, 30)
        Therefore, implementation should just overrride the __call__(lat, lon) method to perform the calculation
        of the intensity in a given point. Note that the __call__ method is called from within the constructor for 
        a "fake" point [0,0] to check well formation of the arguments.
        
        There are two optional "static" attributes which are used if provided:
        sourcetype: 0 for "point", 1 for "extended". This is returned by gmpe.sourcetype.
                By default it is None (implemented in the base class Gmpe). THIS PARAMETER SHOULD ALWAYS BE PROVIDED,
                as applications might load gmpes according to the value returned by it
        doc: returns the doc string for the given gmpe class (this can be used also 
                with gmpe.doc ="a doc" which sets the CLASS doc attribute (i.e., valid for any object).
                By default it is the empty string (implemented in the base class Gmpe)
                    
    """
    
    def __init__(self, **kwargs):
        
        #(see http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/)
        self.__dict__.update(kwargs)
        
        #add spf if slip is present and not sof
        if not hasattr(self, "sof") and hasattr(self, "slip"):
            from gmpe_utils import sof as _sof
            self.sof = _sof(self.slip)
        
        if self.sourcetype == 1 and (not hasattr(self, "sof") or not hasattr(self, "dip") or not hasattr(self, "strike")):
            raise Exception("Extended source type gmpe needs strike, dip and either slip or sof (style of faulting)")
        #now final check: just run this gmpe with 0 lattitude and 0 longitude.
        #This assures all parameters are correctly set. 
        #Otherwise, catch any exception and raise it. On the other hand supporess warnings
        #as we are not interested, e.g., in NaN's or other stuff. 
        #FIXME: also call with uncertain functions?
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self(0,0)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(self.__class__.__name__+" error: {0}".format(str(e)))
        
        if not hasattr(self.__class__,"doc"):
            setattr(self.__class__, "doc", "")
        
        
    def __call__(self, lat, lon):
        raise Exception("__call__ method not implemented")
    
    def __repr__(self):
        return self.__class__.__name__
    
    def __str__(self):
        return self.__class__.__name__ + (": "+self.doc if self.doc else "")+". Parameters:" +str(self.__dict__)

#I (M, R_hyp) = c0 +c1 M + c2 ln (sqrt(R_hyp^2 +R_M^2)) + S
#
#I (M, R_hyp) += c4  ln (R_hyp/50) for Rhyp>50
#
#c0 = 2.085
#c1 = 1.428
#c2 = -1.402
#c4 = 0.078
#R_M = m1 + m2 exp(M-5)
#m1 = -0.209
#m2 = 2.042
#
#===========================================
#
#I(M, R_rup) = c0 + c1 M + c2 ln (sqrt( R_rup^2 + [1 + c3 exp(M-5)]^2 ))
#
#c0 = 3.950
#c1 = 0.913
#c2 = -1.107
#c3 = 0.813

from gmpe_utils import rup_distance, rld_rw

class GlobalWaRup(Gmpe):
    doc = "global I.P.E. (Allen et al., 2012), based on rupture distance"
    sourcetype = 1
    #c0, c1, c2 c3
    __constants = (3.950, 0.913, -1.107, 0.813)
    
    def __call__(self, lat, lon):
        if not hasattr(self, "_rld"):
            self._rld, self._rw = rld_rw(self.sof)(self.m)
        
        c0, c1, c2, c3 = self.__constants
        
        r_rup = rup_distance(lat, lon, self.lat, self.lon, self.depth, self.strike, self.dip, self._rld, self._rw)
        
        return c0 + c1 * self.m + c2 * log (sqrt( r_rup ** 2 + (1 + c3 * exp(self.m -5)) **2 ))

    
class GlobalWaHyp(Gmpe):
    #defining constants (c0, c1 , c2 , c4, m1, m2). FIXME: works like Java, does it save memory?)
    __constants = (2.085, 1.428, -1.402, 0.078, -0.209, 2.042)
    
    doc = "global I.P.E. (Allen et al., 2012), based on hypocentral distance"
    sourcetype = 0
         
    def __call__(self, lat, lon):
        #TO BE IMPLEMENTED
        #getting constants:
        c0, c1 , c2 , c4, m1, m2 = self.__constants
        
        #R_hyp = _threed_dist(self.lat, self.lon, self.depth, lat, lon, 0)
        
        chord = chorddistance(self.lat, self.lon, lat, lon)
        R_hyp = sqrt(self.depth**2 + chord**2)
        
        M = self.m #magnitude
        R_M = m1 + m2 * exp(M-5)
        I = c0 + c1 * M + c2 * log(sqrt(R_hyp ** 2 + R_M ** 2));

        if R_hyp > 50:
            I = I + c4 * log(R_hyp/50)

        return I

class CentralAsiaEmca(Gmpe):
    #defining constants (xEP1, xEP2 , xEP3 , xEP4, xEP5):
    __constants = (1.0074538, -2.0045088, 3.2980663, 2.6920855, 4.2344195e-04)
    
    sourcetype = 0
        
        
    def __call__(self, lat, lon):
        #TO BE IMPLEMENTED
        #getting constants:
        xEP1, xEP2, xEP3, xEP4, xEP5 = self.__constants
        
        dist_epi_sta = deg2km(greatarc_dist(self.lat, self.lon, lat, lon))
        
        M = self.m #magnitude
        depth = self.depth
        
        return xEP1*M + xEP2*log10(depth) + xEP3 - xEP4*0.5*log10((dist_epi_sta/depth)**2 + 1) - xEP5*(sqrt(dist_epi_sta**2 + depth**2)-depth)


if __name__ == "__main__":
    #argz = ("lat", "lon", "depth", "m", "strike", "dip", "sof")
    
    print(str(getgmpe("GlobalWaRup"))+ " "+ str(type(getgmpe("GlobalWaRup"))))
    
    from gmpe_utils import SOF
    for g in getgmpes("core"):
        print("DOC " + str(g[1].doc))
        c= g[1](lat=mcerp.Normal(0,0.01),lon=75, depth=10, m=5, strike=40, dip=40, sof = SOF.REVERSE)
        c(45, 23)
        print(str(c)+" "+str(c.sourcetype))
        print("\n\n")
    
#    from gmpe_utils import SOF
#    
#    c = GlobalWaRup(lat=mcerp.Normal(0,0.01),lon=75, depth=10, m=5, strike=40, dip=40, sof = SOF.REVERSE)
#    c(45,23)

  