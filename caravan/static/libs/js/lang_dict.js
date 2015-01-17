//elements with data-title=key will search the key, retrieve the title and set their html
//elements with data-doc=key will search the key, retrieve the title and display it on focus
caravan.dict = (function(){
	var $ = jQuery;
	
	//THE LINE BELOW UNTIL <END> IS AUTO-GENERATED, DO NOT MODIFY
	var lang_dict = {
en_1 : {CentralAsiaEmca : "Central Asia Intensity prediction Equation, based on epicentral distance<br>Magnitude bounds: [4.6, 8.3]<br>Distance bounds: [0, 600]<br><i>Intensity prediction equations for Central Asia (Bindi et al.). Geophys. J. Int. (2011) 187, 327\u2013337</i>",
GlobalWaHyp : "Global Intensity prediction Equation, based on hypocentral distance<br>Magnitude bounds: [5, 7.9]<br>Distance bounds: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
GlobalWaRup : "Global Intensity prediction Equation, based on rupture distance<br>Magnitude bounds: [5, 7.9]<br>Distance bounds: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
advanced_text : ["advanced", "Advanced", "Toggle advanced settings visibility"],
aoi : ["Area", "Area", ""],
aoi_i_ref : ["intensity reference", "I<sub>ref</sub>", "Intensity reference (Area = circle around epicenter where intensity &ge; I<sub>ref</sub>)"],
aoi_intensity_ref : ["area of interest (according to intensity reference)", "where I &ges; I<sub>ref</sub>", "Perform calculations only on the area where intensity assessment is greater than I<sub>ref</sub> (see 'Advanced')"],
aoi_km_step : ["A(I<sub>ref</sub>) step", "A(I<sub>ref</sub>) step [Km]", "Choose the step (in Km) used in the computation of the target Area (circle around epicenter where intensity &ge; I<sub>ref</sub>)"],
aoi_map_rect : ["", "Map current rect.", "Perform calculations only on the area currently displayed in the map"],
cancel_text : ["cancel", "Cancel", "Cancel running simulation"],
choose_selected_event : ["choose selected event", "Choose selected", "Choose selected event and input its values in the Event Parameters"],
dep : ["depth", "Depth [km]", "Depth [km]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
dip : ["dip", "Dip [deg]", "Dip [degree]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
econ_loss : "Economic losses",
event_params_text : "Event Parameters",
fatal : "Fatalities",
gm_only : ["ground motion only", "Ground motion only", "Ground motion only"],
goback_text : ["go back", "Go back", "Restore parameter window"],
hide_panel : "Hide panel",
intens : "Macroseismic Intensity",
ipe : ["intensity prediction equation", "Ipe", "Intensity prediction equation"],
lat : ["latitude", "Latitude [deg]", "Latitude [degree]<p>You can also specify it as (non-scalar) normal distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the mean and standard deviation, respectively"],
lon : ["longitude", "Longitude [deg]", "Longitude [degree]<p>You can also specify it as (non-scalar) normal distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the mean and standard deviation, respectively"],
mag : ["magnitude", "Magnitude [mw]", "Magnitude [mw]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
mcerp_npts : ["distribution number of points", "Dist. npts", "Choose the number of points of the distributions (if any specified)"],
model_params_text : "Model Parameters",
query_events : ["query events", "Query events", "Query events from the selected catalog matching the given criteria"],
query_events_from_catalog : "Query historical event from catalog and set it in the Event Parameters",
run_text : ["run", "Run", "Start simulation with the given parameters"],
show_info : "show help when moving to a component",
show_panel : "Show panel",
sof : ["style of Faulting", "Style of Faulting", "Select the style of Faulting"],
source_extended_text : "Extended",
source_point_text : "Point",
str : ["strike", "Strike [deg]", "Strike [degree]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
tess_ids : ["tessellation(s)", "Tessellation(s)", "Choose the target tessellations (multiple selection allowed)"],
tim : ["Time", "Time [YYYY MM DD]", "Set time (in the format YYYY MM DD, You can also use commas or slashes \"/\" as separators)"]}
,
cn : {CentralAsiaEmca : "\u57fa\u4e8e\u9707\u4e2d\u8ddd\u7684\u4e2d\u4e9a\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b<br>\u5e45\u5ea6\u8303\u56f4: [4.6, 8.3]<br>\u8ddd\u79bb\u8303\u56f4: [0, 600]<br><i>Intensity prediction equations for Central Asia (Bindi et al.). Geophys. J. Int. (2011) 187, 327\u2013337</i>",
GlobalWaHyp : "\u57fa\u4e8e\u9707\u4e2d\u8ddd\u7684\u5168\u7403\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b<br>\u5e45\u5ea6\u8303\u56f4: [5, 7.9]<br>\u8ddd\u79bb\u8303\u56f4: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
GlobalWaRup : "\u57fa\u4e8e\u65ad\u88c2\u8ddd\u7684\u5168\u7403\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b<br>\u5e45\u5ea6\u8303\u56f4: [5, 7.9]<br>\u8ddd\u79bb\u8303\u56f4: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
advanced_text : ["\u9ad8\u7ea7", "\u9ad8\u7ea7", "\u89e6\u53d1\u9ad8\u7ea7\u8bbe\u7f6e\u53ef\u89c6\u6027"],
aoi : ["\u9762\u79ef", "\u9762\u79ef", ""],
aoi_i_ref : ["\u5f3a\u5ea6\u53c2\u7167", "\u5f3a\u5ea6<sub>\u53c2\u7167</sub>", "\u5f3a\u5ea6\u53c2\u7167 (\u9762\u79ef = \u9707\u4e2d\u5468\u56f4\u5706\uff0c\u8fd9\u91cc\u5f3a\u5ea6 &ge; \u5f3a\u5ea6<sub>\u53c2\u7167</sub>)"],
aoi_intensity_ref : ["\u611f\u5174\u8da3\u533a\u57df (\u6309\u7167\u5f3a\u5ea6\u53c2\u7167)", "\u8fd9\u91cc\u5f3a\u5ea6 &ges; \u5f3a\u5ea6<sub>\u53c2\u7167</sub>", "\u4ec5\u5c31\u5f3a\u5ea6\u8bc4\u4f30\u5927\u4e8e\u5f3a\u5ea6<sub>\u53c2\u7167</sub>\u7684\u533a\u57df\u8fdb\u884c\u8ba1\u7b97 (\u89c1 '\u9ad8\u7ea7')"],
aoi_km_step : ["\u9762\u79ef(\u5f3a\u5ea6<sub>\u53c2\u7167</sub>) \u8ba1\u7b97\u6b65\u9aa4", "\u9762\u79ef(\u5f3a\u5ea6<sub>\u53c2\u7167</sub>) \u8ba1\u7b97\u6b65\u9aa4 [\u5343\u7c73]", "\u9009\u62e9\u7528\u4e8e\u76ee\u6807\u9762\u79ef\u8ba1\u7b97\u7684\u6b65\u9aa4\uff08\u5355\u4f4d\u4e3a\u5343\u7c73\uff09(\u9707\u4e2d\u5468\u56f4\u5706\uff0c\u8fd9\u91cc\u5f3a\u5ea6 &ge; \u5f3a\u5ea6<sub>\u53c2\u7167</sub>)"],
aoi_map_rect : ["", "\u5730\u56fe\u5f53\u524d\u77e9\u5f62\u533a", "\u4ec5\u5c31\u5f53\u524d\u5730\u56fe\u4e2d\u663e\u793a\u7684\u533a\u57df\u8fdb\u884c\u8ba1\u7b97"],
cancel_text : ["\u53d6\u6d88", "\u53d6\u6d88", "\u53d6\u6d88\u6a21\u62df"],
choose_selected_event : ["choose selected event", "Choose selected", "Choose selected event and input its values in the \u4e8b\u4ef6\u53c2\u6570"],
dep : ["\u6df1\u5ea6", "\u6df1\u5ea6 [\u5343\u7c73]", "\u6df1\u5ea6 [\u5343\u7c73]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u5747\u5300\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u6700\u4f4e\u503c\u548c\u6700\u9ad8\u503c"],
dip : ["\u503e\u89d2", "\u503e\u89d2 [\u5ea6]", "\u503e\u89d2 [\u5ea6\u6570]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u5747\u5300\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u6700\u4f4e\u503c\u548c\u6700\u9ad8\u503c"],
econ_loss : "\u7ecf\u6d4e\u635f\u5931",
event_params_text : "\u4e8b\u4ef6\u53c2\u6570",
fatal : "\u6b7b\u4ea1",
gm_only : ["\u4ec5\u5730\u8868\u8fd0\u52a8", "\u4ec5\u5730\u8868\u8fd0\u52a8", "\u4ec5\u5730\u8868\u8fd0\u52a8"],
goback_text : ["\u8fd4\u56de", "\u8fd4\u56de", "\u6062\u590d\u53c2\u6570\u7a97\u53e3"],
hide_panel : "Hide panel",
intens : "\u5b8f\u89c2\u70c8\u5ea6",
ipe : ["\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b", "\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b", "\u5f3a\u5ea6\u9884\u6d4b\u65b9\u7a0b"],
lat : ["\u7eac\u5ea6", "\u7eac\u5ea6 [\u5ea6]", "\u7eac\u5ea6 [\u5ea6\u6570]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u6b63\u592a\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u5e73\u5747\u503c\u548c\u6807\u51c6\u5dee"],
lon : ["\u7ecf\u5ea6", "\u7ecf\u5ea6 [\u5ea6]", "\u7ecf\u5ea6 [\u5ea6\u6570]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u6b63\u592a\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u5e73\u5747\u503c\u548c\u6807\u51c6\u5dee"],
mag : ["\u5e45\u5ea6", "\u5e45\u5ea6 [\u5146\u74e6]", "\u5e45\u5ea6 [\u5146\u74e6]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u5747\u5300\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u6700\u4f4e\u503c\u548c\u6700\u9ad8\u503c"],
mcerp_npts : ["\u5206\u5e03\u70b9\u6570", "\u5206\u5e03\u70b9\u6570", "\u9009\u62e9\u5206\u5e03\u70b9\u6570 (\u5728\u6307\u5b9a\u60c5\u51b5\u4e0b)"],
model_params_text : "\u6a21\u578b\u53c2\u6570",
query_events : ["query events", "Query events", "Query events from the selected catalog matching the given criteria"],
query_events_from_catalog : "Query historical event from catalog and set it in the \u4e8b\u4ef6\u53c2\u6570",
run_text : ["\u8fd0\u884c", "\u8fd0\u884c", "\u4f7f\u7528\u7ed9\u5b9a\u53c2\u6570\u5f00\u59cb\u6a21\u62df"],
show_info : "show help when moving to a component",
show_panel : "Show panel",
sof : ["\u65ad\u5c42\u6837\u5f0f", "\u65ad\u5c42\u6837\u5f0f", "\u9009\u62e9\u65ad\u5c42\u6837\u5f0f"],
source_extended_text : "\u6269\u5c55",
source_point_text : "\u70b9",
str : ["\u8d70\u5411", "\u8d70\u5411 [\u5ea6]", "\u8d70\u5411 [\u5ea6\u6570]<p>\u60a8\u4e5f\u53ef\u4ee5\u901a\u8fc7\u8f93\u5165\u4e00\u7cfb\u5217\u6570\u5bf9\u5c06\u5176\u6307\u5b9a\u4e3a\uff08\u975e\u6807\u91cf\uff09\u5747\u5300\u5206\u5e03\uff08\u901a\u8fc7\u7a7a\u683c\u3001\u9017\u53f7\u6216\u5206\u53f7\u5c06\u5176\u8fdb\u884c\u5206\u9694\uff09<br>\u5206\u522b\u8868\u793a\u6700\u4f4e\u503c\u548c\u6700\u9ad8\u503c"],
tess_ids : ["\u8868\u9762\u7ec6\u5316", "\u8868\u9762\u7ec6\u5316", "\u9009\u62e9\u76ee\u6807\u8868\u9762\u7ec6\u5316 (\u53ef\u591a\u9009)"],
tim : ["\u65f6\u95f4", "\u65f6\u95f4 [\u5e74 \u6708 \u65e5]", "\u8bbe\u7f6e\u65f6\u95f4 (\u4f7f\u7528 \u5e74 \u6708 \u65e5 \u683c\u5f0f, \u60a8\u4e5f\u53ef\u4ee5\u4f7f\u7528\u9017\u53f7\u6216\u8005\u659c\u6760\"/\"\u4f5c\u4e3a\u5206\u9694)"]}
,
de : {CentralAsiaEmca : "Zentralasiatische Intensit\u00e4tsvorhersagegleichung, basierend auf der Distanz zum Epizentrum<br>Magnitudengrenzen: [4.6, 8.3]<br>Distanzgrenzen: [0, 600]<br><i>Intensity prediction equations for Central Asia (Bindi et al.). Geophys. J. Int. (2011) 187, 327\u2013337</i>",
GlobalWaHyp : "Globale Intensit\u00e4tsvorhersagegleichung, basierend auf der Distanz zum Hypozentrum<br>Magnitudengrenzen: [5, 7.9]<br>Distanzgrenzen: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
GlobalWaRup : "Globale Intensit\u00e4tsvorhersagegleichung, basierend auf der Distanz zur Verwerfung<br>Magnitudengrenzen: [5, 7.9]<br>Distanzgrenzen: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
advanced_text : ["erweiterte", "Erweitert", "Verberge erweiterte Optionen"],
aoi : ["Gebiet", "Gebiet", ""],
aoi_i_ref : ["Referenzintensit\u00e4t", "I<sub>ref</sub>", "Referenzintensit\u00e4t (Gebiet = Kreis um Epizentrum wo Intensit\u00e4t &ge; I<sub>ref</sub>)"],
aoi_intensity_ref : ["Ausgew\u00e4hltes Gebiet (entsprechend der Intensit\u00e4tseingabe)", "where I &ges; I<sub>ref</sub>", "Berechnung nur auf dem Gebiet durchf\u00fchren wo Intensit\u00e4tsabsch\u00e4tzung gr\u00f6\u00dfer ist als I<sub>ref</sub> (siehe 'Erweitert')"],
aoi_km_step : ["A(I<sub>ref</sub>) Umkreis", "A(I<sub>ref</sub>) Umkreis [Km]", "W\u00e4hle den Umkreis (in Km) f\u00fcr die Berechnung in dem ausgew\u00e4hlten Gebiet (Kreis um das Epizentrum wo Intensit\u00e4t &ge; I<sub>ref</sub>)"],
aoi_map_rect : ["", "ausgew\u00e4hltes Rechteck auf der Karte", "F\u00fchre Berechnung nur f\u00fcr das auf der Karte ausgew\u00e4hlte Gebiet durch"],
cancel_text : ["abbrechen", "Abbrechen", "Laufende Simulation abbrechen"],
choose_selected_event : ["choose selected event", "Choose selected", "Choose selected event and input its values in the Ereignis Parameter"],
dep : ["Tiefe", "Tiefe [km]", "Tiefe [km]<p>Es ist m\u00f6glich dies als (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die unteren und oberen Werte darstellen"],
dip : ["Neigung", "Neigung [Grad]", "Neigung [Grad]<p>Es ist m\u00f6glich dies als (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die unteren und oberen Werte darstellen"],
econ_loss : "\u00d6konomischer Verlust",
event_params_text : "Ereignis Parameter",
fatal : "Todesopfer",
gm_only : ["Nur Bodenbewegung", "Nur Bodenbewegung", "Nur Bodenbewegung"],
goback_text : ["geh zur\u00fcck", "Geh zur\u00fcck", "Z\u00fcruck zum Eingabefenster"],
hide_panel : "Verberge Optionen",
intens : "Makroseismische Intensit\u00e4t",
ipe : ["Intensit\u00e4tsvorhersagegleichung", "IPE", "Intensit\u00e4tsvorhersagegleichung"],
lat : ["Breitengrad", "Breitengrad", "Breitengrad<p>Es ist m\u00f6glich dies als normale (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die durchschnittliche- und Standartabweichung darstellen"],
lon : ["L\u00e4ngengrad", "L\u00e4ngengrad", "L\u00e4ngengrad<p>Es ist m\u00f6glich dies als normale (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die durchschnittliche- und Standartabweichung darstellen"],
mag : ["Magnitude", "Magnitude [mw]", "Magnitude [mw]<p>Es ist m\u00f6glich dies als (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die unteren und oberen Werte darstellen"],
mcerp_npts : ["Anzahl Punkte der Verteilung", "Anz. Punkte Vert.", "W\u00e4hle die Anzahl der Punkte der Verteilung (falls spezifiziert)"],
model_params_text : "Modell Parameter",
query_events : ["query events", "Query events", "Query events from the selected catalog matching the given criteria"],
query_events_from_catalog : "Rufe historisches Ereignis vom Katalog ab und nutzte es als Ereignis Parameter",
run_text : ["starte", "Start", "Starte die Simulation mit den ausgew\u00e4hlten Parametern"],
show_info : "Hilfe anzeigen beim Bewegen \u00fcber eine Komponente",
show_panel : "Zeige Optionen",
sof : ["Art der Verwerfung", "Art der Verwerfung", "W\u00e4hle Art der Verwerfung aus"],
source_extended_text : "Erweitert",
source_point_text : "Punkt",
str : ["Streichrichtung", "Streichrichtung [Grad]", "Streichrichtung [Grad]<p>Es ist m\u00f6glich dies als (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die unteren und oberen Werte darstellen"],
tess_ids : ["Tesselation", "Tesselation", "W\u00e4hle Tesselation (mehrere Optionen ausw\u00e4hlbar)"],
tim : ["Zeit", "Zeit [JJJJ MM TT]", "Lege einen Zeitpunkt fest (Im Format JJJJ MM TT, es ist zudem m\u00f6glich mit Kommata oder Querstrichen \"/\" zu trennen)"]}
,
en : {CentralAsiaEmca : "Central Asia Intensity prediction Equation, based on epicentral distance<br>Magnitude bounds: [4.6, 8.3]<br>Distance bounds: [0, 600]<br><i>Intensity prediction equations for Central Asia (Bindi et al.). Geophys. J. Int. (2011) 187, 327\u2013337</i>",
GlobalWaHyp : "Global Intensity prediction Equation, based on hypocentral distance<br>Magnitude bounds: [5, 7.9]<br>Distance bounds: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
GlobalWaRup : "Global Intensity prediction Equation, based on rupture distance<br>Magnitude bounds: [5, 7.9]<br>Distance bounds: [0, 300]<br><i>Intensity attenuation for active crustal regions (Allen et al.). J Seismol (2012) 16:409\u2013433</i>",
advanced_text : ["advanced", "Advanced", "Toggle advanced settings visibility"],
aoi : ["Area", "Area", ""],
aoi_i_ref : ["intensity reference", "I<sub>ref</sub>", "Intensity reference (Area = circle around epicenter where intensity &ge; I<sub>ref</sub>)"],
aoi_intensity_ref : ["area of interest (according to intensity reference)", "where I &ges; I<sub>ref</sub>", "Perform calculations only on the area where intensity assessment is greater than I<sub>ref</sub> (see 'Advanced')"],
aoi_km_step : ["A(I<sub>ref</sub>) step", "A(I<sub>ref</sub>) step [Km]", "Choose the step (in Km) used in the computation of the target Area (circle around epicenter where intensity &ge; I<sub>ref</sub>)"],
aoi_map_rect : ["", "Map current rect.", "Perform calculations only on the area currently displayed in the map"],
cancel_text : ["cancel", "Cancel", "Cancel running simulation"],
choose_selected_event : ["choose selected event", "Choose selected", "Choose selected event and input its values in the Event Parameters"],
dep : ["depth", "Depth [km]", "Depth [km]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
dip : ["dip", "Dip [deg]", "Dip [degree]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
econ_loss : "Economic losses",
event_params_text : "Event Parameters",
fatal : "Fatalities",
gm_only : ["ground motion only", "Ground motion only", "Ground motion only"],
goback_text : ["go back", "Go back", "Restore parameter window"],
hide_panel : "Hide panel",
intens : "Macroseismic Intensity",
ipe : ["intensity prediction equation", "Ipe", "Intensity prediction equation"],
lat : ["latitude", "Latitude [deg]", "Latitude [degree]<p>You can also specify it as (non-scalar) normal distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the mean and standard deviation, respectively"],
lon : ["longitude", "Longitude [deg]", "Longitude [degree]<p>You can also specify it as (non-scalar) normal distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the mean and standard deviation, respectively"],
mag : ["magnitude", "Magnitude [mw]", "Magnitude [mw]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
mcerp_npts : ["distribution number of points", "Dist. npts", "Choose the number of points of the distributions (if any specified)"],
model_params_text : "Model Parameters",
query_events : ["query events", "Query events", "Query events from the selected catalog matching the given criteria"],
query_events_from_catalog : "Query historical event from catalog and set it in the Event Parameters",
run_text : ["run", "Run", "Start simulation with the given parameters"],
show_info : "show help when moving to a component",
show_panel : "Show panel",
sof : ["style of Faulting", "Style of Faulting", "Select the style of Faulting"],
source_extended_text : "Extended",
source_point_text : "Point",
str : ["strike", "Strike [deg]", "Strike [degree]<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers \n(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"],
tess_ids : ["tessellation(s)", "Tessellation(s)", "Choose the target tessellations (multiple selection allowed)"],
tim : ["Time", "Time [YYYY MM DD]", "Set time (in the format YYYY MM DD, You can also use commas or slashes \"/\" as separators)"]}
};
	//<END>
	
	var _langs = function(){
		a = [];
		for(n in lang_dict){
			a.push(n);
		}
		return a;
	};
	
	var lng = "en";
	//for (lng in lang_dict){break;} //sets the first item as default
	var dd = lang_dict[lng];
	
	//lazily create the popup:
	var getHelpDiv = function(){
		var $d = $('#_help_popup_');
		if(!$d.length){
			$d = $('<div>').attr('id','_help_popup_').appendTo(document.body).css({'margin': '-2em 1em 1em 10em', 'padding': '5px', 'display': 'none', 'background-color': 'black', 'color': 'white'});
		}
		return $d;
	};
	
	var isHelpDivVisible = function(){
		var $d = $('#_help_popup_'); //if it doesn;t exists, returns false
		return $d.is(':visible');
	};
    
	var get_ = function(key, index){
		if(!dd || !dd[key]){return "";}
		var dd_ = dd[key];
		if(typeof(dd_) === 'string' ){return dd_;}
		if(dd_.constructor === Array && dd_[index]){return dd_[index];}
		return "";
	};
	
	var showHelp_ = false;
	
	/*THESE ARE PUBLIC METHODS, WILL BE ATTACHED TO THE RETURNED OBJECT
	 * WITHOUT LEADING "_"
	 */
	var _help = function(value){
		if (arguments.length === 0){
			return showHelp_;
		}
		value = arguments[0];
		showHelp_ = value;
		if(value && document.activeElement){
			$(document.activeElement).trigger('focusin.lang');
		}else if(!value && isHelpDivVisible()){
            getHelpDiv().popClose(); //for safety, and because otherwise we have focus 
            //synchronization problems (the div appears and disappears)
        }
	};
	
	var _name = function(key){
	    return get_(key,0);
	};
	var _title = function(key){
	    return get_(key,1);
	};
    
	var _doc = function(key){
	    return get_(key,2);
	};
    
	var _lang = function(){
	    if (arguments.length === 0){
	    	return lng;
	    }else{
	    	lng = arguments[0];
	    	dd = lang_dict[lng];
	    }
		if(!dd){return;}
		var me = this;
			
		$('*[data-title]').each(function(i, elm){
		    var $elm = $(elm);
		    var title = me.title($elm.data('title'));
		    if($elm.is('input')){
			$elm.val(title);
		    }else if($elm.is('img')){
			$elm.attr('alt', title);
		    }else{
			$elm.html(title);
		    }
		});
        
        $(document).on('focusin.lang',function(e){
            var $elm = $(e.target);
            var $d = undefined;
            if(isHelpDivVisible()){
                $d = getHelpDiv(); 
                $d.popClose(); //for safety, and because otherwise we have focus 
                    //synchronization problems (the div appears and disappears)
            }
            if(!showHelp_ || !$elm.data('doc')){return;}
            if(!$d){
                $d = getHelpDiv();
            }
            var doc = me.doc($elm.data('doc'));
            if(!doc){return;}
            $d.html(doc);
            $d.popSlideToggle({invoker: $elm, duration: 100});
        });
        
//		$('*[data-doc]').each(function(i, elm){
//		    var $elm = $(elm);
//		    $elm.off('focusin.lang').on('focusin.lang', function(){
//				var $d = undefined;
//				if(isHelpDivVisible()){
//					$d = getHelpDiv(); 
//					$d.popClose(); //for safety, and because otherwise we have focus 
//					    //synchronization problems (the div appears and disappears)
//				}
//				if(!showHelp_){return;}
//				if(!$d){
//					$d = getHelpDiv();
//				}
//				var doc = me.doc($(this).data('doc'));
//				if(!doc){return;}
//				$d.html(doc);
//				$d.popSlideToggle({invoker: $(this), duration: 100, toolTip: true});
//			});
//		});
	};
	
    //return the object wwith the given properties defined above
	var dict={
		name : _name,
		title : _title,
		lang: _lang,
		doc: _doc,
		help: _help,
		langs : _langs
	};
	
	$(document).ready(function(){
		dict.lang(lng);
	});
	
	return dict;
})();