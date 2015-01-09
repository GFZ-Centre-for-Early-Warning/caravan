#! /usr/bin/python

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Sep 29, 2014 2:40:54 PM$"

"""
     
(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""
import time

def start(msg=None):
    if msg:
        print msg
    return time.time()
    #return time.clock()
    
def end(start, return_string = True):
    #v = time.clock() - start
    v = time.time() - start
    ss=""
    if return_string:
        seconds = int(v)
        milliseconds = 1000*(v-seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        ss = "%d:%02d:%02d.%0.3d" % (h, m, s, milliseconds)
            
    return (ss,v)

def run_test(function, msg=None, iterations=1):
    if iterations == 1:
        st = start(msg)
        function()
        (st, millisec) = end(st)
        
        print "\t%s\t%f" % (st,millisec)
        #s3.append("\t%d\t%s\t%f" % (iters,st,millisec))
    else:
        st = start(msg)
        for _ in xrange(iterations):
            function()
        (st, millisec) = end(st)
        
        print "\t%s\t%f" % (st,millisec)
        

if __name__ == "__main__":
    import sys
    pmin = float(sys.argv[1])
    pmax = float(sys.argv[2])
    
    import math
    
    prange = pmax-pmin
    decimaldigits = int(math.floor(math.log10(prange)))
    
    maxbins = 10
    divisor=2
    min_bins_distance = 1
    bins_distance = float(10 ** decimaldigits) #NOTE 10 ** 0 =1 INT! this has problems cause we might get division by zero in the loop below
    
    last_bins_distance = bins_distance
    
    while prange/bins_distance < maxbins:
        last_bins_distance = bins_distance
        bins_distance/=divisor 
        divisor = 5 if divisor== 2 else 2
        if divisor == 2: #meaning it was 5, so we dropped one decimal pos down
            decimaldigits-=1 #ACTUALLY NOT USEED, HOWEVER WE KEEP IT HERE
    
    if abs(prange/last_bins_distance - maxbins) < abs(prange/bins_distance - maxbins):
        bins_distance = last_bins_distance
    
    if bins_distance < min_bins_distance:
        bins_distance = min_bins_distance
    
    firstelm = bins_distance*int(0.5+pmin/bins_distance)
    
    while firstelm < pmin: #for safety (round errors made firstelem lower than pmin)
        firstelm = bins_distance*math.ceil(0.5+pmin/bins_distance)    
    
    #round to int if it is the case to avoid rounding errors
    int_bins_distance = int(bins_distance)
    if bins_distance == int_bins_distance:
        bins_distance = int_bins_distance
        k = int(firstelm)
    else:
        k=firstelm
    
    a = []
    while k < pmax:
        val = k
        a.append(val)
        k+=bins_distance
    a.append(k) #append last
    
    print "pmin: {:f}, pmax {:f}, bins: {}".format(pmin, pmax, str(a))
    