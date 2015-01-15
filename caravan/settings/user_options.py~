#! /usr/bin/python

"""

Module holding caravan settings. It is a simple declaration of variables and values editable as 
normal text file

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Nov 13, 2014 1:08:50 PM$"


#mcerp distribution npoints:
# They will be set acccording to percentiles below.
# Called ref = max(1/min(percentiles), 1/(1-max(percentiles)))
# mcerpt_npts = max(mcerpt_npts, 2*ref)
# this is due to the fact that mcerp library is strict and 
# needs that minimum points to calculate percentiles,
# it does not interpolate, resample or whatever...
mcerp_npts = 30 #10000 is the default
#tessellation ids:
tess_ids = (2,) #(4, 7,) #Other values (7,6,3,2,1)
#percentiles for calculation in core. 
#They need NOT to be sorted ascending, they will inside the code
#HOWEVER, ALL VALUES IN ]0,1[, I.E., DO NOT SET ANY VALUE TO 0 or 1:
percentiles = (0.05, 0.25, 0.5, 0.75, 0.95)
#area of intereest (aoi) intensity refence (magnitude), to restrict the calculation area for intenisties higher than this value:
#NOT YET IMPLEMENTED, BUT MAYBER IN FUTURE RELEASES this value will be adjusted with globals.i_ref_margin (implemented there because it is an internal parameter)
aoi_i_ref = 5
#area of intereest (aoi) step radius for calculating Intensity higher than I-ref in core calculations
aoi_km_step = 10
#defining the default value for ground motion only calculation (no fatalities etcetera):
gm_only = False

#database default settings:
DB_ASYNC = 1
DB_HOST = 'localhost' #if "makalu" == socket.gethostname() else "makalu.gfz-potsdam.de" #'lhotse21.gfz-potsdam.de' #'localhost'
DB_NAME = 'caravan'
DB_USER = 'postgres'
DB_PSWD = 'postgres'
