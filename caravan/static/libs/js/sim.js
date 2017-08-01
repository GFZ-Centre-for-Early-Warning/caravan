/**
 * @author Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)
 * @date Tue Jul 15 2014, 11:07 AM
 */

/*
 .:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:
	Simulation class (function) definition and attaching an instance 
	of it to the caravan global event
 .:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:
 */

function simulation_init(crvn){
	//define constants for the simulation status (attached to the prototype at end):
	var STATUS_READY = 0;
	var STATUS_STARTING = 1;
	var STATUS_RUNNING = 2;
	var STATUS_STOPPING = 3;

	var pInt = parseInt;
	
	//first define Simulation function (class), then (see bottom)
	//return add to crvn (the global variable caravan) 
	//a new Simulation() which will be set as caravan.sim
	//and a newSim() function which creates a new Simulation (not used for the moment)
	function Simulation() {
	
	    var session_id = undefined;
	    //temporary: if running, stores the temporary session_id and scenario_id
	    var _session_id = undefined;
	
	    //listeners:
	    var listeners = {'status':[], 'progress':[], 'msg':[]};
	    /**
	     * Register a listener, type can be progress status or message
	     * type callbacks accept an oldStatus newStatus argument
	     * progress callbacks accept a progress argument
	     * message callbacks accept an array of strings, which can start with "WARNING: " or "ERROR: "
	     */
	    this.registerListener = function (type, callback) {
	        listeners[type].push(callback);
	    };
	
	    this.removeListeners = function () {
	    	if(arguments.length){
	    		listeners[arguments[0]] = [];
	    	}else{
	    		for(var n in listeners){
	    			listeners[n] = [];
	    		}
	    	}
	    };
	    
	    /**
	     * Notifies the listeners added with type 'status' that the simulation
	     * status has changed. Possible values of both arguments (which are
	     * assured to be different) can be accessed with the simulation object 
	     * via simulation.READY, simulation.STARTING, simulation.RUNNING and
    	 * simulation.STOPPING
	     */
	    var fireStatusChanged = function (oldStatus, newStatus) {
	        if (oldStatus === newStatus) {
	            return;
	        }
	        for (var i = 0; i < listeners['status'].length; i++) {
	            listeners['status'][i](oldStatus, newStatus);
	        }
	    };
	    
	    /**
	     * Notifies the listeners added with type 'progress' that the simulation
	     * is progressing. The argument completed is the progress value, 
	     * a number in [0,100], remaining represents the remaining
	     * time in seconds (float) and remainingText is remaining string representation
	     * (you can use your own  by formatting remaining, if you want)
	     */
	    var fireProgress = function (completed, remaining, remainingText) {
	        for (var i = 0; i < listeners['progress'].length; i++) {
	            listeners['progress'][i](completed, remaining, remainingText);
	        }
	    };
	    
	    /**
	     * Notifies the listeners added with type 'msg' that  
	     * messages are sent from the server during simulation. msg is an array
	     * of strings, which might start with "ERROR: " or "WARNING: " to denote
	     * error or warning messages, respectively
	     */
	    var fireMsg = function (msg) {
	        var mzg = "";
	        if (typeof msg === 'string') {
	            mzg = [msg];
	        } else {
	            mzg = msg;
	        }
	
	        if (!mzg || !mzg.length) {
	            return;
	        }
	        
	        for(var i=0; i<listeners['msg'].length; i++){
	        	listeners['msg'][i](mzg);
	        }
	    };
	    
	    
	    //end of listeners
	    var _status = STATUS_READY;
	
	    //set the status of the simulation
	    //Passing sessionID and scenarioID make sense only if status is running, and they will set the private variables 
	    //_session_id and scenario_id. In any other case they will be ignored
	    var setStatus = function (status, sessionID, scenarioID) {
	        var oldStatus = _status;
	        _status = status;
	        if (_status === STATUS_READY) { //initialize:
	            _session_id = undefined;
	        } else if (_status === STATUS_RUNNING) {
	            _session_id = sessionID;
	        }
	        fireStatusChanged(oldStatus, status);
	    };
	
	    this.status = function () {
	        return _status;
	    };
	
	    var starttime;    
	
	    //internal stop: called by querySimulationProgress or start:
	    //sets the internal flag and updates the optional stuff, if any...
	    //calls setStatus first
	    //NOTE: if optional_error_message IS not MISSING, then fireMsg will be called 
	    var _stop = function (optional_error_message) {
	        setStatus(STATUS_READY);
	        if (optional_error_message) {
	            fireMsg(optional_error_message);
	        }
	    };
	
	    var querySimulationProgress = function (sim) {
	        if (_status !== STATUS_RUNNING && _status !== STATUS_STOPPING) { //exit silently. This case should never happen...
	            return;
	        }
	
	        var se_id = _session_id;
	        var stopRequest = _status === STATUS_STOPPING ? 1 : 0;
	        if (stopRequest) {
	            fireMsg("Sending stop request to the server");
	        }
	        //if se_id and sc_id have problems, then the post below should fall into the error case (fail function)
	        var $ = jQuery;
	        $.post('query_simulation_progress', JSON.stringify({session_id: se_id, /*scenario_id: sc_id,*/ stop_request: stopRequest}), function (data, textStatus, jqXHR) {
	            try {
	                if (data.msg && data.msg.length) {
	                    fireMsg(data.msg);
	                }
	            } catch (err) {
	            }
	
	            if (data.error) {
	                _stop("ERROR: "+ data.error);
	                return;
	            }
	
	            var completed = 0;
	            //avoid throwing errors for gui update, go on in case
	            try {
	                completed = data.complete; 
	                if (completed >= 100) { completed = 100;
	                } else if (completed <= 0) { completed = 0;
	                }
	                remainingTime = sim.remTime(starttime, completed);
	                frmtTime = sim.formatTime(remainingTime)
	                fireProgress(completed, remainingTime, frmtTime);
	            } catch (err) {
	            }
	            var _completed_ = completed === 100;
	            var delay = 250; //half of half a second. Decrease/increase if you see bad repainting behaviour
	
	            if (_completed_) {
	                //setup necessary stuff:
	                //set session_id and scenario_id:
	                session_id = se_id;
	                //then call _stop, which re-arranges the text area and calls setStatus which notifies the 
	                //listeners. This way, if the listeners want to have access to scenario_id and session_id, they can
	                _stop();
	                fireMsg("Fetching Map Data ...");
                    //generate report
                    $.post('generate_report',JSON.stringify({ session_id: se_id }));
	            }

	            setTimeout(function () {
	                if (_completed_) {
	                    crvn.map.update(se_id);
	                    var timeformatted = sim.formatTime((new Date().getTime() - starttime) / 1000.0); //might be empty string
	                    fireMsg("Done" + (timeformatted ? " in " + timeformatted : ""));
	                    starttime = null;
	                } else {
	                    querySimulationProgress(sim);
	                }
	            }, delay);
	
	        }, "json").fail(function () {
	            _stop("ERROR: " + arguments[0].status + ":\n" + arguments[0].statusText);
	            //NOTE: we SHOULD NEVER BE here (SEE SERVER SIDE CODE). LEFT HERE FOR SAFETY
	        });
	    };
	
	    this.start = function ( event ) {
	        //optional_callback is passed the argument returned by the server, usually a dict with session_id and scenario_id
	        if (_status !== STATUS_READY) {
	            return;
	        }
	
	        setStatus(STATUS_STARTING);
	        fireMsg("Sending input data to server process");
	
	        //NOTE: WITH VALUES OF TYPE NUMBER, THEN:
	        //The value sanitization algorithm is as follows: If the value of the element is not a valid floating-point number, then set it to the empty string instead.
	        //See http://stackoverflow.com/questions/18852244/how-to-get-the-raw-value-an-input-type-number-field
	        var $ = jQuery;
	        
	        var event = getEvent();
	        //alert(JSON.stringify(event));
	
	        var sim = this;
	
	        //we don't use the $.post(...).always() callback cause optional_callback has NOT to be called NOT at the end of the done function,
	        //in case post is successfull (see below)
	        $.post('run_simulation', JSON.stringify(event), function (data, textStatus, jqXHR) {
	
	            if (data.error || sim.status() !== STATUS_STARTING) {
	                _stop("ERROR: "+  (data.error || "Aborted by user"));
	                return;
	            }
	
	            setStatus(STATUS_RUNNING, data.session_id/*, data.scenario_id*/);
	
	            starttime = new Date().getTime(); //locally defined (private), see above
	            querySimulationProgress(sim);
	
	
	        }, "json").fail(function () {
	            //NOTE: we SHOULD NEVER BE here (SEE SERVER SIDE CODE). LEFT HERE FOR SAFETY
	            _stop("ERROR: " + arguments[0].status + ":\n" + arguments[0].statusText);
	        });
	
	    };
		    
	    //either pass the textarea or leave empty. NOTE: empty arguments mean
	    //stopped by user, OTHERWISE STOPPED INTERNALLY BY SERVER ERRORS!!!
	    this.stop = function () {
	
	        if (_status === STATUS_STOPPING || _status === STATUS_READY) {
	            return;
	        }
	
	        var se_id = _session_id;
	        if (se_id !== undefined /*&& sc_id !== undefined*/) { //should never be the case
	            setStatus(STATUS_STOPPING);
	        }
	    };
	};
	
	//constants defining the status of the simulation
    //attach them to the prototype so that are shared across all instances
	//and sim.status() can be compared to sim.READY, sim.RUNNING etcetera
	//(although we have only one instance, for the moment)
    var sp = Simulation.prototype;
	sp.READY = STATUS_READY;
    sp.STARTING = STATUS_STARTING;
    sp.RUNNING = STATUS_RUNNING;
    sp.STOPPING = STATUS_STOPPING;
	
    //these two functions are attached to the prototype so that can be "overridden" 
    //by attaching a new function with the same name to a new simulation instance, 
    //and moreover they don't need to be instantiated for all sim instances (being attached 
    //to the proprotype they are created once)
    /** 
     * Returns the remaining time as float representing seconds
     * to remain during simulation execution. Called internally
     */
    sp.remTime = function (starttime, workdone_from_0_to_100) {
        if (workdone_from_0_to_100 <= 0) {
            return "";
        }

        var time = new Date().getTime();
        var elapsed = (time - starttime) / 1000.0; //note that 1000 is ok, as javascript auto casts division to float
        var remaining = (100.0 - workdone_from_0_to_100) * elapsed / workdone_from_0_to_100;

        return remaining;
    };
    
    /**
     * Formats a time in float, representing seconds, or the empry string 
     * is the argument is less than 1 
     */
    sp.formatTime = function (time_in_sec_as_float) {
        var val = ["", "", ""];
        if (time_in_sec_as_float >= 1) {
            function aprox(divisor, index, appendSymbol) {
                if (time_in_sec_as_float > divisor) {
                    var val_ = pInt(time_in_sec_as_float / divisor);
                    val[index] = (val_ < 10 ? "0" + val_ : "" + val_);
                    time_in_sec_as_float -= (val_ * divisor);

                    if (appendSymbol) {
                        val[index] += appendSymbol;
                    }
                }
            }
            aprox(3600, 0, "h:");
            aprox(60, 1, "m:");
            aprox(1, 2, "s");
        }
        return val.join("");
    };
    
    crvn.newSim = function(){return new Simulation();}
    crvn.sim = crvn.newSim();
    
}


/*
* @returns The plain object representing the simulation event to be sent to the server
*/
function getEvent () {

    function val(elm_or_id) { //elm can be a dom element, a jquery element, or a string denoting the id
        //undefined means don't consider the returned value
        var $elm = (typeof (elm_or_id) === 'string') ? $('#' + elm_or_id) : $(elm_or_id);
        //note given the jquery element $e, $($e) != $e BUT $($e).get(0) == $e.get(0) (the wrapped dom element is the same) 
        var ret = undefined;
        if (!$elm.is(":disabled") && !$elm.hasClass("disabled")) {
            ret = $elm.is('input') ? ($elm.is(':checkbox') ? ($elm.prop("checked") ? true : false) : $elm.val()) : $elm.data('value');
            ret = ret === undefined ? null : ret;
        }
        return [$elm, ret]; //json.dumps accepts null, not undefined. Check for safety...
    }

    function add(event, elms_or_ids) {
        for (var i = 0; i < elms_or_ids.length; i++) {
            var v = val(elms_or_ids[i]);
            var id = v[0].attr('id');
            var value = v[1]; 
            if (value !== undefined) {
                event[id] = value;
            }
        }
    }

    var event = {};
    var p = caravan.params; //caravan globally defined
    add(event, [p.LAT, p.LON, p.MAG, p.DEP, p.STR, p.IPE, p.GMO]);

    var aoi = p.AOI;
    if ($('#' + aoi).data('value') === 2) {
        var rect = caravan.map.getMap().getBounds();
        rect = [rect._northEast.lng, rect._northEast.lat, rect._southWest.lng, rect._southWest.lat];
        event[aoi] = rect;
    }

    if ($("#sou").find(".selected").attr("id") === "sou_ext") {
        add(event, [p.STR, p.DIP, p.SOF]);
    }

    if ($('#advanced').data('value')) {
        var $advanced = $("[data-advanced]");
        add(event, $advanced);
    }
    return event;
}


/*
 * Configuring the click on the run button (on document ready) and its interaction
 * with caravan.sim just defined
 */
jQuery(document).ready(function () {
    var $runBtn = jQuery('#run_button');    
    var $ = jQuery;
    
    if(caravan.viewmode){
        //Avoid initializing the simulation (as it may not be needed), saving the client some javascript.
        //When the run button is clicked the input parameters are compared with the ones set by the server, 
        //if differences are found the simulation is run, else a message is shown to the user. 
        //This should save some work to the server. 

        $runBtn.click( function(){

            function is_the_same_event(client_event, server_event){

                for(var key in client_event){
                    if(client_event[key] != server_event[key]){
                        return false; 
                    }
                }   

                return true;
            } 
            
            event =getEvent(); 
            
            if( is_the_same_event(event, caravan.event_parameters) ){ 
                //it would be better to implement a nicer way to interact with the user, 
                //maybe a message on the screen like the "UPDATING MAP ..." one or something similar
                
                alert("please change some parameter to run the simulation"); 

            }else{ 
                //exit the view mode and get back to the normal one, 
                //initializing all the relevant variables and functions for the simulation
                
                caravan.viewmode =false; 

                $runBtn.off("click"); 

                simulation_init(caravan);   
                simulation_init2(); 

                //emulating a click on the run button
                //maybe not very elegant but saves some troubles as startRun() is hidden inside simulation_init2()
                $runBtn.click(); 
            }
        }); 
    
    }else{
        simulation_init(caravan); 
        simulation_init2(); 
    }


    function simulation_init2 (){

        //sets the run text. Due to the caravan policy, we set both the data-title
        //and the html attribute
        function setRunText(key){
            $runBtn.attr('data-title',key);
            $runBtn.html(crv.dict.title(key));
        }

        var crv = caravan;
        var sim = crv.sim;
        var dict = crv.dict;
        //little note: $cont has two panels: one for the input params and the other
        //holding the simulation stuff ($sim_panel below)
        //$sim_panel has a simulation message panel and (bottom) a progress bar container panel
        var $cont = $('#param_container');
        var $sim_panel = $('#simulation-panel');
        var velocity = 'fast';

        var $ta = $cont.find('.simulation-msgs');
        var $pbar = $cont.find('.pbar');
        var $pbarText = $cont.find('.pbar-text');

        var stopRun = function () {
            sim.stop();
        };

        var startRun = function () {
            //removing/hiding visible elements and then adding/setting to visible other elements causes two width variation to the parent div, 
            //causing two unuseful resize to the map.
            //Therefore, perform a dummy width set and then release it

            $cont.css('width', $cont.css('width'));
            //$cont width explicitly set: it will not stretch/shrink while adding/removing,
            //which is visually nicer and does not call map resizing and unuseful gui related calculation stuff
            //now proceed:
            $cont.children('.input-params').hide(velocity, function () {
                var $div = $sim_panel;
                //restore progressbar, if it was hidden from a previous simulation end/stop
                //If you change code here, change also lines in registerListener below (should do the 'opposite')
                $div.find('.pbar-container').show();
                $div.find('.simulation-msgs').css('bottom', '').html(""); //empty its content

                $div.css('display','block'); //default for divs. I Do not use show as we are not sure what display it sets

                //#pbar-text: vertically center text. This cannot be done with css easily as it works for non absolutely positioned elements
                //so we set line-height equal to the element height:
                $pbarText.css('line-height', $pbarText.css('height'));
                sim.start(); //harmless if already running (true after code changes? check it)
            });
        };
    

        var restoreRun = function(){
            $sim_panel.hide();
            $sim_panel.siblings().show(velocity, function () {
                //remove css property set in startGUIRun
                $cont.css('width', '');
                setRunText('run_text');
                $runBtn.off('click').click(startRun);
            });
        };

        $runBtn.click(startRun);

        sim.registerListener('status', function (oldState, newState) {
            $runBtn.prop('disabled', newState === sim.STARTING || newState === sim.STOPPING);
            //hide toolbar buttons to avoid weird behaviours (e.,g. changing dict, showing help)
            //which are all stuff complex to handle and which are likely to appear as bug even if they aren't:
            $('.banner').find('.toolbar').css("visibility",newState === sim.READY ? "" : "hidden");
            $runBtn.off('click');
            //as this method is called when the state changes, oldState is never READY so we can safely assume
            //we need to go back now:
            if (newState === sim.READY) {
                //first reset the pbar
                var $pbar = $sim_panel.find('.pbar');
                var $pbarText = $sim_panel.find('.pbar-text');
                $pbar.css('width',0);
                $pbarText.html('wait...');
                //hide progressbar and stretch sim messages. 
                //If you change code here, change also lines in startRun (should do the 'opposite')
                $sim_panel.find('.pbar-container').hide(velocity);
                $sim_panel.find('.simulation-msgs').css('bottom', '0px');

                setRunText('goback_text');
                $runBtn.off('click').click(restoreRun);
            }else if (newState === sim.RUNNING){
                setRunText('cancel_text');
                $runBtn.off('click').click(stopRun);
            }
        });

        sim.registerListener('msg', function (mzg) {
            try {
                for (var i = 0; i < mzg.length; i++) {
                    var m = mzg[i];
                    var $span = $("<span>");
                    if(m.indexOf("WARNING: ")==0){
                        m = m.replace("WARNING: ","<img src='"+crv.imgPath('warning.png')+"' alt='WARNING: '/>");
                        $span.addClass("warning");
                    }else if(m.indexOf("ERROR: ")==0){
                        m = m.replace("ERROR: ","<img src='"+crv.imgPath('cancel.png') + "' alt='ERROR: '/>");
                        $span.addClass("error");
                    }
                    $ta.append($span.html(m));
                }
            } catch (err) {
                return;
            }
            //scroll to the bottom of the div:
            $ta.scrollTop($ta.prop("scrollHeight"));
        });

        sim.registerListener('progress', function(completed, remainingTime, remainingTimeStr){
            var dataPercent = completed.toFixed(0) + "%"; 
            $pbar.css('width', dataPercent);
            if (remainingTimeStr) { //empty if remainingTime < 1
                remainingTimeStr = "  (" + remainingTimeStr + " left)";
            }
            dataPercent += remainingTimeStr;
            $pbarText.html(dataPercent);
        });
    }
});
