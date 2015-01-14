#! /usr/bin/python

"""
Test class which runs a python server for testing the web application, along the lines of 
Django manage.py. The globals module _DEBUG_ variable is set to True, which means 
this program is run in debug mode
    
Usage
    python manage.py runserver [port] (or r [port])
    python manage.py openbrowser [port]  (or o [port])

(port is optional. When not run from within the manage.py directory 'manage.py' 
must be typed with full path)

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/
"""

from __future__ import print_function

__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="$Jun 12, 2014 9:14:21 AM$"

import os.path
import sys #for parsing command line args
import os

if __name__ == "__main__":
    
    import caravan.settings.globals as glb
    glb._DEBUG_ = True; #set it to True if executing this script
    
    #change the python working directory, if we called this script from outside the
    #dir this file is. It is necessary otherwise all referrences to files, which are 
    #relative, will be messed up in our app
    #pt = os.path.realpath(__file__)
    #os.chdir(os.path.dirname(pt))
    
    openbrowser = ("o", "openbrowser")
    runserver = ("r", "runserver")
    file = "" #"caravan/static/index.html"
    port = 8080
    
    #first argument is the script name (manage.py), therefore we start reading from index 1
    if (len(sys.argv)<2 or not (sys.argv[1] in openbrowser or sys.argv[1] in runserver)):
        print("ERROR! call manage.py opt port (where port is optional, defaults to 8080)")
        print( "where opt is:")
        print( "\t{0} to run a server at the specified url and port ".format(' or '.join([v for v in runserver])))
        print( "\t{0} to run a server and open the browser at the specified url and port ".format(' or '.join([v for v in openbrowser])))
        quit()
    
    
    if(len(sys.argv)>2):
        port = sys.argv[2]
    
    from caravan_wsgi import CaravanApp
    from miniwsgi import run
    import main
    run(main.application, file=file, openbrowser= (sys.argv[1] in openbrowser), port = port)
    