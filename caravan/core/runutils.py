#! /usr/bin/python

__author__="Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)" 
__date__ ="$Oct 5, 2014 4:56:40 PM$"

"""
Module implementing a RunInfo, a wrapper class for a Scenario which is passed as argument of
(or is created inside) the main run method of core. 
The user calls the setprocess method from within core, and this class handles 
the progress of the calculations, keeping track of potential errors.
An application should simply request for the msg() method which returns a list of 
messages to be printed to a console, or the progress() method which returns a 
number between 0 to 100 indicating the progress state. Any error encountered in 
the process is stored in the class and can be queryed via the method errormsg.
All methods of this class are synchronized and therefore are thread safe

(c) 2014, GFZ Potsdam

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2, or (at your option) any later
version. For more information, see http://www.gnu.org/

"""

from threading import RLock
from array import array
from scenario import Scenario
import caravan.settings.globals as glb

_DEBUG_ =1 
class RunInfo(object):
    def __init__(self, input_event=None):
        super(RunInfo, self).__init__() #FIXME: do I need to call it for objects???
        self.__lock = RLock() #see http://effbot.org/zone/thread-synchronization.htm
        self.__scenario = None
        self.__msglist = []
        self.__status = 0 #1:running, 2:terminated (check __errormsg in case) else: uninit
        self.__errormsg = None #to be checked only if status > 1
        self.__process = None
        self.__session_id = None
        
        if input_event is not None:
            self.start(input_event)
        
    def start(self, input_event=None):
        with self.__lock:
            
            if self.status() == 0:
                if input_event:
                    self.__scenario = input_event
                try:
                    if not isinstance(self.__scenario, Scenario):
                        if self.__scenario is None:
                            raise Exception("No input given (either dict or scenario)")
                        
                        self.__scenario = Scenario(self.__scenario)
                    
                    self.__status = 1
                    self.msg("Input event = "+str(self.__scenario))
                    #self.msg("Database event = "+ self.__scenario.dbstr())
                    
                except Exception as e:
                    if _DEBUG_:
                        import traceback
                        traceback.print_exc()
                    self.stop(e)
                    #raise e
            return self
    
    def setprocess(self, process, session_id):
        with self.__lock:
            
            st = self.status()
            if st > 1:
                raise Exception("The Process cannot be started (status : {0})" .format (self.statusmsg))
            else:
                if st == 0:
                    self.start() 
                self.__process = process
                self.__session_id = session_id
                
            return True
        
    def scenario(self):
        with self.__lock:
            return self.__scenario
        
    def session_id(self):
        return self.__session_id
    
    def stop(self, error=None): #this function is actually never called when stop is completed successfully
        """
            Programmatically stops the underlying process, if: 
            the method start() and the method setprocess() 
            have been called with no exceptions raised (i.e., the status of this object is running)
            
            The optional argument is the error message, in general an Exception 
            message raised whil calling caravan_core.run
            If missing, then the stop is assumed to be called by the user and a default error 
            message of "Aborted by user" will be set
            
            The method errormsg will return the error message
            
            This object will remain in the "running" status until this method is called or progress
            is called and returns a value of 100
        """
        #if error is None, it means abortewd by user, otherwise is due to an exception (code fails)
        with self.__lock:
            if self.status() < 2:
                if self.__process is not None:
                    self.__process.terminate()
                    if error is None:
                        error = "aborted by user"
                if error:
                    err = str(error)
                    self.__errormsg = array('c', err)
                else:
                    self.msg('Process completed')
                
                self.__status = 2
                
        
    def progress(self):
        """
            Returns the progress status of the calculation, from 0 to 100. A value
            of 100 sets the internal status to 2 (completed or stopped). After that, any 
            subsequent call to progress will always return 100. If start has not 
            yet been started, returns 0
        """
        with self.__lock:
            status = self.status()
            if status < 2: 
                
                conn = glb.connection()
                
                s_id = self.__session_id
                progrez = conn.fetchall("(SELECT COUNT(*) FROM processing.ground_motion WHERE session_id=%s)\
                UNION ALL (SELECT num_targets_failed from processing.sessions where gid=%s)\
                UNION ALL (SELECT num_targets from processing.sessions where gid=%s)",(s_id,s_id,s_id,))
                
                total=1
                done=0
                failed = progrez[1][0]
                
                lp = len(progrez)
                #PROGRES SHOULD BE SOMETHING LIKE: [(0L,), (5210L,), (5210L,)] (done_ok, done_failed, total)
                total = progrez[2][0] if lp==3 else 1
                done_ok = progrez[0][0] if lp==3 else 0
                done_failed = progrez[1][0] if lp==3 else 0
                
                done = done_ok + done_failed
                
                conn.close()
                if done >= total:
                    if failed > total:
                        self.stop("No target succesfully written (internal server error)")
                    elif failed == total:
                        self.stop("No target succesfully written")
                    else:
                        mzg = "{:d} of {:d} ground motion distributions succesfully calculated" .format(done_ok, total)
                        if done_ok < total: self.warning(mzg)
                        else: self.msg(mzg)
                        
                    self.__status = 2
                    return 100.0
                else:
                    return (100.0 * done) / total  
                
            else:
                return 100.0 if status>=2 else 0.0
            
    def warning(self, *msgs):
        """
            Same as messages, but any msgs is prepended the string "WARNING: ".
            It is up to accepting devices (e.g., browser) to manage the difference
            from warnings and "normal" messages
        """
        if not msgs:
            return #otherwise we risk to call msg() (no args) whci hRETURNS the msgs
            #clearing the internalm buffer
        msgs = ["WARNING: {0}".format(n) for n in msgs]
        self.msg(*msgs)
    
    #first thing: msgs is a list of python array.array (s) object. 
    #this is best for performances (memory) BUT
    #see http://stackoverflow.com/questions/176011/python-list-vs-array-when-to-use
    def msg(self, *msgs):
        
        with self.__lock:
            if not msgs:
                tmp = self.__msglist
                self.__msglist = []
                return tmp                    
            else:
                if self.status() < 2:
                    for msg_ in msgs:
                        self.__msglist.append(str(msg_))
    @property
    def errormsg(self):
        with self.__lock:
            if self.status()==3:
                return self.sstr(self.__errormsg)
            return ""
        
    def status(self):
        with self.__lock: #True: terminated succesfully, array: aborted (array is exception error), list: running, else: uninit
            #0 uninit, 1: running, 2:terminated succesfully, 3:terminated aborted
            s = self.__status
            #NOTE: 1== True returns true!!!
            #1 means running, True means terminated succesfully. Therefore:
            return 3 if (s == 2 and self.__errormsg is not None) else s
    @property
    def statusmsg(self):
        with self.__lock: #True: terminated succesfully, array: aborted (array is exception error), list: running, else: uninit
            #0 uninit, 1: running, 2:terminated succesfully, 3:terminated aborted
            s = self.status()
            return "terminated" if s == 2 else ("canceled (" + self.errormsg+")" if s==3 else ("running" if s==1 else "ready"))
    
    def sstr(self, value):
        return ''.join(value) if isinstance(value,array) else str(value)
    
    def __str__(self):
        return "input: "+str(self.__scenario)+", status: "+self.statusmsg
    

#if __name__ == '__main__':


    