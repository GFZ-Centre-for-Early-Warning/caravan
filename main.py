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

#change dir. NOW
os.chdir(os.path.dirname('caravan/static/index.html'))
    
def application(environ, start_response):
    if not environ['PATH_INFO'] or not environ['PATH_INFO'].lstrip('/'):
        environ['PATH_INFO'] = "index.html"
        
    return capp(environ, start_response)