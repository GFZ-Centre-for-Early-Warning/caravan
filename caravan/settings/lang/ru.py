#Caravan language dictionary.
# -*- coding: utf-8 -*-

__author__="Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="Dec 3, 2014 7:25:17 PM"

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

_normaldist_help = """<p>You can also specify it as (non-scalar) normal distribution by typing a sequence of two numbers 
(separated by either spaces, a comma or a semicolon)<br>indicating the mean and standard deviation, respectively"""

_uniformdist_help = """<p>You can also specify it as (non-scalar) uniform distribution by typing a sequence of two numbers 
(separated by either spaces, a comma or a semicolon)<br>indicating the low and upper values, respectively"""

globals()[gk.LAT] = [
    'широта',
	'широта [deg]', 
	'широта [деление]' + _normaldist_help, 
]    
globals()[gk.LON] = [
	'долгота',
	'долгота [deg]',
	'долгота [деление]' + _normaldist_help,
]
globals()[gk.DEP] = [
	'глубина',
	'глубина [км]',
	'глубина [км]' + _uniformdist_help,
]
globals()[gk.MAG] = [
	'магнитуда',
	'магнитуда [mw]',
	'магнитуда [mw]' + _uniformdist_help,
]
globals()[gk.IPE] = [
	'Интенсивность уравнение прогнозирования',
 	'IPE',
	'Интенсивность уравнение прогнозирования',
]
globals()[gk.TIM] = [
	'время',
	'время [YYYY MM DD]',
 	'Установить время (в формате YYYY MM DD, Вы можете также использовать запятые или слэш "/" в качестве разделителя)'
]
globals()[gk.STR] = [
	'забастовка',
	'забастовка [deg]',
	'забастовка [деление]' + _uniformdist_help,
]
globals()[gk.DIP] = [
	'DIP',
	'DIP [deg]',
	'DIP [деление]' + _uniformdist_help,
]
globals()[gk.SOF] = [
	'стиль Ошибка в',
	'стиль Ошибка в',
	'Выберите стиль Ошибка в',
]
globals()[gk.GMO] = [
	'только колебания грунта',
	'Только движение грунта',
	'Только движение грунта',
]
globals()[gk.DNP] = [
	'Распределение число точек',
	'Расстояние НПЦ',
 	'Выберите число точек распределения (если таковые указаны)',
]
globals()[gk.TES] = [
	'tessellation(s)',
 	'Tessellation(s)',
 	'Выберите целевые мозаик (множественный выбор допускаются)',
]
globals()[gk.AOI] = [
	"площадь",
	'площадь',
 	'', #not used (see aoi_... variables below
]
_iref = 'I<sub>ref</sub>'
globals()[gk.AIR] =[
	"ориентиром в интенсивности",
	_iref,
	'Ссылка Интенсивность (площадь = круг вокруг эпицентра, где интенсивность &ge; '+_iref+')',
]
globals()[gk.AKS] = [
	"A("+_iref+") шаг",
	'A('+_iref+ ') шаг [км]',
	'Выберите этап (в км), используемый при расчете целевой зоны (круг вокруг эпицентра, где интенсивность &ge; '+_iref+ ')',
]

#docs for I.P.E's. The doc will be built in caravan_wsgi according to this strings, using also dist_bounds string 
#mag_bounds string defined below. If you implement a new IPE, simply write the class name here with a relative doc string
GlobalWaHyp = "Глобальный Уравнение прогнозирования интенсивности, основанный на гипоцентральной расстоянии"
GlobalWaRup = "Глобальный Уравнение прогнозирования интенсивности, в зависимости от расстояния разрыва"
CentralAsiaEmca = "Центральная Азия прогноз интенсивности Уравнение, основанный на эпицентральной расстояния"

_ipe_dist_bounds_text = "Расстояние границы: "
_ipe_mag_bounds_text = "амплитудные оценки: "

#General labels for the caravan app
_event_parameters = "Параметры события"
event_params_text = _event_parameters
model_params_text = "параметров модели"
advanced_text = ["продвинутый","продвинутый","Переключить расширенные настройки видимости"]

run_text = ["пробег", "пробег", "Начать имитацию с заданными параметрами"]
cancel_text = ["отменить", "отменить", "Ансель работает моделирование"]
goback_text = ["возвращаться", "возвращаться", "Восстановить окно параметров"]

source_point_text = "точка"
source_extended_text = "расширенный"
aoi_intensity_ref= ["область интересов (по ссылке интенсивности)",
                         "где я &ges; " + _iref,
                         "Выполнение вычислений только на площади, где оценка интенсивности больше, чем "+_iref+ " (видеть '"+advanced_text[1]+"')"]
aoi_map_rect=["","Карта текущий прямоугольник.","Выполнение вычислений только на площади в данный момент отображается на карте"]

#Not translated into chinese:
globals()[gk.MSI] = "Макросейсмическое Интенсивность"
globals()[gk.FAT] = "Погибшие"
globals()[gk.ECL] = "Экономические потери"
show_info = "показать помощь при переезде к компоненту"
query_events_from_catalog = "Запрос историческое событие из каталога и установить его в "+event_params_text
hide_panel = "Скрыть панель"
show_panel = "Показать панель"

query_events = ["события запроса", "события запроса", "События запрос от выбранного каталога, соответствующих критериям"]
choose_selected_event = ["выбрать выбранное событие", "Выберите selecte", "Выберите выбранное событие и введите значения в "+_event_parameters]





