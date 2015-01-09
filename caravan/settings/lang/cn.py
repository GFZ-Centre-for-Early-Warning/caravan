#Caravan language dictionary.
# -*- coding: utf-8 -*-

__author__="Ying Wang <wangying220062@gmail.com>, Riccardo Zaccarelli, PhD <riccardo(at)gfz-potsdam.de, riccardo.zaccarelli(at)gmail.com>"
__date__ ="Dec 7, 2014 10:14:17 AM"

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
Example: distance = ["distance", "Distance [Km]", "Type the distance, in Km"]

=== NOTES ===
KEYs starting with "_" are ignored. This is handy when a portion of text is shared between several KEYs, as 
you can implement a variable in this module starting with _, inserting it in other keys using it and avoiding conflicts with other keys.
Such variables don't even need to be shared across different languages (.py files in this folder), as they are ignored.
Moreover, this avoids python default global variables starting and ending with "__" mess up with your KEYs 

The file should be ENCODED as UTF-8. Check your text editor encoding. The line # -*- coding: utf-8 -*- at the beginning 
of this file SHOULD NOT BE REMOVED and tells python that it is UTF-8, but the file itself must be encoded and saved in UTF-8. 
This is generally not an issue as most editors (Eclipse, Netbeans, Geany) are already in UTF-8 by default, but encoding problems 
are quite a headache and information minimizes the risks
"""

#START OF THE DICTIONARY HERE, PLEASE PROVIDE TRANSLATION FOR EVERY STRING

_normaldist_help = """<p>您也可以通过输入一系列数对将其指定为（非标量）正太分布（通过空格、逗号或分号将其进行分隔）<br>分别表示平均值和标准差"""

_uniformdist_help = """<p>您也可以通过输入一系列数对将其指定为（非标量）均匀分布（通过空格、逗号或分号将其进行分隔）<br>分别表示最低值和最高值"""

globals()[gk.LAT] = [
    '纬度',
    '纬度 [度]', 
    '纬度 [度数]' + _normaldist_help, 
]    
globals()[gk.LON] = [
    '经度',
    '经度 [度]',
    '经度 [度数]' + _normaldist_help,
]
globals()[gk.DEP] = [
    '深度',
    '深度 [千米]',
    '深度 [千米]' + _uniformdist_help,
]
globals()[gk.MAG] = [
    '幅度',
    '幅度 [兆瓦]',
    '幅度 [兆瓦]' + _uniformdist_help,
]
globals()[gk.IPE] = [
    '强度预测方程',
     '强度预测方程',
    '强度预测方程',
]
globals()[gk.TIM] = [
    '时间',
    '时间 [年 月 日]',
     '设置时间 (使用 年 月 日 格式, 您也可以使用逗号或者斜杠"/"作为分隔)'
]
globals()[gk.STR] = [
    '走向',
    '走向 [度]',
    '走向 [度数]' + _uniformdist_help,
]
globals()[gk.DIP] = [
    '倾角',
    '倾角 [度]',
    '倾角 [度数]' + _uniformdist_help,
]
globals()[gk.SOF] = [
    '断层样式',
    '断层样式',
    '选择断层样式',
]
globals()[gk.GMO] = [
    '仅地表运动',
    '仅地表运动',
    '仅地表运动',
]
globals()[gk.DNP] = [
    '分布点数',
    '分布点数',
     '选择分布点数 (在指定情况下)',
]
globals()[gk.TES] = [
    '表面细化',
     '表面细化',
     '选择目标表面细化 (可多选)',
]
globals()[gk.AOI] = [
    "面积",
    '面积',
     '', #not used (see aoi_... variables below
]
_iref = '强度<sub>参照</sub>'
globals()[gk.AIR] =[
    "强度参照",
    _iref,
    '强度参照 (面积 = 震中周围圆，这里强度 &ge; '+_iref+')',
]
globals()[gk.AKS] = [
    "面积("+_iref+") 计算步骤",
    '面积('+_iref+ ') 计算步骤 [千米]',
    '选择用于目标面积计算的步骤（单位为千米）(震中周围圆，这里强度 &ge; '+_iref+ ')',
]

#docs for I.P.E's. The doc will be built in caravan_wsgi according to this strings, using also dist_bounds string 
#mag_bounds string defined below. If you implement a new IPE, simply write the class name here with a relative doc string
GlobalWaHyp = "基于震中距的全球强度预测方程"
GlobalWaRup = "基于断裂距的全球强度预测方程"
CentralAsiaEmca = "基于震中距的中亚强度预测方程"

_ipe_dist_bounds_text = "距离范围: "
_ipe_mag_bounds_text = "幅度范围: "

#General labels for the caravan app
_event_parameters = "事件参数"
event_params_text = _event_parameters
model_params_text = "模型参数"
advanced_text = ["高级","高级","触发高级设置可视性"]

run_text = ["运行", "运行", "使用给定参数开始模拟"]
cancel_text = ["取消", "取消", "取消模拟"]
goback_text = ["返回", "返回", "恢复参数窗口"]

source_point_text = "点"
source_extended_text = "扩展"
aoi_intensity_ref= ["感兴趣区域 (按照强度参照)",
                         "这里强度 &ges; " + _iref,
                         "仅就强度评估大于"+_iref+ "的区域进行计算 (见 '"+advanced_text[1]+"')"]
aoi_map_rect=["","地图当前矩形区","仅就当前地图中显示的区域进行计算"]

#needs check from native speaker:
globals()[gk.MSI] = "宏观烈度"
globals()[gk.FAT] = "死亡"
globals()[gk.ECL] = "经济损失"
show_info = "show help when moving to a component"
query_events_from_catalog = "Query historical event from catalog and set it in the "+event_params_text
hide_panel = "Hide panel"
show_panel = "Show panel"

query_events = ["query events", "Query events", "Query events from the selected catalog matching the given criteria"]
choose_selected_event = ["choose selected event", "Choose selected", "Choose selected event and input its values in the "+_event_parameters]


