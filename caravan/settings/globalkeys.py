__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="Dec 3, 2014 8:37:25 PM"

""""
Global keys used for parameters I/O operations and language settings:
please PROVIDE ONLY VARIABLES WITH NO LEADING UNDERSCORES ASSOCIATED TO A STRINGS
as a convention (not mandatory) type LOWER CASE STRINGS (otherwise modify scenario __setitem__)
"""
LAT = "lat" #latitude
LON = "lon" #longitude
MAG = "mag" #magnitude
DEP = "dep" #depth
IPE = "ipe" #intensity prediction equation
TIM = "tim" #time 
STR = "str" #strike
SOF = "sof" #style of faulting
DIP = "dip" #dip
EID = "eid" #eid
#ground motion only:
GMO = "gm_only" 
#distribution (mcerp.npts) points:
DNP = "mcerp_npts" 
#tessellation ids:
TES = "tess_ids" 
#area of interest for calculations:
AOI = "aoi"
#area of interest intensity reference (if aoi is not map current rect)
AIR = "aoi_i_ref" 
#area of interest km step (if aoi is not map current rect)
AKS = "aoi_km_step"  

#these are keys for displaying the data:
ECL = "econ_loss"
FAT = "fatal"
MSI = "intens"

