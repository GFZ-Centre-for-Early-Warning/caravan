/* 
 * @author Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>), Marc Wieland <mwieland(at)gfz-potsdam.de>
 * @date Mon October 10 2014, 21:09
 */
(function(crvn){
	var leaf = L;
    var $ = jQuery;
	/**
	 * Class (Function) for managing legend and geocells colors. 
	 * It first builds a scale of increasing values each associated to a color,
	 * by taking as argument an html element E. It first scans E finding all elements 
	 * with 'data-value' attribute (whose value represents a number, and whose css 
	 * 'background-color' property must evaluate to a valid color) and builds the 
	 * above mentioned scale.   
	 * It then implements a function, color(val) which 
	 * takes a value val and returns the corresponding color according to the 
	 * built scale, stored internally. The color returned is the 'closest' to val, 
	 * unless the argument interpolate is true: in that case, for non boundary values,
	 * it interpolates linearly between the two closest colors. This works for 
	 * color scale which are consistent with the scale (i.e., whose color value 
	 * increases or descreases according to the scale)
	 * Out-of bounds values return the closest boundary color.
	 */
	function ColorMap($div, interpolate){
    	//WARNING: IF YOU PUT THE G  FLAG YOU HAVE TO SET THE LASTINDEX REGEX PROPERTY TO 0 BEFORE ANY TEST OR EXEC!
    	var rgbRe = /rgba*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*(.+))*\s*\)/i;
    	var hexRe = /#(?:(?:([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f]))|(?:([0-9a-f])([0-9a-f])([0-9a-f])))$/i;
    	var pInt = parseInt;
    	var pFloat = parseFloat;
    	var _fl_ = Math.floor; //JavaScript auto-converts integer division to float. 
    	//Sometimes we need integer division (see e.g., 'this.color' function below)
    	//NOTE: parseInt seems to be slower than math.floor
    	//(see http://jsperf.com/math-floor-vs-math-round-vs-parseint/2)
    	//it should be tested cross  browser, but it makes sense since parseInt
    	//does 'more'. We use _fl_ when we do not need to parse strings for example
    	var abs = Math.abs;
    	var round = Math.round
    	
    	//I could set static methods for these three functions (so they are not instantiated every time):
    	function rgb(colorstr){
    		var a = hexRe.exec(colorstr);
    		if(a && a.length === 7){
    			return a[1] === undefined  
    					? [pInt(a[4]+a[4],16), pInt(a[5]+a[5],16), pInt(a[6]+a[6],16)] 
    					: [pInt(a[1],16), pInt(a[2],16), pInt(a[3],16)];
    		}
    		a = rgbRe.exec(colorstr);
    		if(a && a.length === 5){
    			return [pInt(a[1]), pInt(a[2]), pInt(a[3])];
    		}
    		return undefined;
    	}
    	
    	function hexstr(r, g, b) {
            r = r.toString(16);
            g = g.toString(16);
            b = b.toString(16);
            return "#" + (r.length === 1 ? "0" + r : r) + (g.length === 1 ? "0" + g : g) + (b.length === 1 ? "0" + b : b);
    	}
    	
    	function interpolationColor(val1, color1, val2, color2, val3){
    		//val1 is lower than val2
    		var a1 = rgb(color1);
    		if(!a1){return undefined;}
    		if(val3 <= val1){return hexstr(a1[0],a1[1],a1[2]);}
    		var a2 = rgb(color2);
    		if(!a2){return undefined;}
    		if(val3 >= val2){return hexstr(a2[0],a2[1],a2[2]);}
    		var den = (val3-val1)/(val2-val1);
    		//y = cmp1 + den*(cmp2-cmp1)
    		function cmp(cmp1, cmp2){
    			return cmp1===cmp2 ? cmp1 : round(cmp1 + den*(cmp2-cmp1));
    		};
    		for (var i=0; i<3 ; i++){ a2[i] = cmp(a1[i], a2[i]); }
    		//console.log('mean: ' + a2);
    		return hexstr(a2[0],a2[1],a2[2]);
    	}
    	
    	var a=[];
    	
    	$div.find('*[data-value]').each(function(i,elm){
    		var $elm = $(elm);
    		a.push([pFloat($elm.data('value')), $elm.css('background-color')]);
    	});
    	
    	//sort array (modifying it):
    	a.sort(function(a,b){return a[0]-b[0];});
    	
    	//we use it below in the binary search algorithm
    	
    	var interp = interpolate || false;
    	this.color = function(val){ //binary search algorithm to find color value (array is sorted)
    		var lo = 0;
    		var last = a.length - 1;
            var hi = last;
            while (lo <= hi) {
                // Key is in a[lo..hi] or not present.
                var mid = lo + _fl_((hi - lo) / 2);
                var cmp = a[mid][0];
                if      (val < cmp) hi = mid - 1;
                else if (val > cmp) lo = mid + 1;
                else return a[mid][1];
            }
            //just a check for safety:
            if(lo<=0){
            	return a[lo][1];
            }
            if(lo>=a.length){
            	return a[lo-1][1];
            }
            
            if(interp){
            	return interpolationColor(a[lo-1][0], a[lo-1][1],a[lo][0], a[lo][1], val) || "";
            }
            //in any other case, return closest value
            //lo is now the insertion index, so check whether it is closer to lo or lo-1
            return abs(a[lo][1]-val)<abs(a[lo-1][1]-val) ? a[lo][1] : a[lo-1][1];
        };
        
        var _values=undefined;
        this.values = function(){
        	//lazily create it:
        	if(_values === undefined){
        		_values=[];
        		for(var i=0; i< a.length; i++){
        			_values.push(a[i][0]);
        		}
        	}
        	return _values;
        };
        
        var _labels=undefined;
        this.labels = function(){
        	//lazily create it:
        	if(_labels === undefined){
                _labels = [];
        		for(var i=0; i< a.length; i++){
        			_labels.push("");
        		}
                $div.find("*[data-label]").each(function(i, elm){
                    _labels[i] = $(elm).data('label')+"";
                });
        	}
        	return _labels;
        };
	}
	
	
	//var crvn = caravan; //globally defined
    function MapManager(mapElementId /*, layerNames*/) {
        var map;
        var baseLayer;
        
        var gmpeLayer; //instanceof 
        var $ = jQuery;
        //instantiate once (faster lookup):
        var pInt = parseInt;
    
        //DEFINES EACH GEOJSON FEATURE 'PROPERTY' FIELDS
        //I.E., GIVEN A GEOJSON FEATURE F, WE CAN SAY F.properties[P_FIELD_BLABLA]
        var P_FIELD_FAT = 'fatalities_prob_dist'; // 'fatalities_perc';
        var P_FIELD_GMPE = 'gmpe_perc';
    
        try {
            //CREATING THE MAP. SEE http://leafletjs.com/reference.html#map-constructor
            map = leaf.map(mapElementId).setView([41.25, 74.75], 7);
            //add baselayer
            baseLayer = leaf.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
                maxZoom: 18,
                attribution: 'Processing &copy; <a target="_blank" href="http://www.gfz-potsdam.de/en/research/organizational-units/technology-transfer-centres/centre-for-early-warning-systems-ews/">GFZ Potsdam - Centre for Early Warning Systems</a>' +
                        ' | Map data &copy; <a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, ' +
                        ' | Imagery &copy; <a target="_blank" href="http://mapbox.com">Mapbox</a> | <span id=latlon>&nbsp;</span>',
                id: 'examples.map-i875mjb7'
            }).addTo(map);
        } catch (e) {
            //console.log(e);
            return;
        }
        
        var _layers = {}; //a dict of keys : caravan-layer properties
        //a caravan-layer is simply a javascript plain object which holds the 
        //leaflet layer, plus a colormap function and a style function
        
        //defining the style default and the style function
        //which will delegate the caravan-layer style function.
        
        //defining default style and empty style objects
        //(empty by default in leaflet IS NOT NO-STYLE, but assigns a 
        //custom style where each geocell is rendered with blue borders and semi transparent fill colors)
        var DEFAULT_STYLE = function(){ return {
                radius: 10,
                //fillColor: val, //colors[val + 1], // '#0B0B3B',
                color: '#000000', //colors[val + 1], //'#0B0B3B',
                opacity: 1, //should be set the half of the value below cause they overlap?? fix me... 
                weight: 0,
                fillOpacity: 0.5
        	};
        };
        var EMPTY_STYLE = function(){
        	return {
        		opacity: 0,
                fillOpacity: 0
        	}
        }
        //passing an empty dict tot the style function
        function getStyleFunction(layer_key_name){
        	return function(feature){
        		if(layer_key_name in feature.properties){
        			if('styleFcn' in _layers[layer_key_name]){
        				var defOpts = DEFAULT_STYLE();
        				_layers[layer_key_name].styleFcn(feature, feature.properties[layer_key_name], _layers[layer_key_name].colorMap, defOpts); 
        				return defOpts;
        			}
        		}
        		return EMPTY_STYLE();
        	};
        }
        
        var selLayerName = undefined;
        
        var control = (function(){
        	function Control(){
            	var _style_ = 'none';
            	var imgs = {'none': crvn.imgPath('arrow-down-01-32.png'), "":crvn.imgPath('arrow-up-01-32.png')}
            	var _div = $("\
            	<div id=leaflet-control class='leaflet-bar'>\
            	<div id=legend-container>\
            	</div>\
            	<div id=leaflet-layer-switcher-toggler>\
            		<a id='leaflet-show_layers' href=#>\
                    	<img src='"+imgs[_style_]+"'/>\
                	</a>\
            	</div>\
            	<div id=leaflet-layer-switcher style='display:"+_style_+"'></div>\
            	</div>");
            	this.getDiv = function(){return _div;}
            	var velocity = 'fast';
            	_div.find('a').click(function(){
            		_style_ = !_style_ ? "none" : "";
            		$(this).find('img').attr('src',imgs[_style_]);
            		if(_style_){
            			_div.find('#leaflet-layer-switcher').hide(/*velocity*/);
            		}else{
            			_div.find('#leaflet-layer-switcher').slideDown(velocity);	
            		}
            		return false;
            	});
            	var doRadioClick = function(name){
            		if(selLayerName){
            			map.removeLayer(_layers[selLayerName].layer);
            			_layers[selLayerName].legend.detach();
            		}
            		_layers[name].layer.addTo(map);
            		var $legendContainer = _div.find('#legend-container');
            		_layers[name].legend.detach().appendTo($legendContainer);
            		selLayerName = name;
            		//set div with arrow height equal to legend height.
            		//Note that we set box-sizing border-box to both in layout.css
            		//note: set the anchor height and line-height (for vertical align):
            		var $a = _div.find('#leaflet-layer-switcher-toggler').children('a');
            		var h = $legendContainer.css('height')
            		$a.css({'height':h,'line-height':h});
            	};
            	this.addLayer = function(name){
                	var $radio = $('<input>').attr('type','radio').attr('name','leaflet-layer-selector').change(function(){
                		doRadioClick(name);
                		_div.find('a').click(); //closes the popup
                	});
                	if(!selLayerName){
                		$radio.prop('checked',true);
                		doRadioClick(name);
                	}
                	var $l = $('<label>').append($radio).append($('<span>').attr('data-title',name).html(crvn.dict.title(name)));
                	_div.find('#leaflet-layer-switcher').append($l);
            	}
            }
            return new Control();
        })();
        
        //defining function to add a control:
        var _addControl =function(position, div){
            var ctrl = leaf.control({
                position : position
            });
            ctrl.onAdd = function(map) {
                this._div = $(div).get(0);
                return this._div;
            };
            ctrl.addTo(map);
            return ctrl;
       };
       
       //adding custom legend:
       _addControl('topright', control.getDiv());
       
       /**
        * Function addControl(position, div)
        * adds a control wrapping div (an html, a string or a jQuery element)
        * to the map, returning the leaflet control object. The object
        * can be removed via ctrl.removeFrom(map)
        * position is the position, e.g., 'topright'
        */
       this.addControl = _addControl;
       
        /**
         * Adds a new empty GeoJson Layer to the internal leaflet map,
         * returning it. The second arg is a function 
         * function(feature, featureData, colorMap, defOpts)
         * used for styling the given feature.
         * featureData is an object with two fields: data and value
         *  data is the feature data (usually an array, e.g. the feature percentiles)
         *  value is the feature value, the one which is usually used for mapping 
         *  a feature to a color (i.e., value might be data last index if data is an array of percentiles 
         *  and value should return the last percentile, but it might be also the index of max(data))
         * colorMap is an object (JavaScript function) which maps the given legend to a set of colors.
         *  It has two methods: values(), which returns the sorted ascending tick values of the legend,
         *  and color(val) which takes a scalar and converts it to a color
         * defOpts is the leaflet dictionary (JavaScript object) which will be returned for styling the 
         * feature. It is set by default as DEFAULT_STYLE (see above)
         * This function does not need to return any value, just fill defOpts with whatever you want
         * (see http://leafletjs.com/examples/geojson.html and 
         * http://leafletjs.com/reference.html#geojson)
         */
		this.addLayer = function(name, $divLegend, interpolate, styleFcn){
        	//needs to add it to the _layers object BEFORE adding to the map:
        	var clay = {
        		legend: $divLegend,
    			colorMap : new ColorMap($divLegend, interpolate),
    			layer : leaf.geoJson([], {
    		        style: getStyleFunction(name)//,
    		        /*onEachFeature: onEachFeatureFcn*/ /*,
    		         pointToLayer: function (feature, latlng) {
    		         var mrk = leaflet.circleMarker(latlng);
    		         return mrk;
    		         }*/
    		    })   			
        	};
        	//add function later, because we add it only if it is a function
        	//(no guarantee it's well implemented, but getStyleFunction above 
        	//will return the empty object if we don't enter this 'if'
        	if (typeof(styleFcn) === "function") {
        		clay.styleFcn = styleFcn;
        	}
        	_layers[name] = clay;
        	//var lay = clay.layer; //the leaflet layer
        	//lay.addTo(map);
        	control.addLayer(name);
        	return clay;
        };
        
        /**
         * @return the leaflet GeoJson layer identified by name
         * returning it
         * @param name the name associated to the given layer, as set in addLayer
         */
        this.getLayer = function(name){
        	return name in _layers ? _layers[name].layer : undefined;
        };
        /**
         * 
         * @param {type} name
         * @returns {clay.colorMap} the colorMap object associated to the layer mapped to name
         * It is a class (function) which has two interesting methods: values() (returns all 
         * the values set as ticks for the legend) and color(val), which returns a color 
         * associated to a given value
         */
        this.getColorMap = function(name){
            return name in _layers ? _layers[name].colorMap : undefined;
        };
        
        //common function for add/set/empty Layers 0: delete, 1:set, 2: add
        var doLayer = function(operation, name, data){
        	var myLayer = _layers[name];
        	if(myLayer){
        		//Note: myLayer.layer is the leaflet layer
        		if(operation < 2){
            		myLayer.layer.clearLayers(); // inherited from LayerGroup
                }
            	if(operation > 0){
            		myLayer.layer.addData(data); // inherited from LayerGroup
                }
            	return myLayer;
        	}
        	return undefined;
        };
        
        /**
         * Removes the data from the layer identified by name
         * @return the layer identified by name, or undefined
         */
        this.removeData = function(name){
        	return doLayer(0, name);
        };
        
        /**
         * Sets data to the layer identified by name, removing previously set data
         * geoJsonFeatures is an array of GeoJson encoded features
         * @return the layer identified by name, or undefined
         */
        this.setData = function(name, geojsonFeatures){
        	return doLayer(1, name, geojsonFeatures);
        };
        
        /**
         * Adds data to the layer identified by name.
         * geoJsonFeatures is an array of GeoJson encoded features
         * @return the layer identified by name, or undefined
         */
        this.addData = function(name, geojsonFeatures){
        	return doLayer(2, name, geojsonFeatures);
        };
        
        //add scale:
        leaf.control.scale().addTo(map);
        
        //adding lat lon display when moving with the mouse on the map, and when clicking
        var latlon = $("#latlon");
        var setLatLon = function (e) {
            var lat = "--.---";
            var lng = "--.---";
            if (e && e.latlng) {
                var l = e.latlng;
                lat = l.lat.toFixed(3);
                lng = l.lng.toFixed(3);
            }
            latlon.html("lat: " + lat + " lng: " + lng);
        };
    
        //add event listener for mouse moving:
        map.on('mousemove', function (e) {
            setLatLon(e);
        });
        map.on('click', function (e) {
            setLatLon(e);
        });
        //set default:
        setLatLon();
        
        /**
         * @return the leaflet map
         */
        this.getMap = function () {
            return map;
        };
        
        //defining the epicenter and centerEpicenter functions
        var epicenter = undefined;
        
        /**
         * Fits the bounds of the map, zooming to include 
         * the current layers bounds. includeEpicenter is a self-explanatory 
         * boolean argument. If true and only the epicenter is shown, it does
         * not zoom, simply centers the map to it
         */
        this.fitBounds = function (includeEpicenter) {
        	var zoomLayers = [];
        	//zoomLayers are leaflet layers properly set via addLayers AND 
        	//whose bounds are valid (which apparently is not the case 
        	//the layer has no data, i.e. when uninitialized):
        	for(var n in _layers){
        		var lay = _layers[n].layer; //leaflet layer
    			if(lay.getBounds().isValid()){
    				zoomLayers.push(lay);
    			}
    		}
    		
        	var noLayers = !(zoomLayers.length); 
        	var noEpicenter = !includeEpicenter || !epicenter;
        	
        	if(noLayers && noEpicenter){
        		return;
        	}else if(noLayers){ //center epicenter
        		map.panTo(epicenter.getLatLng()); //new leaf.LatLng(40.737, -73.923));
        	}else{
        		if(!noEpicenter){
        			zoomLayers.push(epicenter);
        		}
        		//fit bounds: to be sure we use a small delay
                var DELAY = 150;
                setTimeout(function () {
                    var group = new leaf.featureGroup(zoomLayers);
                    map.fitBounds(group.getBounds());
                }, DELAY);
        	}   
        }; 
        
        /**
         * With no arguments, returns an Array of two elements
         * [latitude, longitude] of the epicenter, or undefined if the 
         * epicenter has not been created (same function with arguments must 
         * have been called)
         * With arguments, it creates (if not present) the epicenter 
         * and will set its position according to the first two arguments (mandatory)
         * lat and lon.
         * The third argument (optional) will zoom to the epicenter.
         * Note that if only 
         * the epicenter is present, zoom will actually center the epicenter (leaflet 
         * panTo function)
         */
        this.epicenter = function (lat, lon, zoom) {
            if (!arguments || !arguments.length) {
                if (!epicenter) {
                    return undefined;
                }
                var latlng = epicenter.getLatLng();
                return [latlng.lat, latlng.lng];
            } else {
            	//defining zoom function, which does something 
            	//only if param is set
            	var me = this;
            	function dozoom(){
            		if(zoom){me.fitBounds(true);} //defined above (or below, jsut see)
            	};
                if (!epicenter) {
                	//when creating an epicenter, we need to know its size 
                	//because the iconAnchor leaflet property is necessary
                	//to properly center the epicenter icon. We use javascript,
                	//but in this case we need to defer all stuff after image is loaded
                	var _iconUrl = crvn.imgPath('epi.png');
                	var img = new Image();
                	img.onload = function() {
                		var w = this.width;var h = this.height; //remainder: 'this' is the image
                		var iconProperties={
                        	iconSize : [w, h],
                        	iconAnchor : [w/2, h/2],
                        	iconUrl: _iconUrl
                        };
                        epicenter = leaf.marker([lat, lon], {icon:  leaf.icon(iconProperties)}).addTo(map);
                        dozoom(); //does nothing if zoom evaluates to false
                	};
                	img.src = _iconUrl;
                } else {
                    var latlng = epicenter.getLatLng();
                    if (latlng.lat === lat && latlng.lng === lon) {
                        return;
                    }
                    epicenter.setLatLng([lat, lon]);
                    dozoom(); //does nothing if zoom evaluates to false
                }
            }
        };
        
        //setting ids of the <input> lat and lon elements.
        //Use caravan params keys, written from server python code
        var latId = '#'+crvn.params.LAT;
        var lonId = '#'+crvn.params.LON;
        //internal function which centers the map including the epicenter on
        //input changes
        var me = this; //see below why
        var centerEpicenter = function() {
            //consider the case where we typed a two element value, such as: 75.5 0.6
            var reg = /(?:,\s;)/;

            var latarray = $(latId).val().split(reg);
            var lonarray = $(lonId).val().split(reg);

            if (latarray.length && lonarray.length) {
                var lat = parseFloat(latarray[0]);
                var lon = parseFloat(lonarray[0]);
                if (!isNaN(lat) && !isNaN(lon)) {
                    me.epicenter(lat, lon, true);
                }
            }
        };


        //From: http://stackoverflow.com/questions/7105997/javascript-change-event-on-input-element-fires-on-only-losing-focus
        //make text input change event (real change, not change + focus lost etcetera):
        //however, two events are sufficient (see http://stackoverflow.com/questions/5494648/catching-all-changes-to-the-contents-of-an-input-box-using-javascript-jquery/5494697#5494697)
        //Note in any case that it will NOT fire when we programmatically set the val() attribute
        $(latId).add($(lonId)).on('input propertychange', function () {
            centerEpicenter(); //this is the clicked component. centerEpicenter has a ref on this so we call this mapmanager centerEpicenter
        });
       //this is the window object. centerEpicenter has a ref on this so we call this mapmanager centerEpicenter
        centerEpicenter(); //programmatically starts centering
        
        //====================================================================================== 
        var _events={};
        /**
         * Adds an event listener to the specified eventName to ALL layers 
         * of the map. Follows the same syntax described here: 
         * http://leafletjs.com/reference.html#events
         * 
         * To add an event to the map, use thisobject getMap() function 
         * e.g.: map.getMap().on('click'...)
         * NOTE that function_ accepts MORE arguments than the default layer listeners functions:
         * It is of the form
         * f(name, layer, feature, featureData, e)
         * where:
         * name is the layer name, as added to this class object (map)
         * layer is the leaflet layer event target. It is the associated to name (the "parent" layer)
         * feature is the geoJson feature where actually the event occurs (might be undefined). 
         * See geoJson format for infos. The associated layer (child of layer defined above) 
         * can be retrieved via e.layer
         * featureData is an object with two fields: data and value
         *  data is the feature data (usually an array, e.g. the feature percentiles)
         *  value is the feature value, the one which is usually used for mapping 
         *  a feature to a color (i.e., value might be data last index if data is an array of percentiles 
         *  and value should return the last percentile, but it might be also the index of max(data)), and
         * e is the leaflet event as described here: http://leafletjs.com/reference.html#event-objects
         * (Most of the arguments are actually retrieved from e) 
         * The this keyword refers to this map object, so that called name the 
         * first argument, this.getLayer(name) returns the current layer
         * The function_ implemented as argument does not need to return any value
         * 
         * @param {type} eventName
         * @param {type} function_
         * @returns {undefined}
         */
        this.on = function(eventName, function_){
            _events[eventName] = function_;
            var me = this;
            for(var n in _layers){
                var makeFunc = function(name){
                    return function(e){
                        var feature = e.layer && e.layer.feature ? e.layer.feature : undefined;
                        var data = (feature && feature.properties && feature.properties[name]) ? feature.properties[name] : undefined;
                        function_.apply(me, [name, e.target, feature, data, e]);
                    };
                };
                this.getLayer(n).on(eventName, makeFunc(n));
            }
        };
        
        this.off = function(eventName, function_){
            delete _events[eventName];
            for(var n in _layers){
                this.getLayer(n).off(eventName);
            }
        };
        
        /**
         * Function updating the leaflet map. It takes a session_id (whereby a server request is made)
         * and an optional callbakc to be executed at the end of the request regardless if the query was succesfull or not
         */
        this.update = function (session_id, optional_onalways) {
        	
            if (!map) {
                return;
            }
    
            //building wait div
            //another option would be to hide the map and then show it again, and put the div
            //inside the map container
            var $waiting = $('<div>').addClass('mapWaiter').addClass("waiting");
            var $mapC = $(map._container); //see leaflet object in browser debugger
            $waiting.html("UPDATING MAP...");
            //FIXME: should be harmless. We need it cause mapWaiter has position:absolute
            $mapC.parent().css('position', 'relative');
            $waiting.appendTo($mapC.parent());
    
            var me = this;
    
            $.post('query_simulation_data', JSON.stringify({session_id: session_id}), function (data, textStatus, jqXHR) {
                
//                function resetHighlight(mouseEvent) {
//                    //mouseEvent is a mouse event leaflet object, see
//                    //http://leafletjs.com/reference.html#event-objects
//                    gmpeLayer.resetStyle(mouseEvent.target);
//                    if (gmpechart.is(':visible')) {
//                        gmpechart.hide();
//                    }
//                }
//    
//                function onEachFeatureFcn(feature, layer) {
//                    layer.on({
//                        //click: showPopup,
//                        mouseover: highlightFeature,
//                        mouseout: resetHighlight
//    //                    click: zoomToFeature
//                    });
//                }

                var n;
                
                for(n in _layers){
                	me.removeData(n);
                }
                
                if (!data.features || !data.features.length) {
                    return;
                }
    
                for(n in _layers){
                	if(n in data.captions){
                		me.addData(n, data.features);
                	}
                }
                
                me.fitBounds(false);
    
            }, "json").fail(function () {
                //NOTE: we SHOULD NEVER BE here (SEE SERVER SIDE CODE). LEFT HERE FOR SAFETY
            }).always(function () {
                //remove wait div
                $waiting.remove();
                if (optional_onalways) {
                    optional_onalways();
                }
            });
        };
    }
    
    crvn.initMap = function(mapId){
    	if(!crvn.map){ crvn.map = new MapManager(mapId); }
    	return crvn.map;
    };
    
}
)(caravan);