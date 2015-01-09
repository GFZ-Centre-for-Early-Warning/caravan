#Caravan language dictionary.
# -*- coding: utf-8 -*-

__author__="Marcel Wiethan <wiethan@gfz-potsdam.de>, Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="Dec 12, 2014 5:25:17 PM"

# from .. import globalkeys as gk
import caravan.settings.globalkeys as gk

""""
Module which implements localization strings according to a language. It is simply a set of global variables associated to 
their translation according to the given language. 
Any global variable is a dictionary KEY, and its translation is called the key TEXT. 
The caravan app will then parse the given strings and build a javascript 
file to be included in the Caravan main page. TEXT is assumed to be in html to give the possibility of more refined 
formatting (e.g. you can render subscripts as a<sub>1</sub>. Keep it simple, though)

:::::::::::::::::::::::::::::::::::
=== IMPLEMENTING A NEW LANGUAGE ===
-----------------------------------
To implement a new language, COPY this file in the SAME DIRECTORY, 
rename it according to the language name (e.g., 'de.py') and just change (translate) all strings within quotes (" or ').
A basic knowledge of html is required, as special html tags should NOT be translated

:::::::::::::::::::::::::::::::::::
=== IMPLEMENTING A NEW KEY ====
-----------------------------------
When implementing a new KEY, first consider that you should obviously do the same for all dict modules of this folder, as each one 
represents a language and consistency matters. 
Then, the KEY is useless until it is implemented in the web page. For the moment, dict keys are implemented 
in the caravan main page (file index_template.html). If the program gets bigger, and several pages need translation, 
then have a look at the index_template.html page and what is going on (basically have a look at 
files caravan_wsgi where we create lang_dict.js from lang_dict_template.js by means of this file, 
and index.html where we load lang_dict and we implement a help button which sets help popups on/off and a language switcher button)

Given that, assuming the new KEY and relative TEXT are 

    my_key = "this is the translation of my_key"

You can display my_key TEXT for either:
    
    1) Text label, by adding the data-title attribute to an element in the web page (e.g., <span data-title="my_text"></span>)
        In this case, the element 
            - alt attribute (if image)
            - value attribute (if input)
            - or inner html (in any other case as in the <span> example few lines above. 
                    Obviously, this works for elements with an open and close tag)
                    
    will be set to TEXT replacing old values, if any (i.e., be careful!), and when the web page language is changed and 
    other python modules are implemented, then the value will change accordingly WITHOUT reloading the page. Whereas 
    this causes to load ALL dictionaries making the web page "heavier", as long as the caravan app doesn't get huge 
    the benefits are clearly worth it (keep current parameter settings and/or map visualization when changing language)
    
    2) Doc/help description, by adding the data-doc attribute to an element in the web page 
        (e.g., <input ... data-doc="my_text" />)
        In this case, a popup will show TEXT when the element gains focus and the help button of the caravan main 
        page is clicked. Obviously, this works only for focusable elements (inputs, anchors, buttons, textareas and select elements 
        are among them)

If the same KEY is used for both data-label and data-doc attributes on the same (or several different) elements, 
then obviously the same TEXT is displayed. You can change this behavior by associating KEY to an array of 3 strings: 
in this case the SECOND element will be the string used when the key is associated to a 
data-label attribute, and the THIRD element will be the string used when the key is associated to a data-dic attribute.
The array has 3 elements because the first one is intended to be the key translation in the given language, as of 
december 2014 it is NOT used but it might be in error/warning messages in the future. Basically, the first element 
is the key word in the current language, the second is the key label (a little bit more verbose, if needed) and the third 
is the doc string (the most verbose one, if needed). 
Example: distance = ["distance", "Distance [Km]", "Type the distance, in Km"])

=== NOTES ===
KEYs starting with "_" are ignored. This is handy when a portion of text is shared between several module keys, as 
you can implement a variable starting with _, inserting it in other keys using it and avoiding conflicts with other keys. 
Moreover, this assures python default global variables starting and ending with "__" mess up with your KEYs 

The file should be ENCODED as UTF-8. Check your text editor encoding. The line # -*- coding: utf-8 -*- at the beginning 
of this file SHOULD NOT BE REMOVED and tells python that it is UTF-8, but the file itself must be encoded and saved in UTF-8. 
This is generally not an issue as most editors (Eclipse, Netbeans, Geany) are already in UTF-8 by default, but encoding problems 
are quite a headache and information minimizes the risks
"""

#START OF THE DICTIONARY HERE, PLEASE PROVIDE TRANSLATION FOR EVERY STRING

_normaldist_help = """<p>Es ist möglich dies als normale (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die durchschnittliche- und Standartabweichung darstellen"""		

_uniformdist_help = """<p>Es ist möglich dies als (nicht skalare) Verteilung durch eingeben zweier Zahlen (getrennt durch Leerzeichen,Komma oder Semikolon) zu spezifizieren, welche die unteren und oberen Werte darstellen"""		


globals()[gk.LAT] = [
        'Breitengrad',
	'Breitengrad', 					
	'Breitengrad' + _normaldist_help, 
]    
globals()[gk.LON] = [
	'Längengrad',
	'Längengrad',
	'Längengrad' + _normaldist_help,
]
globals()[gk.DEP] = [
	'Tiefe',
	'Tiefe [km]',
	'Tiefe [km]' + _uniformdist_help,
]
globals()[gk.MAG] = [
	'Magnitude',
	'Magnitude [mw]',
	'Magnitude [mw]' + _uniformdist_help,
]
globals()[gk.IPE] = [
	'Intensitätsvorhersagegleichung',
 	'IPE',
	'Intensitätsvorhersagegleichung',
]
globals()[gk.TIM] = [
	'Zeit',
	'Zeit [JJJJ MM TT]',
 	'Lege einen Zeitpunkt fest (Im Format JJJJ MM TT, es ist zudem möglich mit Kommata oder Querstrichen "/" zu trennen)'
]
globals()[gk.STR] = [
	'Streichrichtung',
	'Streichrichtung [Grad]',
	'Streichrichtung [Grad]' + _uniformdist_help,
]
globals()[gk.DIP] = [
	'Neigung',
	'Neigung [Grad]',
	'Neigung [Grad]' + _uniformdist_help,
]
globals()[gk.SOF] = [
	'Art der Verwerfung',
	'Art der Verwerfung',
	'Wähle Art der Verwerfung aus',
]
globals()[gk.GMO] = [
	'Nur Bodenbewegung',			
	'Nur Bodenbewegung',
	'Nur Bodenbewegung',
]
globals()[gk.DNP] = [
	'Anzahl Punkte der Verteilung',
	'Anz. Punkte Vert.',
 	'Wähle die Anzahl der Punkte der Verteilung (falls spezifiziert)',
]
globals()[gk.TES] = [
	'Tesselation',
 	'Tesselation',
 	'Wähle Tesselation (mehrere Optionen auswählbar)',
]
globals()[gk.AOI] = [
	"Gebiet",
	'Gebiet',
 	'', #not used (see aoi_... variables below
]
_iref = 'I<sub>ref</sub>'
globals()[gk.AIR] =[
	"Referenzintensität",			
	_iref,
	'Referenzintensität (Gebiet = Kreis um Epizentrum wo Intensität &ge; '+_iref+')',
]
globals()[gk.AKS] = [
	"A("+_iref+") Umkreis",
	'A('+_iref+ ') Umkreis [Km]',
	'Wähle den Umkreis (in Km) für die Berechnung in dem ausgewählten Gebiet (Kreis um das Epizentrum wo Intensität &ge; '+_iref+ ')',
]

#docs for I.P.E's. The doc will be built in caravan_wsgi according to this strings, using also dist_bounds string 
#mag_bounds string defined below. If you implement a new IPE, simply write the class name here with a relative doc string
GlobalWaHyp = "Globale Intensitätsvorhersagegleichung, basierend auf der Distanz zum Hypozentrum"
GlobalWaRup = "Globale Intensitätsvorhersagegleichung, basierend auf der Distanz zur Verwerfung"
CentralAsiaEmca = "Zentralasiatische Intensitätsvorhersagegleichung, basierend auf der Distanz zum Epizentrum"

_ipe_dist_bounds_text = "Distanzgrenzen: "				
_ipe_mag_bounds_text = "Magnitudengrenzen: "			

#General labels for the caravan app
_event_parameters = "Ereignis Parameter"
event_params_text = _event_parameters
model_params_text = "Modell Parameter"
advanced_text = ["erweiterte","Erweitert","Verberge erweiterte Optionen"]

run_text = ["starte", "Start", "Starte die Simulation mit den ausgewählten Parametern"]
cancel_text = ["abbrechen", "Abbrechen", "Laufende Simulation abbrechen"]
goback_text = ["geh zurück", "Geh zurück", "Züruck zum Eingabefenster"]

source_point_text = "Punkt"
source_extended_text = "Erweitert"
aoi_intensity_ref= ["Ausgewähltes Gebiet (entsprechend der Intensitätseingabe)",
                         "where I &ges; " + _iref,
                         "Berechnung nur auf dem Gebiet durchführen wo Intensitätsabschätzung größer ist als "+_iref+ " (siehe '"+advanced_text[1]+"')"]
aoi_map_rect=["","ausgewähltes Rechteck auf der Karte","Führe Berechnung nur für das auf der Karte ausgewählte Gebiet durch"]

#Not translated into chinese:
globals()[gk.MSI] = "Makroseismische Intensität"
globals()[gk.FAT] = "Todesopfer"
globals()[gk.ECL] = "Ökonomischer Verlust"
show_info = "Hilfe anzeigen beim Bewegen über eine Komponente"
query_events_from_catalog = "Rufe historisches Ereignis vom Katalog ab und nutzte es als "+event_params_text
hide_panel = "Verberge Optionen"
show_panel = "Zeige Optionen"

query_events = ["query events", "Query events", "Query events from the selected catalog matching the given criteria"]
choose_selected_event = ["choose selected event", "Choose selected", "Choose selected event and input its values in the "+_event_parameters]





