#! /usr/bin/python

"""
Ground motion prediction equation utilities. Uses numpy and mcerp libraries 
to allow each function 
arguments to be passed either as scalar, as numpy array or as UncertainFunction (distributions)

NOTE: All functions accept distributions (mcerp.UncertainFunction(s)) numpy numeric types and python numeric types,
handling the relative operations internally. It is not asssured, though, that passing two python numeric types (scalars) 
will return a python numeric type: sometimes, a numpy numeric type might be returned (see mcerp.umath)
This is fine as long as the returned values need to be used by code computation, as all types support mixed math 
operations and relations (either of order or of equivalence), some problems might arise by those libraries 
(e.g., psycopg2) which might need python numeric types for IO database operations

Code modified from matlab utility using the algorithm proposed in 
James Kaklamanos, Laurie G Baise, and David M Boore (2011) 
Estimating Unknown Input Parameters when Implementing the NGA Ground-Motion Prediction Equations 
in Engineering Practice. Earthquake Spectra, vol. 27 (4) p. 1219

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" #riccardo (
__date__ ="$Aug 11, 2014 3:50:26 PM$"

#from math import pi,cos,sin,atan,sqrt,atan2,asin,tan,ceil, isnan, degrees as rad2deg, radians as deg2rad #NOTE: abs is a builtin function, not in math!
#from parser import isexpr
from mcerp.umath import cos,sin,atan,sqrt,asin,tan,ceil, degrees as rad2deg, radians as deg2rad #NOTE: abs is a builtin function, not in math!
from mcerp import UncertainFunction
import numpy as np

from math import pi
#EARTH RADIUS IN KILOMETERS:
EARTH_RADIUS = 6371.0 #Use the comma so division do not round to integers!!!
#variables used in the functions below (might speed up calculations if calculated once?)
#PI = math.pi
#TWO_PI = PI*2
#HALF_PI = PI/2
TWO_PI = pi*2
HALF_PI = pi/2
THREE_HALF_PI = 3*pi/2

def mod(x1, x2):
    """
        Modulus (element-wise) i.e. x1 % x2
    """
    x1_is_U = isinstance(x1, UncertainFunction) 
    x2_is_U = isinstance(x2, UncertainFunction) 
    
    if x1_is_U and x2_is_U:
        mcpts = np.mod(x1._mcpts, x2._mcpts)
    elif x1_is_U:
        mcpts = np.mod(x1._mcpts, x2)
    elif x2_is_U:
        mcpts = np.mod(x1, x2._mcpts)
    else:
        return np.mod(x1, x2).item() #FIXME: we return a python numeric type? yes for the moment
    return UncertainFunction(mcpts)

def sign(x):
    """
    Signum of a distribution/numpy array
    """
    if isinstance(x, UncertainFunction):
        mcpts = np.sign(x._mcpts)
        return UncertainFunction(mcpts)
    else:
        return np.sign(x).item() #FIXME: we return a python numeric type? yes for the moment

def atan2(x1, x2):
    """
        Element-wise arc tangent of x1/x2 choosing the quadrant correctly.
    """
    x1_is_U = isinstance(x1, UncertainFunction) 
    x2_is_U = isinstance(x2, UncertainFunction) 
    
    if x1_is_U and x2_is_U:
        mcpts = np.arctan2(x1._mcpts, x2._mcpts)
    elif x1_is_U:
        mcpts = np.arctan2(x1._mcpts, x2)
    elif x2_is_U:
        mcpts = np.arctan2(x1, x2._mcpts)
    else:
        return np.arctan2(x1, x2).item() #FIXME: we return a python numeric type? yes for the moment
    return UncertainFunction(mcpts)

    
def sof(slip_deg):
    """
        Returns the style-of-faulting (SOF) given a slip (in degree). Possible values are "Normal", "Reverse" or "Strike-Slip"
        Deprecated: this function does not conform the asusmption that each function within this module accepts either distribution, arrays or scalars
    """
    if slip_deg >= -150 and slip_deg <= -30:     #Determine the style-of-faulting (SOF)
        return SOF.NORMAL  #'Normal'
    elif slip_deg >= 30 and slip_deg <= 150:
        return SOF.REVERSE #'Reverse'
    else:
        return SOF.STRIKE_SLIP  #'Strike-Slip'

##enum implementation (for compatibility with PY<3.4)
##each enum item E is an object storing two proepries E.index (index of declaration) E.value (if missing it is E.index)
##each E string representation is the name of the item, as declared: 
##   myenum = enum("APPLE","BANANA","NOFRUIT"=7)
##creates three E's: APPLE (index=0, value=0), BANANA (index=1, value=1), NOFRUIT (index=2, value=7)
##accessible by simply typing: myenum.BANANA, myenum.FRUIT, ... etcetera
##You can access an enum by index using 
##   myenum.values()
##which returns the tuple of enum items (APPLE, BANANA, NOFRUIT) (in the order they are declared)
##You can also "parse" a string to an enum with 
##   myenum.valueof(string)
##which raises an exception if string does not match (case sensitive) any 
##of the enum items. If string is a valid enum type, then returns it. 
##Otherwise, e.g.: myenum.valueof("BANANA") = BANANA
##Note that enum item names starting and ending with double underscore, or equal to either "values" or "valueof"
##will raise exceptions
#def enum(*enum, **enums):
#    class e(object):
#        def __init__(self, index, name, value):
#            self.__name, self.__value, self.__index = name, value, index
#        @property
#        def index(self): return self.__index    
#        @property
#        def value(self): return self.__value
#        def __hash__(self): return hash((self.__name, self.__index, self.__value))
#        def __repr__(self): return self.__name
#    
#    def check(name):
#        if (len(name)>3 and name[:2] =="__" and name[-2:] =="__") or name == "values" or name =="valueof":
#            raise Exception("'{0}': no enum names with double trailing and leading underscores or equal to 'values' or 'valueof' (reserved methods)".format(name))
#        return name
#    
#    idx=0
#    d = {}
#    for v in enum:
#        d[check(v)] = e(idx, v, idx)
#        idx+=1
#    
#    for k in enums:
#        v = enums[k]
#        d[check(k)] = e(idx, k, v)
#        idx+=1
#    
#    def vals(self):
#        if not hasattr(self, "__values__"): #DO NOT WORK WITH self.__dict__ as IT DOES NOT SUPPORT DIRECT ITEM ASSIGNEMENT. USE attribute functions:
#            setattr(self, "__values__", tuple(sorted([v for _, v in d.iteritems() if isinstance(v,e)], key = lambda elm: elm.index)))
#        return getattr(self, "__values__")
#    
#    def valof(self, v):
#        if isinstance(v, e): #make a set lazily (and store it in __values2__) from the builtin tuple. Faster if we have several enum types, memory shouldn't be affected
#            if not hasattr(self, "__values2__"): setattr(self, "__values2__",frozenset(self.values()))
#            if v in getattr(self, "__values2__"): return v
#        elif v in self.__dict__ and isinstance(self.__dict__[v], e): return self.__dict__[v]
#        raise Exception("{0} not found".format(str(v)))
#    
#    def contains(self, v): return v in self.values()
#    
#    en = type('Enum', (object,), d)
#    #bind methods:
#    import types
#    en.values = types.MethodType(vals, en)
#    en.valueof = types.MethodType(valof, en)
#    en.__contains__ = types.MethodType(contains, en)
#    return en
#    
#SOF = enum(REVERSE= "reverse",NORMAL = "normal",STRIKE_SLIP = "strike-slip",UNKNOWN="unknown")

class SOF(object):
    REVERSE= "reverse"
    NORMAL = "normal"
    STRIKE_SLIP = "strike-slip"
    UNKNOWN = "unknown"

#class SOF(object):
#    REVERSE = "reverse"
#    NORMAL = "normal"
#    STRIKE_SLIP = "strike-slip"
#    UNKNOWN = "unknown"
#    
#    @classmethod
#    def values(clz):
#        if not "__VALUES__" in clz.__dict__:
#            lst = []
#            for k in clz.__dict__:
#                if (len(k)>1 and k[:2] == "__") or k == "valueof" or k == "values":
#                    continue
#                lst.append(clz.__dict__[k])
#            clz.__dict__.__VALUES__ = frozenset(lst)
#        return clz.__dict__.__VALUES__
#    
#    @staticmethod
#    def valueof(val): #fixme: implement better search?
#        v = SOF.values()
#        if val in v:
#            return val
#        try:
#            if val.lower() in SOF.VALUES: return val
#        except: pass
##            raise Exception("Cannot convert {0} to a valid style of faulting".format(str(val)))
#        return None    

def rld_rw(sof):
    """
        Returns a function of magnitude mw which in turn returns the tuple RLD, RW
        According to Donald et all 1994
        sof can be one of the SOF.REVERSE, SOF.UNKNOWN, SOF.STRIKE_SLIP and SOF.NORMAL values
        (
    """
    # Formulas and relative coeffients for calculating RLD and RW from magnitude M
    # (Donald Wells and Coopersmith, p.990)
    # SS: strike-slip, R: reverse, N: normal,  All :unknown
    #
    #                               a           b 
    #log(RLD) = a + b*M     SS  -2.57(0.12) 0.62(0.02)
    #                       N   -2.42(0,21) 0.58(0.03)
    #                       R   -1.88(0,37) 0.50(0.06)
    #                       All -2.44(0.11) 0.59(0.02)
    #                        
    #log(RW) = a + b*M     SS  -0.76(0.12) 0.27(0.02)
    #                       N   -1.61(0.20) 0.41(0.03)
    #                       R   -1.14(0.28) 0.35(0.05)
    #                       All -1.01(0.10) 0.32(0.02)
    
    #sof = SOF.valueof(sof) #cast to proper type
                    
    coeffs = {"RLD":     {  SOF.STRIKE_SLIP :  (-2.57, 0.12, 0.62, 0.02),\
                            SOF.NORMAL:   (-2.42, 0.21, 0.58, 0.03),\
                            SOF.REVERSE   :   (-1.88, 0.37,  0.50, 0.06),\
                            SOF.UNKNOWN :   (-2.44, 0.11,  0.59, 0.02),
                        },\
            "RW":       {   SOF.STRIKE_SLIP  :   (-0.76, 0.12,  0.27, 0.02),\
                            SOF.NORMAL  :   ( -1.61, 0.20,  0.41, 0.03),\
                            SOF.REVERSE  :   ( -1.14, 0.28,  0.35, 0.05),\
                            SOF.UNKNOWN :   ( -1.01, 0.10,  0.32, 0.02),\
        }\
    }
    
    a_rld, b_rld, a_rw, b_rw = coeffs['RLD'][sof][0], coeffs['RLD'][sof][2], coeffs['RW'][sof][0], coeffs['RW'][sof][2] 
    
    def func(mw):
        
        return 10 ** (a_rld + b_rld * mw), 10 ** (a_rw + b_rw * mw)
    
    return func

def rup_distance_sof(lat_sta, lon_sta, lat_epi, lon_epi, depth, mw, strike_deg, dip_deg, sof):
    rld, rw = rld_rw(sof)(mw)
    return rup_distance(lat_sta, lon_sta, lat_epi, lon_epi, depth, strike_deg, dip_deg, rld, rw)

def rup_distance_slip(lat_sta, lon_sta, lat_epi, lon_epi, depth, mw, strike_deg, dip_deg, slip_deg):
    rld, rw = rld_rw(sof(slip_deg))(mw)
    return rup_distance(lat_sta, lon_sta, lat_epi, lon_epi, depth, strike_deg, dip_deg, rld, rw)

#import inspect
def rup_distance(lat_sta, lon_sta, lat_epi, lon_epi, depth, strike_deg, dip_deg, RLD, RW):
    """
        Returns the rupture distance from the sta(tion) lat and lon (in degree) and the epicentrum 
        (plus the given rupture parameters). Note that sof can be:
            1) either a style of faulting (SOF.REVERSE, SOF.NORMAL, SOF.STRIKE_SLIP, SOF.UNKNOWN after
            from gmpe_utils import SOF. These are numbers from -1000 to -100000), 
            which can also be given in string form (case insensitive, e.g. 
            "reverse", "normal" "strike_slip" or unknown")
            2) A number (not one of the style of faulting, see above), in that case it indicates 
            the slip in DEGREES), 
            3) A callback RESULTING FROM gmpes_utils.rld_rw(sof), which returns a function returning the RDL and RW parameters
            froma given magnitude. The sof argument of rld_rw can be either a string or a number (same as above). Passing a 
            function might be convenient when a style of faulting or a slip in degrees is given, for instantiationg a function once
    """

    #FOR DEBUG PURPOSES (LEAVE HERE FOR THE MOMENT):
#    frame = inspect.currentframe()
#    args, _, _, values = inspect.getargvalues(frame)

#    for i in args:

    
    two_pi = TWO_PI
    half_pi = HALF_PI
    three_half_pi = THREE_HALF_PI
   
    strike = deg2rad(strike_deg)
    dip    = deg2rad(dip_deg)
#    strike = strike_rad #d2r * strike_deg;
#    dip    = dip_rad #d2r * dip_deg;
    
    D_tor = depth - RW / 2 * sin(dip)  #Calculate the depth to Top of the Rupture
        
    
    # Calculating the Surface Fault dimension
    cos_dip = cos(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
    if D_tor > 0:
        L1 = RLD / 2
        W1 = RW / 2 * cos_dip
        W2 = W1
    else:
        tan_dip = tan(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
        L1 = RLD / 2
        W1 = depth / tan_dip
        W2 = RW * cos_dip - depth / tan_dip
    
    L2 = L1
    
    Ztor=max(D_tor,0) # Ztop = depth of top of rupture

#  Now Determine the Location of the Projected Fault Corners.
#
#                   c2-------w1-----|-------w2------------ c3
#                   |               |                       |
#                l2 |      d2       |          d3           |
#                   |               |                       |
#                   -              Epi                      -
#                   |               |                       |
#                l1 |      d1       |          d4           |
#                   |               |                       |
#                   c1-------w1-----|------ w2------------ c4
#

    Dist_C1toEpi = sqrt(L1 * L1 + W1 * W1)
    Dist_C2toEpi = sqrt(L2 * L2 + W1 * W1)
    Dist_C3toEpi = sqrt(L2 * L2 + W2 * W2)
    Dist_C4toEpi = sqrt(L1 * L1 + W2 * W2)
    
    
    
    Az_EC1 = rad2deg(mod(strike + 1 * pi + atan(W1 / L1) , two_pi))    #[mod((strike + 1 * pi + atan(W1 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner1 in degress
    Az_EC2 = rad2deg(mod(strike + 2 * pi - atan(W1 / L2) , two_pi))    #[mod((strike + 2 * pi - atan(W1 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner2 in degress
    Az_EC3 = rad2deg(mod(strike + 0 * pi + atan(W2 / L2) , two_pi))    #[mod((strike + 0 * pi + atan(W2 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner3 in degress
    Az_EC4 = rad2deg(mod(strike + 1 * pi - atan(W2 / L1) , two_pi))     #[mod((strike + 1 * pi - atan(W2 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner4 in degress

    [C1_lat, C1_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C1toEpi), Az_EC1)
    [C2_lat, C2_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C2toEpi), Az_EC2)
    [C3_lat, C3_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C3toEpi), Az_EC3)
    [C4_lat, C4_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C4toEpi), Az_EC4)

    # Now obtain Site azimuths wrt. corners and respective distance. Angles are corrected wrt strike

    Az_C1S = mod(deg2rad(azimuth(C1_lat, C1_lon, lat_sta, lon_sta)) - strike, two_pi) #mod(azimuth(C1_lat, C1_lon, lat_sta, lon_sta) * d2r - strike, two_pi)      #in radian
    Az_C2S = mod(deg2rad(azimuth(C2_lat, C2_lon, lat_sta, lon_sta)) - strike, two_pi) #mod(azimuth(C2_lat, C2_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C3S = mod(deg2rad(azimuth(C3_lat, C3_lon, lat_sta, lon_sta)) - strike, two_pi) #mod(azimuth(C3_lat, C3_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C4S = mod(deg2rad(azimuth(C4_lat, C4_lon, lat_sta, lon_sta)) - strike, two_pi) #mod(azimuth(C4_lat, C4_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    
    Dist_C1toSite = deg2km(distance(C1_lat, C1_lon, lat_sta, lon_sta))
    Dist_C2toSite = deg2km(distance(C2_lat, C2_lon, lat_sta, lon_sta))
    Dist_C3toSite = deg2km(distance(C3_lat, C3_lon, lat_sta, lon_sta))
    Dist_C4toSite = deg2km(distance(C4_lat, C4_lon, lat_sta, lon_sta))


#                           Now calculate distance metrics
#
#                (North)                            Site
#                                                     S
#                                                   
#                   |                         |
#           Reg1    |          Reg2           |    Reg3
#                   |Az_C2S                   |Az_C3S
#           ________c2-----------------------c3________
#                   |        "width"          |
#                   |                         |
#           Reg4    |          Reg5           |    Reg6
#                   |                         |
#                   |Az_C1S                   |Az_C4S
#           ________c1-----------------------c4________
#                   |                         |
#           Reg7    |          Reg8           |    Reg9
#                   |                         |
#
#
#   Repi & R_hyp & R_JB & R_CD & R_XX

    #This was used to calculate Rhyp. Leave it here might be useful (not for the moment):
    #Repi = deg2km(distance(lat_epi, lon_epi, lat_sta, lon_sta)); #Repi = epicentral distance
    #Rhyp = sqrt(Repi  **  2 + depth  **  2) # Rhyp = hypocentral distance
    
    #Now, this seems to be redundant, adn it is actually.
    #The reason why I leave it here is that in the original code there was apparently 
    #the option to giv a R_JB (R_JB_gvn), and in case in the future we want to re-implement this possibility, 
    #the code is already here. In case, ALL YOU NEED TO DO IS TO REMOVE R_JB = None BELOW AND ADD IT AS A FUNCTION 
    #ARGUMENT 
    R_JB = None
    if R_JB is None: #isempty(R_JB_gvn)
        if Az_C1S >= pi and Az_C1S < three_half_pi: 
            R_JB = Dist_C1toSite; # RJB = shortest distance from the surface projection of the fault (Joyner- Boore distance)
        elif Az_C1S >= three_half_pi:
            R_JB = Dist_C2toSite if Az_C2S > three_half_pi else Dist_C1toSite * abs(sin(Az_C1S))
        elif Az_C1S > half_pi and Az_C1S < pi:
            R_JB = Dist_C1toSite * abs(cos(Az_C1S)) if Az_C4S > pi else Dist_C4toSite
        elif Az_C1S <= half_pi and Az_C2S >= half_pi: 
            R_JB = 0 if Az_C3S >= pi else Dist_C3toSite * abs(sin(Az_C3S))
        elif Az_C1S < half_pi and Az_C2S < half_pi: 
            R_JB = Dist_C2toSite * abs(cos(Az_C2S)) if Az_C3S > half_pi else Dist_C3toSite
    
   
    if Az_C1S >= pi and Az_C1S < three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg7'
        R_XX = R_JB * sin(Az_C1S)
        R_YY = R_JB * cos(Az_C1S)
    elif Az_C1S >= three_half_pi: #(3 / 2 * pi):
        if Az_C2S > three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg1'
            R_XX = R_JB * sin(Az_C2S)
            R_YY = R_JB * cos(Az_C2S)
        else:
#                Region = 'Reg4'
            R_XX = R_JB * sin(three_half_pi) #sin(3 / 2 * pi)
            R_YY = 0
    elif Az_C1S > half_pi and Az_C1S < pi: #Az_C1S > (1 / 2 * pi) and Az_C1S < pi:
        if Az_C4S > pi: 
#                Region = 'Reg8'
            R_XX = R_JB * abs(tan(Az_C1S))
            R_YY = R_JB
        else:
#                Region = 'Reg9'
            R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C4S))
            R_YY = R_JB * cos(Az_C4S)
    elif Az_C1S <= half_pi and Az_C2S >= half_pi: #Az_C1S <= (1 / 2 * pi) and Az_C2S >= (1 / 2 * pi):
        if Az_C3S >= pi:
#                Region = 'Reg5'
            R_XX = Dist_C2toSite * abs(sin(Az_C2S))
            R_YY = 0
        else:
#                Region = 'Reg6'
            R_XX = RW * cos(dip) + R_JB
            R_YY = 0
    elif Az_C1S < half_pi and Az_C2S < half_pi: #Az_C1S < (1 / 2 * pi) and Az_C2S < (1 / 2 * pi):
        if Az_C3S > half_pi: #(1 / 2 * pi):
#                Region = 'Reg2'
            R_XX = R_JB * abs(tan(Az_C2S))
            R_YY = R_JB
        else:
#                Region = 'Reg3'
            R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C3S))
            R_YY = R_JB * cos(Az_C3S)
    
    R_YY=abs(R_YY);
    
    if dip_deg==90:
        Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2);
    else:
        if R_XX < (Ztor * tan(dip)):
            Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2)
        elif R_XX >= Ztor*tan(dip) and  R_XX <= Ztor*tan(dip) + RW/cos(dip):
            Rrup_prime = R_XX*sin(dip) + Ztor*cos(dip)
        else:
            Rrup_prime = sqrt((R_XX - RW*cos(dip)) ** 2 + (Ztor + RW*sin(dip)) ** 2)
    
    R_CD = sqrt(Rrup_prime ** 2 + R_YY ** 2) #R_CD = rupture distance 
    




    
    return R_CD

    #return (Ztor, HW_Flag, Repi, Rhyp, R_JB, R_CD, R_XX, C1_lat, C1_lon, C2_lat, C2_lon, C3_lat, C3_lon, C4_lat, C4_lon)
    


def reckon(lat, lon, arclen, az): #[latout,lonout] = reckon(varargin)
    """
        Calculates and returns the tuple (LATOUT, LONOUT) denoting the position 
        at a given range, arclen, and azimuth, az, along a great circle arc from 
        a starting point defined by lat and lon (both are in degrees). 
        arclen must be expressed as degrees of arc on a sphere, and equals the 
        length of a great circle arc connecting the point (lat, lon) to the point 
        (LATOUT, LONOUT). 
        az, also in degrees, is measured clockwise from north.
    """
    
    #redefining matlab parseInputs in reckon.m, basically converting to radiants (reckon.m line 72) 
    lat = deg2rad(lat)
    lon = deg2rad(lon)
    rng = deg2rad(arclen)
    az = deg2rad(az)
        
    #[newlat, newlon] = greatcirclefwd(lat,lon,az,rng,1)
    newlat, newlon = _greatcirclefwd(lat,lon,az,rng)
    
    
    newlon = pi*((abs(newlon)/pi) - 2 * ceil(((abs(newlon)/pi)-1)/2)) * sign(newlon) #npi2pi(newlon,'radians')
    return (rad2deg(newlat), rad2deg(newlon))

#def sign(number): #not defined in python (!!??!!)
#    """
#        Signum of a number (no, it is not implemented in Python math...) 
#        Along the lines of Matlab sign function, returns:
#          1 if number is positive (including positive infinity), 
#         -1 if number is negative (including negative infinity), 
#        NaN if number is NaN (returns a value for which math.isnan(value) is True)
#          0 in any other case
#    """
#    return 1 if number>0 else (-1 if number<0 else (float('nan') if isnan(number) else 0))



#    if number>0:
#        return 1
#    elif number<0:
#        return -1
#    return 0

def _greatcirclefwd(phi0, lambda0, az, rng): #function [phi,lambda] = greatcirclefwd(phi0, lambda0, az, rng, r)
    """    
        On a sphere of radius A, compute points on a great circle at specified
        azimuths and ranges.  PHI, LAMBDA, PHI0, LAMBDA0, and AZ are angles in
        radians, and RNG is a distance having the same units as the sphere radius.
    """

    # Convert the range to an angle on the sphere (in radians).
    #rng = rng / r #r(1);

    # Ensure correct azimuths at either pole.
    epsilon = 10 * deg2rad(1.0E-6) #10*epsm('radians');    # Set tolerance
    half_pi = HALF_PI
    if phi0 >= half_pi - epsilon:
        az = pi
    if phi0 <= epsilon-half_pi:
        az = 0
    
#    az(phi0 >= pi/2-epsilon) = pi;    # starting at north pole
#    az(phi0 <= epsilon-pi/2) = 0;     # starting at south pole

    #Calculate coordinates of great circle end point using spherical trig.
    phi = asin( sin(phi0) * cos(rng) + cos(phi0) * sin(rng) * cos(az) ) #phi = asin( sin(phi0).*cos(rng) + cos(phi0).*sin(rng).*cos(az) );

#    lambda_ = lambda0 + atan2( sin(rng).*sin(az),...
#                      cos(phi0).*cos(rng) - sin(phi0).*sin(rng).*cos(az) );
    lambda_ = lambda0 + atan2( sin(rng) * sin(az),\
            cos(phi0) * cos(rng) - sin(phi0) * sin(rng) * cos(az) );
    
    return (phi, lambda_)

def deg2km(deg):
    """
        Converts distances from degrees to kilometers as
        measured along a great circle on a sphere with a radius of 6371 km (EARTH_RADIUS), the
        mean radius of the Earth.
    """
    rad = deg2rad(deg);
    return rad2km(rad)

def km2deg(km):
    """
        Converts distances from kilometers to degrees as
        measured along a great circle on a sphere with a radius of 6371 km (EARTH_RADIUS), the
        mean radius of the Earth.
    """
    rad = km2rad(km);
    return rad2deg(rad);

def rad2km(rad):
    """
        Converts distances from radians to kilometers as
        measured along a great circle on a sphere with a radius of 6371 km (EARTH_RADIUS), the
        mean radius of the Earth.
    """
    return rad * EARTH_RADIUS

def km2rad(km):
    """
        Converts distances from kilometers to radians as
        measured along a great circle on a sphere with a radius of 6371 km (EARTH_RADIUS), the
        mean radius of the Earth.
    """
    return km / EARTH_RADIUS

#def deg2rad(angleInDegrees):
#    """
#        Converts angle units from degrees to radians.
#    """
#    return  (pi/180) * angleInDegrees
#
#def rad2deg(angleInRadians):
#    """
#        Converts angles from radians to degrees
#    """
#    return (180/pi) * angleInRadians;

def chorddistance(lat1, lon1, lat2, lon2):
    """
        Computes and returns the length, in kilometers, of the chord 
        whose endpoints are P1=[lat1, lon1] and P2=[lat2, lon2] of the great circle 
        passing for P1 and P2.
        The input latitudes and longitudes, LAT1, LON1, LAT2, LON2 must be 
        expressed in degrees
    """
    rad = greatcircledist(deg2rad(lat1), deg2rad(lon1), deg2rad(lat2), deg2rad(lon2)) #in radians
    r= EARTH_RADIUS
    return r * sqrt(2*(1-cos(rad)))
    
def distance(lat1, lon1, lat2, lon2):
    """
        Computes and returns the length,
        ARCLEN, of the great circle arcs connecting pairs of points on the
        surface of a sphere. In each case, the shorter (minor) arc is assumed.
        The input latitudes and longitudes, LAT1, LON1, LAT2, LON2 must be 
        expressed in degrees. ARCLEN is also expressed in degrees
    """
    
    #rng = greatcircledist(deg2rad(lat1), deg2rad(lon1), deg2rad(lat2), deg2rad(lon2), 1)
    rng = greatcircledist(deg2rad(lat1), deg2rad(lon1), deg2rad(lat2), deg2rad(lon2))
    
    #az = greatcircleaz(lat1, lon1, lat2, lon2)
    rng = rad2deg(rng) #fromRadians(units, rng);
    return rng

def greatcircledist(lat1, lon1, lat2, lon2): #greatcircledist(lat1, lon1, lat2, lon2, r):
    """
        Calculates the great circle distance between points on a sphere using the
        Haversine Formula.  LAT1, LON1, LAT2, and LON2 are in radians.  The returned 
        value RNG is a length and is expressed in radians.
    """
#    a = sin((lat2-lat1)/2).^2 + cos(lat1) .* cos(lat2) .* sin((lon2-lon1)/2).^2
    a = sin((lat2-lat1)/2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2) ** 2
    return 2 * atan2(sqrt(a),sqrt(1 - a)) # r * 2 * atan2(sqrt(a),sqrt(1 - a))

def azimuth(lat1, lon1, lat2, lon2):
    """
        Computes and returns the great circle bearing AZ,
        the azimuth from point 1 to point 2, for pairs of points on the surface
        of a sphere.  The input latitudes and longitudes, LAT1, LON1, LAT2,
        LON2, are expressed in degrees.  The returned azimuth is also 
        expressed in degrees clockwise from north, ranging from 0 to 360.
    """
    #az = greatcircleaz(lat1, lon1, lat2, lon2)
    az = greatcircleaz(deg2rad(lat1), deg2rad(lon1), deg2rad(lat2), deg2rad(lon2))
    
    
    # Ensure azimuth in the range [0 2*pi).
    #az = az % TWO_PI;
    az = mod(az , TWO_PI);
    
    az = rad2deg(az) #fromRadians(units,az);
    return az

def greatcircleaz(lat1,lon1,lat2,lon2):
    """
        Computes the great circle bearing AZ,
        the azimuth from point 1 to point 2, for pairs of points on the surface
        of a sphere.  The input latitudes and longitudes, LAT1, LON1, LAT2,
        LON2, are expressed in radians.  The returned azimuth is also 
        expressed in radians clockwise from north, ranging from 0 to 360.
    """
    # Inputs LAT1, LON1, LAT2, LON2 are in units of radians.

#    az = atan2(cos(lat2) .* sin(lon2-lon1),\
#        cos(lat1) .* sin(lat2) - sin(lat1) .* cos(lat2) .* cos(lon2-lon1));
    
    az = atan2(cos(lat2) * sin(lon2-lon1), cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2-lon1))
        
    # Azimuths are undefined at the poles, so we choose a convention: zero at
    # the north pole and pi at the south pole.
    half_pi = HALF_PI;
    if lat1 <= -half_pi or lat2 >= half_pi:
        az = 0
    
    if lat1 >=half_pi or lat2 <= -half_pi:
        az = pi
    
    return az

#az(lat1 <= -pi/2) = 0;
#az(lat2 >=  pi/2) = 0;
#az(lat2 <= -pi/2) = pi;
#az(lat1 >=  pi/2) = pi;

#OLD FUNCTION (ORIGINALLY COPIED FROM DINO'S MATLAB CODE). TO BE REMOVED IN FUTURE
def _calc_distance_metrics(lat_sta, lon_sta, lat_epi, lon_epi, depth, mw, strike_deg, dip_deg, slip_deg,\
                                R_JB=None, D_tor=None, RLD=None, RW=None, W1=None, W2=None, L1=None, L2=None):
    """
        Doc to be added...
    """

#Note: leave matlab function commented when needed so that changes can be 
#easily made (hopefully)

#ResultFile=fopen(ResultFileName,'wt');
#fprintf(ResultFile,'%s\n','RecordNo;SOF;FD_flag;Ztor;Ztor_flag;HW_Flag;Repi;Rhyp;R_JB;R_CD;R_XX;C1_lat;C1_lon;C2_lat;C2_lon;C3_lat;C3_lon;C4_lat;C4_lon');

#InputFile=fopen(InputFileName,'r');
#%junk=fgetl(InputFile);
    
    #pi = math.pi
    two_pi = 2 * pi
    half_pi = pi/2
    three_half_pi = 3 * pi / 2
    
    #d2r = pi / 180;
    #r2d = 180 / pi;

#while feof(InputFile)~=1
    
    #InputData_str=fgetl(InputFile);  # Reading the input parameters
    #semicolon_mtrx=findstr(InputData_str,';');
    
    #RecordNo  = str2double(InputData_str(                      1:(semicolon_mtrx(1,1)-1)));
#    lat_sta   = str2double(InputData_str((semicolon_mtrx(1,1)+1):(semicolon_mtrx(1,2)-1)));
#    lon_sta   = str2double(InputData_str((semicolon_mtrx(1,2)+1):(semicolon_mtrx(1,3)-1)));
#    lat_epi   = str2double(InputData_str((semicolon_mtrx(1,3)+1):(semicolon_mtrx(1,4)-1)));
#    lon_epi   = str2double(InputData_str((semicolon_mtrx(1,4)+1):(semicolon_mtrx(1,5)-1)));
#    depth     = str2double(InputData_str((semicolon_mtrx(1,5)+1):(semicolon_mtrx(1,6)-1)));
#    mw        = str2double(InputData_str((semicolon_mtrx(1,6)+1):(semicolon_mtrx(1,7)-1)));
#    strike_deg = str2double(InputData_str((semicolon_mtrx(1,7)+1):(semicolon_mtrx(1,8)-1)));
#    dip_deg    = str2double(InputData_str((semicolon_mtrx(1,8)+1):(semicolon_mtrx(1,9)-1)));
#    slip_deg   = str2double(InputData_str((semicolon_mtrx(1,9)+1):(semicolon_mtrx(1,10)-1)));
#    R_JB_gvn  =            InputData_str((semicolon_mtrx(1,10)+1):(semicolon_mtrx(1,11)-1));
#    D_tor_gvn =            InputData_str((semicolon_mtrx(1,11)+1):(semicolon_mtrx(1,12)-1));
#    RDL       =            InputData_str((semicolon_mtrx(1,12)+1):(semicolon_mtrx(1,13)-1));
#    RW        =            InputData_str((semicolon_mtrx(1,13)+1):(semicolon_mtrx(1,14)-1));
#    W1        =           InputData_str((semicolon_mtrx(1,14)+1):(semicolon_mtrx(1,15)-1));
#    W2        =           InputData_str((semicolon_mtrx(1,15)+1):(semicolon_mtrx(1,16)-1));
#    L1        =           InputData_str((semicolon_mtrx(1,16)+1):(semicolon_mtrx(1,17)-1));
#    L2        =           InputData_str((semicolon_mtrx(1,17)+1):end);
    

    strike = deg2rad(strike_deg) #d2r * strike_deg;
    dip    = deg2rad(dip_deg) #d2r * dip_deg;
    
#    if slip_deg >= -150 and slip_deg <= -30:     #Determine the style-of-faulting (SOF)
#        SOF = 'Normal'
#    elif slip_deg >= 30 and slip_deg <= 150:
#        SOF = 'Reverse'
#    else:
#        SOF = 'strike-Slip'
    styile_of_faulting = sof(slip_deg)
    
    FD_flag=0
    if RLD is None or RW is None:        # Calculating the Fault dimension
        RLD= 10 ** (-2.44 + 0.59 * mw)
        RW = 10 ** (-1.01 + 0.32 * mw)
#        FD_flag=1
#    else
#        RDL=str2double(RDL)
#        RW =str2double(RW)
#        FD_flag=0

    D_tor_flag=0
    if D_tor is None:
        D_tor = depth - RW / 2 * sin(dip)  #Calculate the depth to Top of the Rupture
        D_tor_flag=1
    
    if W1 is None or W2 is None or L1 is None or L2 is None:       # Calculating the Surface Fault dimension
        cos_dip = cos(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
        if D_tor > 0:
            L1 = RLD / 2
            L2 = RLD / 2
            W1 = RW / 2 * cos_dip
            W2 = RW / 2 * cos_dip
        else:
            tan_dip = tan(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
            L1 = RLD / 2
            L2 = RLD / 2
            W1 = depth / tan_dip
            W2 = RW * cos_dip - depth / tan_dip
#    else
#        W1=str2double(W1)
#        W2=str2double(W2)
#        L1=str2double(L1)
#        L2=str2double(L2)
    
    Ztor=max(D_tor,0) # Ztop = depth of top of rupture

#  Now Determine the Location of the Projected Fault Corners.
#
#                   c2-------w1-----|-------w2------------ c3
#                   |               |                       |
#                l2 |      d2       |          d3           |
#                   |               |                       |
#                   -              Epi                      -
#                   |               |                       |
#                l1 |      d1       |          d4           |
#                   |               |                       |
#                   c1-------w1-----|------ w2------------ c4
#

    Dist_C1toEpi = sqrt(L1 * L1 + W1 * W1)
    Dist_C2toEpi = sqrt(L2 * L2 + W1 * W1)
    Dist_C3toEpi = sqrt(L2 * L2 + W2 * W2)
    Dist_C4toEpi = sqrt(L1 * L1 + W2 * W2)

    
    Az_EC1 = rad2deg((strike + 1 * pi + atan(W1 / L1)) % two_pi)     #[mod((strike + 1 * pi + atan(W1 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner1 in degress
    Az_EC2 = rad2deg((strike + 2 * pi - atan(W1 / L2)) % two_pi)     #[mod((strike + 2 * pi - atan(W1 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner2 in degress
    Az_EC3 = rad2deg((strike + 0 * pi + atan(W2 / L2)) % two_pi)     #[mod((strike + 0 * pi + atan(W2 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner3 in degress
    Az_EC4 = rad2deg((strike + 1 * pi - atan(W2 / L1)) % two_pi)     #[mod((strike + 1 * pi - atan(W2 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner4 in degress

    [C1_lat, C1_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C1toEpi), Az_EC1)
    [C2_lat, C2_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C2toEpi), Az_EC2)
    [C3_lat, C3_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C3toEpi), Az_EC3)
    [C4_lat, C4_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C4toEpi), Az_EC4)

    # Now obtain Site azimuths wrt. corners and respective distance. Angles are corrected wrt strike

    Az_C1S = (deg2rad(azimuth(C1_lat, C1_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C1_lat, C1_lon, lat_sta, lon_sta) * d2r - strike, two_pi)      #in radian
    Az_C2S = (deg2rad(azimuth(C2_lat, C2_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C2_lat, C2_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C3S = (deg2rad(azimuth(C3_lat, C3_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C3_lat, C3_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C4S = (deg2rad(azimuth(C4_lat, C4_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C4_lat, C4_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    
    Dist_C1toSite = deg2km(distance(C1_lat, C1_lon, lat_sta, lon_sta))
    Dist_C2toSite = deg2km(distance(C2_lat, C2_lon, lat_sta, lon_sta))
    Dist_C3toSite = deg2km(distance(C3_lat, C3_lon, lat_sta, lon_sta))
    Dist_C4toSite = deg2km(distance(C4_lat, C4_lon, lat_sta, lon_sta))

    if Az_C1S > pi and Az_C1S < two_pi:      #   HW_Flag  (HW=1), (FW=0) HW = Hanging Wall
        HW_Flag = 0
    else:
        HW_Flag = 1

#                           Now calculate distance metrics
#
#                (North)                            Site
#                                                     S
#                                                   
#                   |                         |
#           Reg1    |          Reg2           |    Reg3
#                   |Az_C2S                   |Az_C3S
#           ________c2-----------------------c3________
#                   |        "width"          |
#                   |                         |
#           Reg4    |          Reg5           |    Reg6
#                   |                         |
#                   |Az_C1S                   |Az_C4S
#           ________c1-----------------------c4________
#                   |                         |
#           Reg7    |          Reg8           |    Reg9
#                   |                         |
#
#
#   Repi & R_hyp & R_JB & R_CD & R_XX

    Repi = deg2km(distance(lat_epi, lon_epi, lat_sta, lon_sta)); #Repi = epicentral distance
    Rhyp = sqrt(Repi  **  2 + depth  **  2) # Rhyp = hypocentral distance
    
    if R_JB is None: #isempty(R_JB_gvn)
        if Az_C1S >= pi and Az_C1S < three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg7';
            R_JB = Dist_C1toSite; # RJB = shortest distance from the surface projection of the fault (Joyner- Boore distance)
            R_XX = R_JB * sin(Az_C1S); # R_XX shortest perpendicular distance from the surface projection of the fault (fault strike)
            R_YY = R_JB * cos(Az_C1S); # R_YY shortest distance along the fault strike (0 if the point is inside the fault or region 4 and 6)
                                           # Rjb if in region 2 and 8)
        elif Az_C1S >= three_half_pi: #(3 / 2 * pi):
            if Az_C2S > three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg1'
                R_JB = Dist_C2toSite
                R_XX = R_JB * sin(Az_C2S)
                R_YY = R_JB * cos(Az_C2S)
            else:
#                Region = 'Reg4'
                R_JB = Dist_C1toSite * abs(sin(Az_C1S))
                R_XX = R_JB * sin(three_half_pi) #sin(3 / 2 * pi)
                R_YY = 0
        elif Az_C1S > half_pi and Az_C1S < pi: #Az_C1S > (1 / 2 * pi) and Az_C1S < pi:
            if Az_C4S > pi: 
#                Region = 'Reg8'
                R_JB = Dist_C1toSite * abs(cos(Az_C1S))
                R_XX = R_JB * abs(tan(Az_C1S))
                R_YY = R_JB
            else:
#                Region = 'Reg9'
                R_JB = Dist_C4toSite
                R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C4S))
                R_YY = R_JB * cos(Az_C4S)
        elif Az_C1S <= half_pi and Az_C2S >= half_pi: #Az_C1S <= (1 / 2 * pi) and Az_C2S >= (1 / 2 * pi):
            if Az_C3S >= pi:
#                Region = 'Reg5'
                R_JB = 0
                R_XX = Dist_C2toSite * abs(sin(Az_C2S))
                R_YY = 0
            else:
#                Region = 'Reg6'
                R_JB = Dist_C3toSite * abs(sin(Az_C3S))
                R_XX = RW * cos(dip) + R_JB
                R_YY = 0
        elif Az_C1S < half_pi and Az_C2S < half_pi: #Az_C1S < (1 / 2 * pi) and Az_C2S < (1 / 2 * pi):
            if Az_C3S > half_pi: #(1 / 2 * pi):
#                Region = 'Reg2'
                R_JB = Dist_C2toSite * abs(cos(Az_C2S))
                R_XX = R_JB * abs(tan(Az_C2S))
                R_YY = R_JB
            else:
#                Region = 'Reg3'
                R_JB = Dist_C3toSite
                R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C3S))
                R_YY = R_JB * cos(Az_C3S)
    else:
        #R_JB=str2double(R_JB_gvn);
        if Az_C1S >= pi and Az_C1S < three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg7'
            R_XX = R_JB * sin(Az_C1S)
            R_YY = R_JB * cos(Az_C1S)
        elif Az_C1S >= three_half_pi: #(3 / 2 * pi):
            if Az_C2S > three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg1'
                R_XX = R_JB * sin(Az_C2S)
                R_YY = R_JB * cos(Az_C2S)
            else:
#                Region = 'Reg4'
                R_XX = R_JB * sin(three_half_pi) #sin(3 / 2 * pi)
                R_YY = 0
        elif Az_C1S > half_pi and Az_C1S < pi: #Az_C1S > (1 / 2 * pi) and Az_C1S < pi:
            if Az_C4S > pi: 
#                Region = 'Reg8'
                R_XX = R_JB * abs(tan(Az_C1S))
                R_YY = R_JB
            else:
#                Region = 'Reg9'
                R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C4S))
                R_YY = R_JB * cos(Az_C4S)
        elif Az_C1S <= half_pi and Az_C2S >= half_pi: #Az_C1S <= (1 / 2 * pi) and Az_C2S >= (1 / 2 * pi):
            if Az_C3S >= pi:
#                Region = 'Reg5'
                R_XX = Dist_C2toSite * abs(sin(Az_C2S))
                R_YY = 0
            else:
#                Region = 'Reg6'
                R_XX = RW * cos(dip) + R_JB
                R_YY = 0
        elif Az_C1S < half_pi and Az_C2S < half_pi: #Az_C1S < (1 / 2 * pi) and Az_C2S < (1 / 2 * pi):
            if Az_C3S > half_pi: #(1 / 2 * pi):
#                Region = 'Reg2'
                R_XX = R_JB * abs(tan(Az_C2S))
                R_YY = R_JB
            else:
#                Region = 'Reg3'
                R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C3S))
                R_YY = R_JB * cos(Az_C3S)
    
    R_YY=abs(R_YY);
    
    if dip_deg==90:
        Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2);
    else:
        if R_XX < (Ztor * tan(dip)):
            Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2)
        elif R_XX >= Ztor*tan(dip) and  R_XX <= Ztor*tan(dip) + RW/cos(dip):
            Rrup_prime = R_XX*sin(dip) + Ztor*cos(dip)
        else:
            Rrup_prime = sqrt((R_XX - RW*cos(dip)) ** 2 + (Ztor + RW*sin(dip)) ** 2)
    
    R_CD = sqrt(Rrup_prime ** 2 + R_YY ** 2) #R_CD = rupture distance 
    
    return (styile_of_faulting, FD_flag, Ztor, D_tor_flag, HW_Flag, Repi, Rhyp, R_JB, R_CD, R_XX, C1_lat, C1_lon, C2_lat, C2_lon, C3_lat, C3_lon, C4_lat, C4_lon)
    

#DEPRECATED! WILL BE REMOVED!!!
def _rup_distance(lat_sta, lon_sta, lat_epi, lon_epi, depth, mw, strike_deg, dip_deg, sof):
    """
        Returns the rupture distance from the sta(tion) lat and lon (in degree) and the epicentrum 
        (plus the given rupture parameters). Note that sof can be:
            1) either a style of faulting (SOF.REVERSE, SOF.NORMAL, SOF.STRIKE_SLIP, SOF.UNKNOWN after
            from gmpe_utils import SOF. These are numbers from -1000 to -100000), 
            which can also be given in string form (case insensitive, e.g. 
            "reverse", "normal" "strike_slip" or unknown")
            2) A number (not one of the style of faulting, see above), in that case it indicates 
            the slip in DEGREES), 
            3) A callback RESULTING FROM gmpes_utils.rld_rw(sof), which returns a function returning the RDL and RW parameters
            froma given magnitude. The sof argument of rld_rw can be either a string or a number (same as above). Passing a 
            function might be convenient when a style of faulting or a slip in degrees is given, for instantiationg a function once
    """

    
    two_pi = TWO_PI
    half_pi = HALF_PI
    three_half_pi = THREE_HALF_PI
   

    strike = deg2rad(strike_deg) #d2r * strike_deg;
    dip    = deg2rad(dip_deg) #d2r * dip_deg;

    rld_rw_func = sof if hasattr(sof, "__call__") else rld_rw(sof)
    RLD, RW = rld_rw_func(mw)
    
    D_tor = depth - RW / 2 * sin(dip)  #Calculate the depth to Top of the Rupture
        
    
    # Calculating the Surface Fault dimension
    cos_dip = cos(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
    if D_tor > 0:
        L1 = RLD / 2
        L2 = RLD / 2
        W1 = RW / 2 * cos_dip
        W2 = RW / 2 * cos_dip
    else:
        tan_dip = tan(dip) #calculate once for optimization (more for styling, performance boost is in most cases probably negligible)
        L1 = RLD / 2
        L2 = RLD / 2
        W1 = depth / tan_dip
        W2 = RW * cos_dip - depth / tan_dip

    
    Ztor=max(D_tor,0) # Ztop = depth of top of rupture

#  Now Determine the Location of the Projected Fault Corners.
#
#                   c2-------w1-----|-------w2------------ c3
#                   |               |                       |
#                l2 |      d2       |          d3           |
#                   |               |                       |
#                   -              Epi                      -
#                   |               |                       |
#                l1 |      d1       |          d4           |
#                   |               |                       |
#                   c1-------w1-----|------ w2------------ c4
#

    Dist_C1toEpi = sqrt(L1 * L1 + W1 * W1)
    Dist_C2toEpi = sqrt(L2 * L2 + W1 * W1)
    Dist_C3toEpi = sqrt(L2 * L2 + W2 * W2)
    Dist_C4toEpi = sqrt(L1 * L1 + W2 * W2)

    
    Az_EC1 = rad2deg((strike + 1 * pi + atan(W1 / L1)) % two_pi)     #[mod((strike + 1 * pi + atan(W1 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner1 in degress
    Az_EC2 = rad2deg((strike + 2 * pi - atan(W1 / L2)) % two_pi)     #[mod((strike + 2 * pi - atan(W1 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner2 in degress
    Az_EC3 = rad2deg((strike + 0 * pi + atan(W2 / L2)) % two_pi)     #[mod((strike + 0 * pi + atan(W2 / L2)), two_pi)] * r2d     # Azimuth of Epicenter to Corner3 in degress
    Az_EC4 = rad2deg((strike + 1 * pi - atan(W2 / L1)) % two_pi)     #[mod((strike + 1 * pi - atan(W2 / L1)), two_pi)] * r2d     # Azimuth of Epicenter to Corner4 in degress

    [C1_lat, C1_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C1toEpi), Az_EC1)
    [C2_lat, C2_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C2toEpi), Az_EC2)
    [C3_lat, C3_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C3toEpi), Az_EC3)
    [C4_lat, C4_lon] = reckon(lat_epi, lon_epi, km2deg(Dist_C4toEpi), Az_EC4)

    # Now obtain Site azimuths wrt. corners and respective distance. Angles are corrected wrt strike

    Az_C1S = (deg2rad(azimuth(C1_lat, C1_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C1_lat, C1_lon, lat_sta, lon_sta) * d2r - strike, two_pi)      #in radian
    Az_C2S = (deg2rad(azimuth(C2_lat, C2_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C2_lat, C2_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C3S = (deg2rad(azimuth(C3_lat, C3_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C3_lat, C3_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    Az_C4S = (deg2rad(azimuth(C4_lat, C4_lon, lat_sta, lon_sta)) - strike) % two_pi #mod(azimuth(C4_lat, C4_lon, lat_sta, lon_sta) * d2r - strike, two_pi)
    
    Dist_C1toSite = deg2km(distance(C1_lat, C1_lon, lat_sta, lon_sta))
    Dist_C2toSite = deg2km(distance(C2_lat, C2_lon, lat_sta, lon_sta))
    Dist_C3toSite = deg2km(distance(C3_lat, C3_lon, lat_sta, lon_sta))
    Dist_C4toSite = deg2km(distance(C4_lat, C4_lon, lat_sta, lon_sta))

    if Az_C1S > pi and Az_C1S < two_pi:      #   HW_Flag  (HW=1), (FW=0) HW = Hanging Wall
        HW_Flag = 0
    else:
        HW_Flag = 1

#                           Now calculate distance metrics
#
#                (North)                            Site
#                                                     S
#                                                   
#                   |                         |
#           Reg1    |          Reg2           |    Reg3
#                   |Az_C2S                   |Az_C3S
#           ________c2-----------------------c3________
#                   |        "width"          |
#                   |                         |
#           Reg4    |          Reg5           |    Reg6
#                   |                         |
#                   |Az_C1S                   |Az_C4S
#           ________c1-----------------------c4________
#                   |                         |
#           Reg7    |          Reg8           |    Reg9
#                   |                         |
#
#
#   Repi & R_hyp & R_JB & R_CD & R_XX

    Repi = deg2km(distance(lat_epi, lon_epi, lat_sta, lon_sta)); #Repi = epicentral distance
    Rhyp = sqrt(Repi  **  2 + depth  **  2) # Rhyp = hypocentral distance
    
    #Now, this seems to be redundant, adn it is actually.
    #The reason why I leave it here is that in the original code there was apparently 
    #the option to giv a R_JB (R_JB_gvn), and in case in the future we want to re-implement this possibility, 
    #the code is already here. In case, ALL YOU NEED TO DO IS TO REMOVE R_JB = None BELOW AND ADD IT AS A FUNCTION 
    #ARGUMENT 
    R_JB = None
    if R_JB is None: #isempty(R_JB_gvn)
        if Az_C1S >= pi and Az_C1S < three_half_pi: 
            R_JB = Dist_C1toSite; # RJB = shortest distance from the surface projection of the fault (Joyner- Boore distance)
        elif Az_C1S >= three_half_pi:
            R_JB = Dist_C2toSite if Az_C2S > three_half_pi else Dist_C1toSite * abs(sin(Az_C1S))
        elif Az_C1S > half_pi and Az_C1S < pi:
            R_JB = Dist_C1toSite * abs(cos(Az_C1S)) if Az_C4S > pi else Dist_C4toSite
        elif Az_C1S <= half_pi and Az_C2S >= half_pi: 
            R_JB = 0 if Az_C3S >= pi else Dist_C3toSite * abs(sin(Az_C3S))
        elif Az_C1S < half_pi and Az_C2S < half_pi: 
            R_JB = Dist_C2toSite * abs(cos(Az_C2S)) if Az_C3S > half_pi else Dist_C3toSite
    
   
    if Az_C1S >= pi and Az_C1S < three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg7'
        R_XX = R_JB * sin(Az_C1S)
        R_YY = R_JB * cos(Az_C1S)
    elif Az_C1S >= three_half_pi: #(3 / 2 * pi):
        if Az_C2S > three_half_pi: #(3 / 2 * pi):
#                Region = 'Reg1'
            R_XX = R_JB * sin(Az_C2S)
            R_YY = R_JB * cos(Az_C2S)
        else:
#                Region = 'Reg4'
            R_XX = R_JB * sin(three_half_pi) #sin(3 / 2 * pi)
            R_YY = 0
    elif Az_C1S > half_pi and Az_C1S < pi: #Az_C1S > (1 / 2 * pi) and Az_C1S < pi:
        if Az_C4S > pi: 
#                Region = 'Reg8'
            R_XX = R_JB * abs(tan(Az_C1S))
            R_YY = R_JB
        else:
#                Region = 'Reg9'
            R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C4S))
            R_YY = R_JB * cos(Az_C4S)
    elif Az_C1S <= half_pi and Az_C2S >= half_pi: #Az_C1S <= (1 / 2 * pi) and Az_C2S >= (1 / 2 * pi):
        if Az_C3S >= pi:
#                Region = 'Reg5'
            R_XX = Dist_C2toSite * abs(sin(Az_C2S))
            R_YY = 0
        else:
#                Region = 'Reg6'
            R_XX = RW * cos(dip) + R_JB
            R_YY = 0
    elif Az_C1S < half_pi and Az_C2S < half_pi: #Az_C1S < (1 / 2 * pi) and Az_C2S < (1 / 2 * pi):
        if Az_C3S > half_pi: #(1 / 2 * pi):
#                Region = 'Reg2'
            R_XX = R_JB * abs(tan(Az_C2S))
            R_YY = R_JB
        else:
#                Region = 'Reg3'
            R_XX = RW * cos(dip) + R_JB * abs(sin(Az_C3S))
            R_YY = R_JB * cos(Az_C3S)
    
    R_YY=abs(R_YY);
    
    if dip_deg==90:
        Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2);
    else:
        if R_XX < (Ztor * tan(dip)):
            Rrup_prime = sqrt(R_XX ** 2 + Ztor ** 2)
        elif R_XX >= Ztor*tan(dip) and  R_XX <= Ztor*tan(dip) + RW/cos(dip):
            Rrup_prime = R_XX*sin(dip) + Ztor*cos(dip)
        else:
            Rrup_prime = sqrt((R_XX - RW*cos(dip)) ** 2 + (Ztor + RW*sin(dip)) ** 2)
    
    R_CD = sqrt(Rrup_prime ** 2 + R_YY ** 2) #R_CD = rupture distance 
    
    return R_CD




if __name__ == "__main__":
    quit()
#     
#     for v in SOF.__dict__:
#         print str(v)+": "+str(SOF.__dict__[v])+" "+str(type(SOF.__dict__[v]))
#     
#     quit()
#     #TEST CODE (TO CHECK CONSISTENCY WITH DINO MATLAB FILE)
#     numbers = [0,1.1,-1.2,float('inf'),-float('inf'),float('nan')]
#     for n in numbers:
#         print str(n)+" sign: " +str(sign(n))
#     
#     test = False
#     argv = ('/home/riccardo/Documents/lavoro/gfz/dino_dim_estimator/inputchile.txt', '/home/riccardo/Documents/lavoro/gfz/dino_dim_estimator/outputchile.py.txt')
#     if not test:
#         import sys
#         argz = argv #sys.argv
#         if len(argz) !=2:
#             print " excpected two arguments: infile outfile"
#             sys.exit()
# 
#         f = open(argz[0], 'r')
#         k = f.readline()
#         fo = open(argz[1], 'w')
# #        fo.write('%s' % 'RecordNo;SOF;FD_flag;Ztor;Ztor_flag;HW_Flag;Repi;Rhyp;R_JB;R_CD;R_XX;C1_lat;C1_lon;C2_lat;C2_lon;C3_lat;C3_lon;C4_lat;C4_lon')
#         fo.write('%s' % 'FD_flag;Ztor;Ztor_flag;HW_Flag;Repi;Rhyp;R_JB;R_CD;R_XX;C1_lat;C1_lon;C2_lat;C2_lon;C3_lat;C3_lon;C4_lat;C4_lon')
#         try:
#             while k:
#                 #parse, do stuff
#                 varz = k.split(';')
#                 varz_n=[];
#                 first = True
#                 for v in varz:
#                     if first:
#                         first = False
#                         continue
#                     if v:
#                         varz_n.append(float(v))
#                     else:
#                         varz_n.append(None)
#                 res = calc_distance_metrics(*varz_n)
#                 prevchar='\n'
#                 for r in res:
#                     fo.write("%s%s" % (prevchar, str(r)))
#                     prevchar=';'
#                 k = f.readline()
#         except:
#             traceback.print_exc(file=output)
#         
#         fo.close()
#         f.close()
# 
#     else:
#     #azimuth(120, 0, 120, 60)
#         reckon(0,0,60,60)
#         step = 60
#         steps = 360/step
#         start=0
#         #lat1=lat2=lon1=lon2=0
#         for i in range(steps):
#             lat1 = start + i*step
#             for j in range(steps):
#                 lat2 = start + j*step
#                 for k in range(steps):
#                     lon1 = start + k*step
#                     for v in range(steps):
#                         lon2 = start + v*step;
#                         
# 
#                         (latout, lonout) = reckon(lat1, lon1, lat2, lon2)
#                         print "[lat1="+str(lat1)+", lon1="+str(lon1)+"] "+"[lat2="+str(lat2)+", lon2="+str(lon2)+"]\t"+ str(latout)+"\t"+ str(lonout)
