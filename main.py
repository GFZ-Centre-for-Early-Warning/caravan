# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from __future__ import print_function

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)"
__date__ ="$Jan 12, 2015 5:32:51 PM$"

"""
    Main file implementing the wsgi application
"""

import sys, os

def geturl(environ):
    """
        Reads the url string from environ, basically
        environ['PATH_INFO'].lstrip('/')
    """
    url = environ['PATH_INFO']
    if(url):
        url = url.lstrip("/")
    return url

capp = None

def application(environ, start_response):
    #change the python working directory, if we called this script from outside the
    #dir this file is. It is necessary otherwise all referrences to files, which are 
    #relative, will be messed up in our app
    pt = os.path.realpath(__file__)
    os.chdir(os.path.dirname(pt))
    
    print('os_path: {0}'.format(os.path.dirname(pt)), file=sys.stderr)
    output = ''
    try:
        #raise Exception("try-out")
        global capp
        if capp is None: 
            import caravan_wsgi
            capp = caravan_wsgi.CaravanApp
        return capp(environ, start_response)
    except Exception as e:
        from StringIO import StringIO
        s = StringIO()
        import traceback
        traceback.print_exc(file=s)
        output = s.getvalue()
        print(output, file=sys.stderr)
    
        
    status = '200 OK'
#    output = "URL IS:<div>"+ geturl(environ) + "</div>"

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
