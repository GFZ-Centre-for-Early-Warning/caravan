//elements with data-title=key will search the key, retrieve the title and set their html
//elements with data-doc=key will search the key, retrieve the title and display it on focus
caravan.dict = (function(){
	var $ = jQuery;
	
	//THE LINE BELOW UNTIL <END> IS AUTO-GENERATED, DO NOT MODIFY
	var lang_dict = {% DICT %}
	//<END>
	
	var _langs = function(){
		a = [];
		for(n in lang_dict){
			a.push(n);
		}
		return a;
	};
	
	var lng = "{% DEFAULT_LANG %}";
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