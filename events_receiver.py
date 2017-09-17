'''
Retrieving events from Geofon (for now) and passing them to loca_run.py.
Event information are saved in folders (named after the event's id). 
In the same folder will be saved the report after simulation is completed. 

run as simply as: 
python3 events_receiver.py
'''

import os 
import pickle
import subprocess
import simpleclient 
import shutil
import time

from caravan.settings.shared import events_folder_name, events_folder_location


## Settings section begin

# These settings were moved caravan.settings.shared (so that caravan_wsgi.py could have access to them), 
# see import above

# will hold reports related to events gathered by events_receiver 
#events_folder_name = "local_events"
# and will reside in events_folder_location
#events_folder_location = "./"

#simpleclient parameters
RETRY_WAIT = 10
source = "https://ingv:ingv@geofon.gfz-potsdam.de/hmb/qml"
timeout = 120
backfill = 10
auth = None

param = {
    'heartbeat': timeout //2,
    'queue': {
        'QUAKEML': {
            'seq': -backfill -1
        }
    }
}

## Settings section end

events_folder_location = os.path.abspath(events_folder_location)
events_folder = os.path.join(events_folder_location, events_folder_name)


# creating the source object
source = simpleclient.HMB(
    source, 
    param, 
    retry_wait=RETRY_WAIT, 
    timeout=timeout, 
    auth=auth, 
    verify=False
)


def handle_event(event):
    gdacs = event["gdacs"]
    print("\n", gdacs)

    # checking if event longitude and latitude are compatible with min and max defined in caravan/settings/globals
    # note that it isnot possible to import caravan/settings/globals because it is written for python2 
    # a better solution would be create settings file shared between the main caravan program and events_receiver.py (this one)
    lon = gdacs["longitude"]
    lat = gdacs["latitude"]

    if lon < 68.5 or lon > 81 or lat < 38.5 or lat > 44:
        print("outside area of interest, skipping")
        return
            

    # naming event_folder after event_id
    event_id = gdacs["eventID"]
    event_folder = os.path.join(events_folder, event_id)

    
    # if event_folder (named after event_id) already exists it means simulation has already been performed for the event
    if os.path.isdir(event_folder): 
        return   
            

    os.makedirs(event_folder)
             
    # creating a pickle file containing event info, will be passed to loca_run.py to start the simulation
    event_info = os.path.join(event_folder, "info.pickle")
    with open(event_info, "wb") as f: 
        pickle.dump(gdacs, f, 0)
            
    
    # starting the simulation
    return_code = subprocess.run(["python2", "./local_run.py", event_info])

    if return_code.returncode > 0:
        # if errors occurs the event_folder directory is deleted
        # it could be done much better but communication between different python versions is not trivial
        # an immediate enhancement would be to use the linux tmp file system to save disk life cycles
        print("An error occurred during simulation, deleting event folder \n")
        shutil.rmtree(event_folder, ignore_errors=True)


def main(): 
    # creating events_folder if it does not exists 
    if not os.path.isdir(events_folder): 
        os.makedirs(events_folder)


    while True:
        events = source.recv()
    
        for event in events:
            if event["type"] == "QUAKEML":
                handle_event(event)
        
            elif event["type"] == "EOF":
                print("Waiting for next events in real time")


if __name__ == "__main__": 
    main()
