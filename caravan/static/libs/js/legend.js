
//*Note:implemented by Marcel:Layer Options
function legendImplement() {

$(document).ready(function () {
    
    //get all Map divs    
    var $allIdMaps = $("#fatalMap,#econMap,#colorMap,#intenFutureMap");   
       
    //simple function to highlight div
    $(".highlightIt").mouseover(function () {
        $allIdMaps.css("opacity","1");  
        $(".highlightIt").mouseout(function () {
            $allIdMaps.css("opacity","0.7");
        });
      });
                   
//    var inten = new leaf.LayerGroup();
//    var fatal = new leaf.LayerGroup();
//    var econ = new leaf.LayerGroup();
//
//    //var overlays = {"Show Intensities": inten,
//      //  "Show Fatalities": fatal,
//       // "Show Economic Losses(EUR)": econ};
//
//    var osmLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>'; //why is the baselayer dissapearing when i delete it?
//
//    var thunLink = '<a href="http://thunderforest.com/">Thunderforest</a>';
//    var landUrl = 'http://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png';
//    var thunAttrib = 'Processing &copy; <a target="_blank" href="http://www.gfz-potsdam.de/en/research/organizational-units/technology-transfer-centres/centre-for-early-warning-systems-ews/">GFZ Potsdam - Centre for Early Warning Systems|</a>'
//            + '&copy; ' + osmLink + ' Contributors & ' + thunLink;
//    var landMap = leaf.tileLayer(landUrl, {attribution: thunAttrib});
//
//    var esriLink = '<a href="http://www.esri.com/">Esri</a>';
//    var esriUrl = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer\
///tile/{z}/{y}/{x}';
//    var esriAttrib = 'Processing &copy; <a target="_blank" href="http://www.gfz-potsdam.de/en/research/organizational-units/technology-transfer-centres/centre-for-early-warning-systems-ews/">GFZ Potsdam - Centre for Early Warning Systems|</a>'
//            + '&copy; ' + esriLink + ' Contributers';
//    var esriMap = leaf.tileLayer(esriUrl, {attribution: esriAttrib});
//
//    var baseLayers = {
//        "OpenStreetMap": baseLayer,
//        "Landscape": landMap,
//        "Esri Satellite": esriMap};
//
//    //leaf.control.layers(baseLayers).addTo(map);
//    
//    //TODO: discuss Overlays options seem to have limited functionality??!
//    //checkbox setup and functionality 
//
//    layerOptions = leaf.control.layers();
//    layerOptions.onAdd = function (map) {
//        this._div = leaf.DomUtil.create('div', 'layerOptions');
//        this._div.innerHTML = '<label><input type="checkbox" class="radio" value="A" name="oneSelectable" id="checkboxInten" >Show Intensities</input></label><br>' +
//                '<label><input type="checkbox" class="radio" value="B" name="oneSelectable" id="checkboxFata" >Show Fatalities </input></label><br>' +
//                '<label><input type="checkbox" class="radio" value="C" name="oneSelectable" id="checkboxEcon">Show Economic Losses(EUR)</input></label>';
//        return this._div;
//    };
//
//    layerOptions.addTo(map);    
//        
//         //mutually exclusive function
//          $("input:checkbox").on('click', function () {
//            var $box = $(this);
//            if ($box.is(":checked")) {
//                var group = "input:checkbox[name='" + $box.attr("name") + "']";
//                $(group).prop("checked", false);
//                $box.prop("checked", true);
//            } else {
//                $box.prop("checked", false);               
//            }
//        });
//                
//        $("#checkboxInten").change(function () {
//            if ($(this).is(":checked")) {
//                $allIdMaps.hide();
//                $("#colorMap").show();
//            } else {
//                $("#colorMap").hide();
//            }
//        });
//
//        $("#checkboxFata").change(function () {
//            if ($(this).is(":checked")) {
//                $allIdMaps.hide();
//                $("#fatalMap").show();             
//            } else {
//                $("#fatalMap").hide();
//            }
//        });
//
//        $("#checkboxEcon").change(function () {
//            if ($(this).is(":checked")) {
//                $allIdMaps.hide();
//                $("#econMap").show();
//            } else  {              
//                $("#econMap").hide();
//                
//            }
//        });
              
    

 });

}