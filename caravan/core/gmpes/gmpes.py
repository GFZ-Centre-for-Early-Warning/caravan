#! /usr/bin/python
# -*- coding: utf-8 -*-
#the line above so that we can safely copy refs for gmpes without worrying about encoding
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
    
    @staticmethod
    def disthyp(lat_hyp, lon_hyp, depth_hyp, lat, lon):
        """
            Returns the distance, in km, from the hypocenter whose latitude, longitude 
            and depth are lat_hyp, lon_hyp and depth_hyp, respectively, and a generic location 
            whose latitude and longitude are lat and lon, respectively.
            All arguments are assumed in degrees except for depth, in km
        """
        chord = chorddistance(lat_hyp, lon_hyp, lat, lon)
        return sqrt(depth_hyp**2 + chord**2)
    
    @staticmethod
    def distepi(lat_epi, lon_epi, lat, lon):
        """
            Returns the distance, in km, from the epicenter whose latitude, longitude 
            are lat_epi and lon_epi, respectively, and a generic location 
            whose latitude and longitude are lat and lon, respectively.
            All arguments are assumed in degrees. The returned distance is the arc
            of the great circle  passing for the epicenter and the given location
        """
        return deg2km(greatarc_dist(lat_epi, lon_epi, lat, lon))
        
    
    #Ideally, we might want to provide static properties for these two arguments, i.e., 
    #@property and #classmethods decorators. There is a possibility BUT does not work in PY3
    #(see http://stackoverflow.com/questions/128573/using-property-on-classmethods, 2ND ANSWER)
    #As long as these properties can be set and got, it is easier just to implement the static vars here
    #subclasses might define them, or if missing, they will devalut to these given values:
    ref = ""
    sourcetype = None
    
    """
        "Abstract" base class for gmpes (actually, ipe's), which are callable 
        (and therefore "function-like" classes) returning the intensity at a given 
        location (g(lat, lon)) or at a given gmpe distance (g.(d)), where the 
        notion of distance is gmpe dependent. 
        A constructor of this class accepts a dict-like series of arguments 
        (e.g. g = MyGmpe(arg1g=val1, arg2=val2,...)) and will set the given arguments 
        as class attributes. In principle, the following argument should be always 
        provided: m (magnitude), lat (latitude, in degrees), lon (longitude, in degrees)
        depth (self-explanatory, in km) (NOTE: m is actually mandatory); in addition ,
        for consistency across implementations, if any of the following additional 
        parameters is passed as argument, it should be written as:
        strike (in degrees), dip (in degrees), slip (in degrees) and sof (style of 
        faulting, see gmpe_utils.SOF)
        In general, there is no restriction on the arguments of a Gmpe as long 
        as they let the gmpe can be callable. Therefore, the Gmpe cnstructor, 
        __init__, calls the class as a function with a "fake" point [0,0] to check 
        the well formation of the arguments (a new gmpe implementation should hence 
        either should not override the __init__ method or, if it does, should call 
        the super __init__ method). 
        
        Skeleton of a typical implementation:
        ------------------------------------------------------------------------
        class MyGmpe(Gmpe):
            ref = ""
            sourcetype = 0 #or1
            d_bounds = (0, 150)
            m_bounds = (4, 7.6)
            
            def distance(self, lat, lon):
                #implement the Gmpe distance
            
            def calculate(self, distance):
                #implement the calculation of the intensity at a given distance
        ------------------------------------------------------------------------
        
        ref is a string which is not mandatory (defaults to "") and represents 
            the reference paper for the given gmpe. It will be displayed, if any, using the str function with 
            argument a given Gmpe. This is a "static" attribute which holds for 
            all Gmpe's of the same type
        
        sourcetype denotes the source type, 0 for "point", 1 for "extended". 
            By default it is None (implemented in the base class Gmpe). THIS PARAMETER 
            SHOULD ALWAYS BE PROVIDED, as any Gmpe which overrides __init__ 
            should call the super.__init__ method which checks the parameters 
            according to the sourcetype. For instance, sourcetype=1 needs strike, 
            dip and either slip or sof (style of faulting). This is also a static 
            attribute which holds for all Gmpes of the same type
        
        m_bounds and d_bounds are 2-elements tuples (or lists) denoting the 
            bounds (min, max) of magnitude and distances, repectively. They raise 
            exceptions if the given magnitude m (which is therefore mandatory in 
            the __init__ method) and location distance (calculated when calling the gmpe) 
            are not in the specified range. Note that distance is assumed here as 
            the epicentral distance from the point of interest, not the gmpe distance (see below)
        
        distance returns the gmpe distance from the source to the point [lat, lon], 
            and it's implementation dependent. There are two static methods:
                Gmpe.disthyp(lat_hyp, lon_hyp, depth_hyp, lat, lon)
                Gmpe.distepi(lat_epi, lon_epi, lat, lon):
            which can turn out to be handy especially for point source types.
        
        calculate returns the intensity at the given implemented distance.
        
        None of the implemented methods is usually called directly: a new Gmpe 
        is callable, i.e.it bahaves like a function. Defined a new Gmpe class, 
        say MyGmpe, you can create a new instance as usual via, e.g.:
            g = MyGmpe(lat=mcerp.Normal(0,0.01),lon=75, depth=10, m=5, strike=40, 
                dip=40, sof = gmpe_utils.SOF.REVERSE)
        
        As you can see, you can pass numeric values but also pass mcerp distributions.
        
        Then you can get the intensity at a given location (lat=40, lon=30, in 
        degrees) by calling (two arguments):
            I = g(40, 30)
        or alternatively (single argument) get the intensity at a given gmpe distance 
        (e.g., 35km):
            I = g(35)
        As already said, note that the gmpe distance is IMPLEMENTATION dependent: it might 
        be hypocentral, epicentral, or more complex (especially for sourcetype's 1, 
        i.e. extended). A sourcetype=0 (point source) assures in principle the 
        same intensity on all points on a circle centered in the given epicenter. 
        This is not assured for sorucetype's =1 (extended source) 
                    
    """
    
    def __init__(self, **kwargs):
        
        #(see http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/)
        self.__dict__.update(kwargs)
        
        if not hasattr(self, 'm'):
            raise Exception('{0} error: missing magnitude'.format(self.__repr__()))
        
        if self.m > self.m_bounds[1] or self.m < self.m_bounds[0]:
            raise Exception("{0} error: magnitude not in {1}".format(self.__repr__(), str(list(self.m_bounds) ) )) #because list str is like closed interval in math
        
        
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
                self(self.lat, self.lon)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(self.__class__.__name__+" error: {0}".format(str(e)))
        
        if not hasattr(self.__class__,"ref"): #for safety
            setattr(self.__class__, "ref", "")
        
        
    def __call__(self, *args):
        """
            Calculates the current gmpe given args. If len(args)==1, then it is the 
            distance D from the hypocenter to the point of interest
            If len(args)==2, then it is the latitude and longitude of the point of interest: in that 
            case, D=distance(lat, lon), which varies across implementations (see subclasses)
            In any other cases, an Exception is raised
        """
        l = len(args)
        if l == 2:
            epidist = Gmpe.distepi(self.lat, self.lon, args[0], args[1])
            if epidist > self.d_bounds[1] or epidist < self.d_bounds[0]:
                
                
                raise Exception("{0} error: unable to calculate intensity at (lat={1:f}, lon={2:f}), epicentral distance ({3:f}) not in {4}".
                    format(self.__repr__(), args[0], args[1], epidist, str(list(self.d_bounds)) )) #because list str is like closed interval in math
        
        distance = self.distance(args[0], args[1]) if l == 2 else args[0] if l == 1 else None
        if distance is None:
            raise Exception("A gmpe must be called with either 1 (distance) or 2 (lat, lon) arguments")
        return self.calculate(distance)
        
    def distance(self, lat, lon):
        raise Exception("distance(lat, lon) method not implemented")
    
    def calculate(self, distance):
        raise Exception("calculate(distance) method not implemented")
    
    def __repr__(self):
        return self.__class__.__name__
    
    def __str__(self):
        return self.__repr__() + (" ("+self.ref+")" if self.ref else "")+". Parameters:" +str(self.__dict__)
    
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
    ref = "Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409–433"
    sourcetype = 1
    #c0, c1, c2 c3
    __constants = (3.950, 0.913, -1.107, 0.813)
    
    m_bounds = (5 , 7.9)
    d_bounds = (0, 300)
    
#    def __call__(self, lat, lon):
#        if not hasattr(self, "_rld"):
#            self._rld, self._rw = rld_rw(self.sof)(self.m)
#        
#        c0, c1, c2, c3 = self.__constants
#        
#        r_rup = rup_distance(lat, lon, self.lat, self.lon, self.depth, self.strike, self.dip, self._rld, self._rw)
#        
#        return c0 + c1 * self.m + c2 * log (sqrt( r_rup ** 2 + (1 + c3 * exp(self.m -5)) **2 ))
    
    def calculate(self, distance):
        c0, c1, c2, c3 = self.__constants
        I = c0 + c1 * self.m + c2 * log (sqrt( distance ** 2 + (1 + c3 * exp(self.m -5)) **2 ))
        return I
    
    def distance(self, lat, lon):
        if not hasattr(self, "_rld"):
            self._rld, self._rw = rld_rw(self.sof)(self.m)
        R_rup = rup_distance(lat, lon, self.lat, self.lon, self.depth, self.strike, self.dip, self._rld, self._rw)
        return R_rup
    
class GlobalWaHyp(Gmpe):
    #defining constants (c0, c1 , c2 , c4, m1, m2). FIXME: works like Java, does it save memory?)
    __constants = (2.085, 1.428, -1.402, 0.078, -0.209, 2.042)
    
    ref = "Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409–433"
    sourcetype = 0
    
    m_bounds = (5 , 7.9)
    d_bounds = (0, 300)
    
#    def __call__(self, lat, lon):
#        #TO BE IMPLEMENTED
#        #getting constants:
#        c0, c1 , c2 , c4, m1, m2 = self.__constants
#        
#        #R_hyp = _threed_dist(self.lat, self.lon, self.depth, lat, lon, 0)
#        
#        chord = chorddistance(self.lat, self.lon, lat, lon)
#        R_hyp = sqrt(self.depth**2 + chord**2)
#        
#        M = self.m #magnitude
#        R_M = m1 + m2 * exp(M-5)
#        I = c0 + c1 * M + c2 * log(sqrt(R_hyp ** 2 + R_M ** 2));
#
#        if R_hyp > 50:
#            I = I + c4 * log(R_hyp/50)
#
#        return I
    
    def calculate(self, distance):
        c0, c1 , c2 , c4, m1, m2 = self.__constants
        M = self.m #magnitude
        R_M = m1 + m2 * exp(M-5)
        I = c0 + c1 * M + c2 * log(sqrt(distance ** 2 + R_M ** 2))
        if distance > 50:
            I = I + c4 * log(distance/50)

        return I
    
    def distance(self, lat, lon):
        return Gmpe.disthyp(self.lat, self.lon, self.depth, lat, lon)
    
class CentralAsiaEmca(Gmpe):
    #defining constants (xEP1, xEP2 , xEP3 , xEP4, xEP5):
    __constants = (1.0074538, -2.0045088, 3.2980663, 2.6920855, 4.2344195e-04)
    ref = "Intensity prediction equations for Central Asia (Bindi et al.). Geophys. J. Int. (2011) 187, 327–337"
    sourcetype = 0
    m_bounds = (4.6 , 8.3)
    d_bounds = (0, 600)
    
#    def __call__(self, lat, lon):
#        #TO BE IMPLEMENTED
#        #getting constants:
#        xEP1, xEP2, xEP3, xEP4, xEP5 = self.__constants
#        
#        dist_epi_sta = deg2km(greatarc_dist(self.lat, self.lon, lat, lon))
#        
#        M = self.m #magnitude
#        depth = self.depth
#        
#        return xEP1*M + xEP2*log10(depth) + xEP3 - xEP4*0.5*log10((dist_epi_sta/depth)**2 + 1) - xEP5*(sqrt(dist_epi_sta**2 + depth**2)-depth)

    def calculate(self, distance):
        xEP1, xEP2, xEP3, xEP4, xEP5 = self.__constants
        M = self.m #magnitude
        depth = self.depth
        return xEP1*M + xEP2*log10(depth) + xEP3 - xEP4*0.5*log10((distance/depth)**2 + 1) - xEP5*(sqrt(distance**2 + depth**2)-depth)
    
    def distance(self, lat, lon):
        return Gmpe.distepi(self.lat, self.lon, lat, lon)
    
if __name__ == "__main__":
    import mcerp
    v = GlobalWaHyp(lat=42.87,lon=74.6, depth=15, m=mcerp.Uniform(6.8, 7.2))
    print(v(43,78))
#     print str(getgmpe("GlobalWaRup"))+ " "+ str(type(getgmpe("GlobalWaRup")))
#     
#     from gmpe_utils import SOF
#     for g in getgmpes("core"):
#         print "DOC " + str(g[1].doc)
#         c= g[1](lat=mcerp.Normal(0,0.01),lon=75, depth=10, m=5, strike=40, dip=40, sof = SOF.REVERSE)
#         c(45, 23)
#         print str(c)+" "+str(c.sourcetype)
#         print "\n\n"
    
  