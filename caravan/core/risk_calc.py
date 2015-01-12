#! /usr/bin/python

"""
    Risk calculation module. It calls class defined in the risk module package
    Code copied and modified from Michael
    
    (c) 2014, GFZ Potsdam

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation; either version 2, or (at your option) any later
    version. For more information, see http://www.gnu.org/
"""

__author__= "Michael Haas mhaas(at)gfz-potsdam.de, Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Oct 21, 2014 2:12:35 PM$"

#for the moment, absolute import, 
#see https://docs.python.org/2/whatsnew/2.5.html#pep-328-absolute-and-relative-imports
#Relative imports are still possible by adding a leading period to the module name
#Additional leading periods perform the relative import starting from the parent of the current package

import risk.exposure_module as exposure_module
import risk.vulnerability_module as vulnerability_module
import risk.loss_module as loss_module
import caravan.settings.globals as glb

#FIRST thing: importing modules from upper packages seems to be a mess, at least debugging should be done from the upper parent folder
#sharing both of them. After some try, as it was not the main goal of the simulation AND I NEEDED A DEBUGGER, 
#I imported all files in a local python package

#SECOND: Michael caravan postgres does not work for us as we have asynchronous connections. This means we need 
#the wait() function, this means we need our dbutils.Connection class

#THIRD: the point above implies to modify the content of ALL modules of Michael where we estabilish a connection

#gm: ground motion (mcerp distribution)
#percentiles = an array of values usually [0.05 0.25 0.50 0.75 0.95]
def calculaterisk(gm, percentiles, session_id, scenario_id, target_id, geocell_id):
    
    db_conn = glb.connection() #FIXME: THIS CAN BE PASSED FROM THE MAIN METHOD?
    

    # get exposure informations for the given location
    exp = exposure_module.exposure(db_conn,geocell_id)

    
    #Get DPMs
    vul = vulnerability_module.vulnerability(gm,exp.bldg_dist,exp.bt_prop)
    #dg_pdfs=vul.dg_pdf #FIXME: UNUSED
    #get bt damage
    bt_dmg=vul.damage_bts()


    ###Calculate loss
    loss = loss_module.loss(session_id, scenario_id, target_id, geocell_id, exp.bldg_dist, exp.bt_prop, exp.target_prop, bt_dmg)
    loss.calculate()
    loss.write2db(db_conn, percentiles)
    
    
if __name__ == "__main__":
    import mcerp
    calculaterisk(mcerp.Normal(5,0.25),[0.05, 0.25, 0.5, 0.75, 0.95], 0,0,0)