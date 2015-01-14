# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from __future__ import print_function

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)"
__date__ ="$Jan 12, 2015 5:32:51 PM$"

"""
    Main file implementing the wsgi application
"""

import sys, os, caravan_wsgi

capp = caravan_wsgi.CaravanApp

#CHANGE MATPLOT CONFIG DIR. HOPE IT WORKS 

#import tempfile
#os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp() #"/var/www/caravan/matplotconfigdir"
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt

#change dir. NOW. Brutal, might be done with os.path.join, is just a test
pt = os.path.realpath(__file__)
#os.chdir(os.path.dirname(pt))
#os.chdir(os.path.dirname('caravan/static/index.html'))
os.chdir(os.path.join(os.path.dirname(pt),'caravan/static'))
#print("ASD "+ os.getcwd())
    
def application(environ, start_response):
    #print("ASD"+os.getcwd())
    if not environ['PATH_INFO'] or not environ['PATH_INFO'].lstrip('/'):
        environ['PATH_INFO'] = "index.html"
        
    return capp(environ, start_response)
