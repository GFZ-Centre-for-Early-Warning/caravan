/* 
 * @author Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>), Marc Wieland <mwieland(at)gfz-potsdam.de>
 * @date Mon October 10 2014, 21:09
 */
function MapManager(mapElementId, optional_callback) {
    var map;
    var baseLayer;
    var gmpeLayer; //instanceof 
    var leaf = L;
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
    //add scale:
    leaf.control.scale().addTo(map);

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
//        alert(e.latlng); // e is an event object (MouseEvent in this case)
    });
    //set default:
    setLatLon();

    if (optional_callback) {
        optional_callback();
    }

    this.getMap = function () {
        return map;
    };
    //var marker = L.marker([51.5, -0.09]).addTo(map);

    var epicenter = undefined;
    this.epicenter = function (lat, lon, zoom) {
        if (!arguments || !arguments.length) {
            if (!epicenter) {
                return undefined;
            }
            var latlng = epicenter.getLatLng();
            return [latlng.lat, latlng.lng];
        } else {
            if (!epicenter) {
                epicenter = leaf.marker([lat, lon], {icon:  leaf.icon({iconUrl:'caravan/static/imgs/epi.png'}) }).addTo(map);
            } else {
                var latlng = epicenter.getLatLng();
                if (latlng.lat == lat && latlng.lng == lon) {
                    return;
                }
                epicenter.setLatLng([lat, lon]);
            }
            if (zoom) {
                this.fitBounds(true);
            }
        }
    };

    var ipeMin = 5;
    var ipeMax = 10;

    this.ipeBounds = function () {
        if (!arguments || arguments.length === 0) {
            return [ipeMin, ipeMax];
        }
        ipeMin = arguments[0];
        ipeMax = arguments[1];
    };

    function rgbToHex(r, g, b) {
//        var componentToHex = function (c) {
//            var hex = c.toString(16);
//            return hex.length === 1 ? "0" + hex : hex;
//        };
//        return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);

        r = r.toString(16);
        g = g.toString(16);
        b = b.toString(16);
        return "#" + (r.length === 1 ? "0" + r : r) + (g.length === 1 ? "0" + g : g) + (b.length === 1 ? "0" + b : b);
    }


    var getWarmColorFcn = function (min, max) {

        //var minC = 0;
        var maxC = 256 * 3.0 - 1;

        //y = minC + (maxC - minC) * (x-min) / (max -min) 

        //var denom = max - min + 0.0; //converts to float, right?
        //var denomC = maxC; //maxC - minC;

        var convertFcn = getLinearTransform(min, max, 0, maxC);

        return function (value) {
            var cconv = convertFcn(value); // denomC * (value - min) / denom;

            var index = 2 - pInt(cconv / 256.0);
            var val = 255 - (cconv % 256);

            var components = [255, 255, 255];
            components[index] = pInt(0.5 + val); //necessary in color conversion
            for (var i = index + 1; i < components.length; i++) {
                components[i] = 0;
            }
            return rgbToHex.apply(this, components);
        };
    };

    this.getColorMapLegend = function (width, height, optional_hide_legend) {
        var div = $('<div>').attr('id', 'caz').css({'width': width, 'height': height});

        var minI = ipeMin;
        var maxI = ipeMax;

        var colorFcn = getWarmColorFcn(minI, maxI);
        var intensity;

        //get maximum decimal digits:
        var maxdd = Math.log((maxI - minI) / (width > height ? width : height)) / Math.LN10;
        //the function above gives an approximation of the unsupported log!0. See
        //https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log10

        maxdd = maxdd < 0 ? -Math.floor(maxdd) : Math.ceil(maxdd);

        if (width > height) {
            var max = pInt(div.css('width'));
            var converFcn = getLinearTransform(0, max, minI, maxI); //defined in common.js 
            for (var i = 0; i < max; i++) {
                intensity = converFcn(i);
                var span = $('<span>').css({'padding': 0, 'margin': 0, border: '0px', 'width': '1px', 'height': '100%', 'display': 'inline-block', 'background': colorFcn(intensity)});
                span.attr('title', 'value: ' + intensity.toFixed(maxdd));
                span.appendTo(div);
            }
            if (!optional_hide_legend) {
                var $div_c = $('<div>').css('display', 'inline-block');
                $div_c.append($('<div>').html(minI)).append(div).append($('<div>').html(maxI));
                $div_c.children().css({'vertical-align': 'middle', 'display': 'inline-block'});
                div = $div_c;
            }
        } else {
            var max = pInt(div.css('height'));
            var converFcn = getLinearTransform(0, max, minI, maxI); //defined in common.js 
            for (var i = max; i >= 0; i--) {
                intensity = converFcn(i);
                var span = $('<span>').css({'padding': 0, 'margin': 0, border: '0px', 'height': 1, 'display': 'block', 'background': colorFcn(intensity)});
                span.attr('title', 'value: ' + intensity.toFixed(maxdd));
                span.appendTo(div);
            }
            if (!optional_hide_legend) {
                var $div_c = $('<div>').css('display', 'inline-block');
                $div_c.append($('<div>').html(maxI)).append(div).append($('<div>').html(minI)).css('text-align', 'center');
                div = $div_c;
            }
        }


        return div;
    };


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

//        var offset = $mapC.offset();
//        $waiting.css({'position':'absolute', 'width':$mapC.outerWidth(false),'height':$mapC.outerHeight(false),"left":offset.left,"top":offset.top});
//        $waiting.css("background", "url('static/imgs/wait1.gif') no-repeat center");
//        $waiting.appendTo($('body'));

        var me = this;

        $.post('query_gmpe', JSON.stringify({session_id: session_id}), function (data, textStatus, jqXHR) {

            if (gmpeLayer !== undefined) {
                map.removeLayer(gmpeLayer);
            }
            gmpeLayer = undefined;

            //var percentiles_caption = data.percentiles_caption;
            var ipeColorFcn = getWarmColorFcn(ipeMin, ipeMax);

            //instantiate once leaflet (faster lookup)
            var leaflet = L;


            var gmpechart;

            function getChart(geojson_feature) {
                var $plotTitle, $plot, $xaxis, $yaxis;
                if (!gmpechart) {
                    //DONT ADD LEGEND IN FLOT: IS A MESS. PROVIDE CUSTOM DIV WITH CSS
                    $plot = $('<div class=plot>');
                    $plotTitle = $('<div class=plotTitle>');
                    $xaxis = $("<div class='axisLabel xaxisLabel'></div>").text('Estimated fatalities');
                    $yaxis = $("<div class='axisLabel yaxisLabel'></div>").text('Prob. (%)'); //this cannot be higher than plot height

//                    gmpechart = $('<div>').addClass('skinnable-panel raised plotContainer').append($plotTitle).
//                            append(
//                                $('<div>').append($yaxis).append($plot))
//                                .append($xaxis);

                    gmpechart = $('<div>').addClass('skinnable-panel raised plotContainer').append($plotTitle).
                            append($plot);

                    gmpechart.appendTo($mapC.parent());
                } else {
//                    gmpechart.empty(); //for safety. Is it removed later?
                    $plot = gmpechart.find('.plot'); //.empty();
                    $plotTitle = gmpechart.find('.plotTitle');
                    $xaxis = gmpechart.find('.xaxisLabel');
                    $yaxis = gmpechart.find('.yaxisLabel');
                }

                //restore divs whichmight have been set when no data is available (see below)
                $plot.show(); //might have benn set hidden
                $plotTitle.html(""); //to be sure

                gmpechart.show(); //NEEDED, SO THAT FLOT RESIZES PROPERLY THE CHART

                //see example on http://stackoverflow.com/questions/13817403/title-for-x-and-y-axis-in-flot-graph
                //NOTE: needs to set labelWidth on yaxis and labelHeight on x axis
                //(see below)


                //chart color: 
                //so we set colors with rgba
                //custom colors:
                //gold: #FFD700 (255, 215,0)
                //orange: #FFA500 (255, 165,0)
                //FIXME / PROBLEMS:
                //1) fill sets the opacity. However, when setting fill color, it seems to override the property
                //2)The color in the legend seems to take the bar BORDER color. We would like to 
                //display the fill color (imagine red bars with black border: red should be displayed)
                //needs to be checked

                var chart_options = {
                    series: {
                        lines: {show: false},
                        points: {show: false},
                        bars: {
                            show: true,
//                            fill:0.7, //opacity
                            color: '#FFD700',
                            fillColor: 'rgba(255,215,0,0.9)'
                        }
                    },
                    xaxis: {
                        labelHeight: 15,
                        tickLength: 10,
                        reserveSpace: true
                                //FIXME: should align tick CENTERED, but apparently there is no such featrure.
                                //We just put space BEFORE, but is ugly
                                //Note: there is also a bar align property.. heve a try?
                                //see https://github.com/flot/flot/blob/master/API.md#customizing-the-data-series
                                //ticks: [0.5, 1.5, 2.5, 3.5, 4.5],
//                        ticksLength: 5,
//                        tickFormatter: function (val, axis) {
//                            val = pInt(val);
//                            return val < 0 || val >= percentiles_caption.length ? "" : percentiles_caption[val]; //+ "%";
//                        }
                    },
                    yaxis: {
                        labelWidth: 20,
                        tickLength: 10,
                        reserveSpace: true//,
//                        tickFormatter: function (val, axis) {
//                            val = (100*val.toFixed(4));
//                            return val + "%"; //+ "%";
//                        }
//                        ticks: function (axis) {
//                            var min = axis.min;
//                            var max = axis.max;
//
//                            var step = 1; //provide a POSITIVE number N = C*10^k, where C in [1,5]
//
//                            //first get a "valid step", i.e. a step which does not write tons of ticks
//                            //we set a max number of ticks:
//                            var maxTickNum = 10; //note:10 excluded!
//                            //and then readjust the step
//                            var span = max - min;
//                            //set step to 
//                            var multiplicator = step === 1 || step % 10 === 0 ? 5 : 2;
//                            while (span / step >= maxTickNum) {
//                                step *= multiplicator;
//                                multiplicator = multiplicator === 5 ? 2 : 5;
//                            }
//
//                            min = min % step === 0 ? min : step * pInt((min / step));
//                            max = max % step === 0 ? max : step * pInt((max / step));
//
//                            var res = [];
//                            var val = min;
//                            do {
//                                res.push([val, val + ""]); //value and string repr
//                                val += step;
//                            } while (val <= max);
//
//                            return res;
//                        }
                    },
                    legend: {
                        container: $plotTitle,
                        show: false
//                        position: "ne"
                    }
                };

                var geojsondata = geojson_feature.properties[P_FIELD_FAT];
                if (geojsondata && geojsondata.length && geojsondata.length > 2) {
                    //use flot library:
                    var len = geojsondata.length;

                    var fatalities = new Array(len - 2); //preallocate array is faster? should be harmless in any case

                    var x = pInt(geojsondata[0]);
                    var step = geojsondata[1];

                    //set bars width in flot
                    chart_options.series.bars.barWidth = step;

                    for (var i = 2; i < len; i++) {
                        fatalities[i] = [x, geojsondata[i]];
                        x += step;
                    }
                    //round to int (should be even)
//                    var lenn = pInt(fatalities.length / 2);
//                    for (var i = 0; i < lenn; i++) {
//                        var idx = 2 * i;
//                        var y = geojsondata[idx + 1]; //pInt(0.5+geojsondata[idx + 1]*100)
//                        fatalities[i] = [geojsondata[idx], y];
//                    }

                    //this empties the content:
                    $.plot($plot, [{label: 'Fatalities probability distribution', data: fatalities}/*, {label: 'Ipe dist.', data: gmpe}*/], chart_options);
                    //So we append now axes:
//                    $xaxis.appendTo($plot);
//                    $yaxis.appendTo($plot);

                    //last stuff: padding cannot be too much on plotContainer, otherwise plot is too little
                    //so, override padding on plotContainer here, and set a title padding (cause title needs space)
                    //THIS IS UGLY but we are stuck with flot...
//                    gmpechart.css('padding', 1);
//                    $plotTitle.css({'padding-top': 1, 'padding-right': 8, 'padding-left': 8, 'padding-bottom': 1});
                } else {
                    $plot.hide();
                    $plotTitle.html("No data available");
                    //return null;
                }
                return gmpechart;

//                //build chart: example taken from: http://bost.ocks.org/mike/bar/1/
//                //FIXME: vertical bars? it seems we need svg for that (see http://bost.ocks.org/mike/bar/3/)
//                //For the moment leave it like this
//                var retelm = gmpechart.get(0);
//                var d3elm = d3.select(retelm);
//                d3elm.selectAll("div")
//                        .data(feature.properties[P_FIELD_FAT])
//                        .enter().append("div").attr('class', 'bar')
//                        .style("width", function (d) {
//                            //note: we should need to be safer than this:
//                            //leaflet popup maxWidth should control this width.
//                            //for the moment as the former is 300px we do like this:
//                            return pInt(0.5 + 300 * d / 12.0) + "px";
////                            return d * 20 + "px";
//                        });
//
//                //add text separately (for each bar)
//                //see https://github.com/mbostock/d3/wiki/Selections#text
//                d3elm.selectAll("div").text(function (d, i) {
//                    return percentiles_caption[i] + "th percentile: " + d.toFixed(2);
//                });
//
//
//                //gmpechart.appendTo($('body'));
//                return retelm;
            }

            //getChart({target:{feature:{properties:{percentiles:[9,5,6,3,-1]}}}});

            function showPopup(mouseEvent) {
                //mouseEvent is a mouse event leaflet object, see
                //http://leafletjs.com/reference.html#event-objects
                var chart = getChart(mouseEvent.target.feature);

                if (chart && !chart.is(':visible')) {
                    chart.show();
                }
                //se doc: http://leafletjs.com/reference.html#popup
//                leaf.popup()
//                        .setLatLng(feature.latlng)
//                        .setContent(getChart(feature)) //'<p>Hello world!<br />This is a nice popup.</p>')
//                        .openOn(map); //The same as map.openPopup(popup).
            }

            function styleFcn(feature) {
                var val = ipeColorFcn(feature.properties[P_FIELD_GMPE][2]); //pInt(0.5 + feature.properties.percentiles[2]);
                return {
                    radius: 10,
                    fillColor: val, //colors[val + 1], // '#0B0B3B',
                    color: '#000000', //colors[val + 1], //'#0B0B3B',
                    opacity: 1, //should be set the half of the value below cause they overlap?? fix me... 
                    weight: 0,
                    fillOpacity: 0.5
                };
            }

            var isNotIeNorOpera = !leaf.Browser.ie && !leaf.Browser.opera;
            function highlightFeature(mouseEvent) {
                //mouseEvent is a mouse event leaflet object, see
                //http://leafletjs.com/reference.html#event-objects
                var layer = mouseEvent.target;
                layer.setStyle({
//                    radius: 8,
//                    fillColor: '#0B0B3B',
//                    color: '#000000',
//                    opacity: 1,
                    weight: 1,
                    fillOpacity: 0.75
                });
                if (isNotIeNorOpera) {
                    layer.bringToFront();
                }
                //info.update(layer.feature.properties);
                showPopup(mouseEvent);
            }

            function resetHighlight(mouseEvent) {
                //mouseEvent is a mouse event leaflet object, see
                //http://leafletjs.com/reference.html#event-objects
                gmpeLayer.resetStyle(mouseEvent.target);
                if (gmpechart.is(':visible')) {
                    gmpechart.hide();
                }
            }

            function onEachFeatureFcn(feature, layer) {
                layer.on({
                    //click: showPopup,
                    mouseover: highlightFeature,
                    mouseout: resetHighlight
//                    click: zoomToFeature
                });
            }

            if (!data.features || !data.features.length) {
                return;
            }

            //var markerz = new Array(data.features.length);
            //var ik = 0;
            gmpeLayer = leaflet.geoJson(data.features, {
                style: styleFcn,
                onEachFeature: onEachFeatureFcn/*,
                 pointToLayer: function (feature, latlng) {
                 var mrk = leaflet.circleMarker(latlng);
                 return mrk;
                 }*/
            }).addTo(map);

            //add a zoom resizer: see http://stackoverflow.com/questions/17382012/is-there-a-way-to-resize-marker-icons-depending-on-zoom-level-in-leaflet (not implemented yet)


            //fit bounds: a small delay is sometimes needed to properly zoom
//            var DELAY = 250;
//            setTimeout(function () {
//                map.fitBounds(gmpeLayer.getBounds());
//            }, DELAY);

            me.fitBounds(false);

        }, "json").fail(function () {
            var s = 5;
//            _stop($textarea, "Error " + arguments[0].status + ":\n" + arguments[0].statusText);

            //NOTE: we SHOULD NEVER BE here (SEE SERVER SIDE CODE). LEFT HERE FOR SAFETY
        }).always(function () {
            //remove wait div
            $waiting.remove();
            if (optional_onalways) {
                optional_onalways();
            }
        });
    };

    this.fitBounds = function (includeEpicenter) {
        var arr = gmpeLayer ? [gmpeLayer] : [];
        if (includeEpicenter && epicenter) {
            arr.push(epicenter);
        }
        if (!arr) {
            return;
        }

        //fit bounds: a small delay is sometimes needed to properly zoom
        var DELAY = 250;
        setTimeout(function () {
            var group = new leaf.featureGroup(arr);
            map.fitBounds(group.getBounds());
        }, DELAY);

//        var group = new leaf.featureGroup(arr);
//        map.fitBounds(group.getBounds());
    }; 

    
    //NOTE FOR RICARDO:GOING TO MOVE CODE TO legend.js next time
    //
    //checkbox setup and functionality     
    layerOptions = leaf.control.layers();
    layerOptions.onAdd = function (map) {
        this._div = leaf.DomUtil.create('div', 'layerOptions');
        this._div.innerHTML =
                '<label class="layerElements"><input type="checkbox" class="radio" value="A" name="oneSelectable" id="checkboxInten">Intensities</input></label>'+
                '<label><img src="caravan/static/imgs/layers.png" style="float:right" id="expand"/></label><br>' +
                '<label class="layerElements"><input type="checkbox" class="radio" value="B" name="oneSelectable" id="checkboxFata" >Fatalities </input></label><br>' +
                '<label class="layerElements"><input type="checkbox" class="radio" value="C" name="oneSelectable" id="checkboxEcon">Economic Losses(EUR)</input></label>';
        return this._div;
    };
    
   layerOptions.addTo(map);
       
   $(".layerElements").hide();
        
    $(".layerOptions").mouseover(function () {
        $(".layerElements").show();
        $(".layerOptions").mouseout(function () {
            $(".layerElements").hide();
        });
    });
    
    var $allIdMaps = $("#fatalMap,#econMap,#colorMap,#intenFutureMap");
    //mutually exclusive function
          $("input:checkbox").on('click', function () {
            var $box = $(this);
            if ($box.is(":checked")) {
                var group = "input:checkbox[name='" + $box.attr("name") + "']";
                $(group).prop("checked", false);
                $box.prop("checked", true);
            } else {
                $box.prop("checked", false);               
            }
        });
                
        $("#checkboxInten").change(function () {
            if ($(this).is(":checked")) {
                $allIdMaps.hide();
                $("#intenFutureMap").show();
            } else {
                $("#intenFutureMap").hide();
            }
        });

        $("#checkboxFata").change(function () {
            if ($(this).is(":checked")) {
                $allIdMaps.hide();
                $("#fatalMap").show();             
            } else {
                $("#fatalMap").hide();
            }
        });

        $("#checkboxEcon").change(function () {
            if ($(this).is(":checked")) {
                $allIdMaps.hide();
                $("#econMap").show();
            } else  {              
                $("#econMap").hide();               
            }
        });
        //TODO:MOVE CODE IN LEGEND.JS
    legendImplement();
}