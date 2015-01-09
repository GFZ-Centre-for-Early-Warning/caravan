#__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
#__date__ ="$Jan 07, 2015 9:41:21 PM$"

import os
import sys	

sys.path.insert(0, '/var/www/caravan/')

#import webinterface
#application = webinterface.application

from caravan_wsgi import CaravanApp as application
