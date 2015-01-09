/*
 * Copyright (c) 2011-2014 Riccardo Zaccarelli <riccardo.zaccarelli(at)gmail.com>
 *
 * This is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed WITHOUT ANY WARRANTY; 
 * without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.
 *
 * @author Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)
 * @date Wed August 20 2014, 11:34
 */



// Create closure. //See http://learn.jquery.com/plugins/advanced-plugin-concepts/
(function ($) {
    // Plugin definition.
    /**
     * jQuery plugin for showing html elements (usually divs) as popup dialogs. 
     * It can be called by appending 'pop' to the jQuery default counterparts 
     * builti-in functions slideToggle, slideUp, slideDown, show, fadeIn, e.g.: 
     *  E.popupShow(arguments)
     *  E.popupFadeIn(arguments)
     * 
     * This functions does what the jQuery defautl counterpart function does, 
     * but before it places and resizes (overriding css position, top, left, 
     * max-width and max-height properties of) 
     * E according to the user settings. Note that to properly work, E should be 
     * appended to the document.biody. Any other sub-element as parent might mess 
     * up E position and size. 
     * Arguments to the functions are THE SAME as the jQuery default counterpart 
     * functions. The only difference is that, when 
     * arguments args is a plain object, it accepts the following ADDITIONAL keys:
     * <ul>
     *      <li><code>args.invoker</code><br>
     *          denotes a jQuery element which is usually a clickable element 
     *          (such as an anchor or a button) which "invokes" E pop-up, and 
     *          affects the place-resize algorithm explained below. Hereafter, 
     *          we will refer to "invoker is not specified" to indicate that 
     *          either args is not a plain object, or args.invoker is missing.
     *      <li><code>args.toolTip</code><br>
     *          If boolean, tells whether this popup div should behave as a toolitip, 
     *          i.e. being automatically hidden (invoking div.popClose()) when it (or one of 
     *          its nested children, recusrive search) looses the focus 
     *          (if missing, defaults to false, i.e. no tooltip popup)
     *          Otherwise, it is a function taking as argument the current document
     *          focus element (note: NOT jquery element, really html dom element,
     *          which can be wrapped in jQuery) and returning a boolean value telling 
     *          whether the popup div will be hidden. Additionally, the function can return a 
     *          string: 'detach' or 'remove', which evaluate as true (hide div)
     *          but also will also do what they say, once the popup div is hidden:
     *          invoke div.detach() or div.remove()
     *          NOTE: If toolTip is specified (either as true or as a function) 
     *          YOU SHOULD INVOKE div.popClose() instead of div.hide(),  
     *          as the former removes data value set when toolTip is not 
     *          missing nor false
     *          
     * </ul> 
     * The place-resize algorithm used to show (or fadeIn) E works as follows: 
     * <ol>
     *      <li>Calculate E natural size (width and height). E must have a parent, 
     *          thus attach E to the document root if it does not have a parent 
     *          (for the algorithm to properly work, document should always be 
     *          element's parent - or container). E position will be set as absolute, 
     *          E z-index to 10000, E box-sizing to 'border-box', E display and 
     *          visibility will be set to 'initial' and 'hidden' but only temporarily 
     *          (they will be restored to their user defined values at the end of 
     *          the algorithm before showing E) 
     *      <li>Calculate the Rectangle R where E must be placed. R is:
     *          <ul>
     *              <li>The viewport (the browser visible rectangle) if invoker 
     *                  is not specified, otherwise:
     *              <li>The Rectangle R defined by invoker: divide the viewport 
     *                  into four rectangles around invoker, and use the rectangle 
     *                  where E fits best according to its natural size. 
     *          </ul>
     *      <li>Shrink R by substracting to R the css margins of E, if any (note: 
     *          contrarily to all css properties set on E, margins refer to R, 
     *          thus they do not behave as default if they are given in percentage)
     *      <li>Override E max-width and max-height css properties to make E  
     *          size included in R size, if E natural size exceeds R width or height. 
     *      <li>Place E (overriding its left and top css properties):
     *          <ul>
     *              <li>centered in R if invoker is missing, otherwise:
     *              <li>adjacent to invoker. Adjacent means with one side close 
     *              to an invoker side (which side depends on which of the four 
     *              rectangles of the viewport has been chosen)
     *          </ul>
     * </ol>
     * <p>Notes:</p>
     * <ul>
     * <li>In principle, everything about E size and E content can be controlled 
     *     via user defined css. The only thing this plugin does is to place E 
     *     and to set a maximum width and a maximum height. Thus, for instance, 
     *     specifying width and height to 100% on E should make its natural size as big as 
     *     possible inside R, or setting E display property to inline-block should make its 
     *     natural size calculated according to its content. 
     *     Note also that inner E elements overflow must be specified by 
     *     the user, if it occurs. 
     *     Css control is  not a limitation: on the contrary, it 
     *     allows to specify classes and css on E as with any other element. 
     *     Remember only that css margins on E, if given in percentage, refer to 
     *     the calculated rectangle R
     * <li>However, in order to this plugin to properly work, the following E 
     *     css properties must be set and thus overridden:
     *     position (always absolute), box-sizing (always border-box), max-width, max-height, left, top, 
     *     z-index (always 10000), min-width (only if invoker is specified). 
     *     Thus, specifying them on E is useless
     * </ul>
     */

    var popupStaticId = new Date().getTime();

    //Self explanatory: note that argument must be a jQuery element
    var _isNotContainer = function ($element) {
        return ($element instanceof $) && !$element.is('div') && !$element.is('body') && $element.parent().length;

//        return $element && $element.length === 1 && $element instanceof $ && $element[0] !== w_ && $element[0] !== d_ &&
//                ($element.is('a') || $element.is('input[type=button]') || $element.is('button') ||
//                        $element.is('input[type=submit]'));
//        return ($element instanceof $) &&
//                ($element.is('a') || $element.is('input[type=button]') || $element.is('button') ||
//                        $element.is('input[type=submit]'));
    };

    var getId = function (element) {
        if (!(element.attr('id'))) {
            var pp = popupStaticId;
            var pre = 'popupdiv_';
            var idstr = pre + pp;
            while ($('#' + idstr).length) {
                popupStaticId++;
                pp = popupStaticId;
                idstr = pre + pp;
            }
            element.attr('id', idstr);
        }
        return element.attr('id');
    };

    
    var isShowing = function ($element) {
        return $element.is(':visible');
    };
    
    var _show = function (plainobject, showCallbackName) {

        //var default_duration = plainobject.duration;

        var div = this;
        getId(div); //actually sets the id if it does not have one

        var invoker = plainobject.invoker;
        var isNotContainer = _isNotContainer(invoker);
        var setBoundsCallback = isNotContainer ? _setBoundsAsPopup : _setBoundsInside;


        if (!div.parent().length) { //to be done before setBounds
            //actually, to be defined before everything, as e.g. the css display (see below) changes in chrome '
            //when a parent is non undefined
            div.appendTo('body');
        }

        div.hide();

        var overflows = setBoundsCallback.apply(this, [invoker]); //after this call, the main div is set to visible:hidden 
        //(it is absolutely positioned and appended to the document, so it does not move any other component, 
        //and its central component css overflow MUST STILL be set to auto

        //var place = undefined; //  this.setOffset;
        var customShowFunc = undefined; //arg of the show function (defined when parsing show arguemnts below)

        var arg = plainobject;
        if (typeof arg.toolTip === 'boolean'){
        	var b = arg.toolTip;
        	arg.toolTip = function(e){return b;};
        }
        var istooltip = typeof arg.toolTip === 'function';
        var duration = arg.duration;
        var hideCallbackName = showCallbackName === "fadeIn" ? "fadeOut" :
                showCallbackName === "slideToggle" ? showCallbackName : "hide";
        div.data('popup-close-function-name',hideCallbackName);
        if(duration){
        	div.data('popup-close-duration', duration);
        }
        
        var postShowFcn = function () {
            //resetting overflow: See notes below
            if (istooltip) { //set the focus: when div (or any of its children) looses it, hide the div
                var $doc = $(document);
                var idz = getId(div);
                //focusin sucks. Attach to mousedown and keyup:
                var queryStr = 'focusin.'+idz; //  'mousedown.' + idz + ' keyup.' + idz;
                div.data('popup-close-focusin', queryStr); //see popClose

                $doc.on(queryStr, function (e) {
                    if (!div.find(e.target).length && e.target !== invoker.get(0)) { //if invoker, avoid closing
                	//focus events mess up with invoker, especially if this popup is invoker on focusin
                        var ret = arg.toolTip(e.target);
                        if(ret){
                        	div.popClose(); //will reset everything set here
                            if(ret === 'detach'){
                                div.detach();
                            }else if(ret === 'remove'){
                                div.remove();
                            }
                        }
                    }
                }); 
            }
            if (typeof (customShowFunc) === 'function') {
                customShowFunc.apply(this.get(0));
            }
        };

        //PARSING ARGUMENTS TO BEHAVE AS JQUERY SHOW
        //var arg = this._parseShowHideArg(arguments); //defined some lines below, after this.close callback. Returns a plain object

        if (arg.complete) {
            customShowFunc = arg.complete;
        }
        arg.complete = function () {
            postShowFcn.apply(div);
        };

        div[showCallbackName](plainobject);

        return div;
    };

    var _getMargins = function ($element) {
        var v = $element.data('margin-remainder');
        if (!v) {
            var pFloat = parseFloat;
            v = [pFloat($element.css('marginTop')),
                pFloat($element.css('marginRight')),
                pFloat($element.css('marginBottom')),
                pFloat($element.css('marginLeft'))];
            $element.data('margin-remainder', v);
        }
        $element.css('margin', '0px');//margins seem to cause resize problems (ie, other elements on the page resize,
        //especially siblings of $element direct children of body. Why?? it should NOT be the case as we have position 
        //absolute and z-index (well, the OTHER elements should also have position, absolute, maybe that's the problem)
        return v;
    };

    var _setBoundsAsPopup = function ($invoker) {
        //var invoker = this.invoker;
        var $element = this;

        var oldDisplay = $element.css('display');
        var oldVisibility = $element.css('visibility');

        var preSize = _preSizeFcn($element);  //re-initializes css display, dimensions (width height) position (top, bottom) of all popup div elements


        var windowRectangle = getBoundsOf(); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object

        var invokerOffset = $invoker.offset();

        var invokerOuterHeight = $invoker.outerHeight();
        var spaceAbove = invokerOffset.top - windowRectangle.y;
        var spaceBelow = windowRectangle.height - invokerOuterHeight - spaceAbove;
        var placeAbove = spaceAbove > spaceBelow && $element.outerHeight(false) > spaceBelow;

        var invokerOuterWidth = $invoker.outerWidth();
        var spaceRight = windowRectangle.x + windowRectangle.width - invokerOffset.left;
        var spaceLeft = invokerOffset.left + invokerOuterWidth - windowRectangle.x;
        var placeLeft = spaceLeft > spaceRight && $element.outerWidth(false) > spaceRight;

        var x = placeLeft ? invokerOffset.left + invokerOuterWidth - $element.outerWidth(true) : invokerOffset.left;
        var y = (placeAbove ? invokerOffset.top - $element.outerHeight(true) :
                invokerOffset.top + invokerOuterHeight);

        var height = (placeAbove ? spaceAbove : spaceBelow);
        var width = (placeLeft ? spaceLeft : spaceRight);

        var insets = _getMargins($element);
//        var pFloat = parseFloat;
//        var insets = [pFloat($element.css('marginTop')),
//            pFloat($element.css('marginRight')),
//            pFloat($element.css('marginBottom')),
//            pFloat($element.css('marginLeft'))];
//        $element.css('margin', '0px'); //margins seem to cause resize problems (ie, other elements on the page resize,
        //especially siblings of $element direct children of body. Why?? it should NOT be the case as we have position 
        //absolute and z-index (well, the OTHER elements should also have position, absolute, maybe that's the problem)

        var rect = _getRectangle(x, y, width, height, insets);


        $element.css({//THIS SETS THE WIDTH AND HEIGHTS OF THE DIV INCLUDING PADDING AND BOTTOM, AS WE SET THE BOX-SIZING CSS TO BORDERBOX IN _PRESIZEFCN
            'display': oldDisplay,
            'visibility': oldVisibility,
            'max-width': rect.w + 'px',
            'max-height': rect.h + 'px',
            'min-width': $invoker.outerWidth(false) + 'px'
        });

        $element.css({//REFER TO DIV LEFT AND TOP MARGIN EDGES, see https://developer.mozilla.org/en-US/docs/Web/CSS/left
            'left': rect.x + 'px',
            'top': rect.y + 'px'
        });

        var postSize = _postSizeFcn($element); //Sets some more css values which must be set at the end. Most of the problems here regard IE. 

        return preSize[0] > postSize[0] || preSize[1] > postSize[1] ? true : false;
    };


    //Sets the popup div dimensions (css width height). See show() for an usage. 
    //inside the popup invoker argument, which is not a clickable element (it might be undefined and in this case it defaults to the window object). 
    //Returns a boolean indicating if the central div overflows
    var _setBoundsInside = function ($invoker) {
        var $element = this;

        var oldDisplay = $element.css('display');
        var oldVisibility = $element.css('visibility');

        var preSize = _preSizeFcn($element); //re-initializes css display, dimensions (width height) position (top, bottom) of all popup div elements
        var bounds = getBoundsOf($invoker); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
        var x = bounds.x;
        var y = bounds.y;
        var w = bounds.width;
        var h = bounds.height;

        var insets = _getMargins($element);
//        var pFloat = parseFloat;
//        var insets = [pFloat($element.css('marginTop')),
//            pFloat($element.css('marginRight')),
//            pFloat($element.css('marginBottom')),
//            pFloat($element.css('marginLeft'))];
//        $element.css('margin', '0px'); //margins seem to cause resize problems (ie, other elements on the page resize,
        //especially siblings of $element direct children of body. Why?? it should NOT be the case as we have position 
        //absolute and z-index (well, the OTHER elements should also have position, absolute, maybe that's the problem)

        var rect = _getRectangle(x, y, w, h, insets);

        var w = $element.outerWidth(true);
        var h = $element.outerHeight(true);

        //must be centered, so if the window is shorter shift x and y:
        if (w < rect.w) {
            rect.x += parseInt((rect.w - w) / 2);
        }
        if (h < rect.h) {
            rect.y += parseInt((rect.h - h) / 2);
        }

        $element.css({//THIS SETS THE WIDTH AND HEIGHTS OF THE DIV INCLUDING PADDING AND BOTTOM, AS WE SET THE BOX-SIZING CSS TO BORDERBOX IN _PRESIZEFCN
            'display': oldDisplay,
            'visibility': oldVisibility,
            'max-width': rect.w,
            'max-height': rect.h
        });

        $element.css({//REFER TO DIV LEFT AND TOP MARGIN EDGES, see https://developer.mozilla.org/en-US/docs/Web/CSS/left
            'left': rect.x + 'px',
            'top': rect.y + 'px'
        });


        var postSize = _postSizeFcn($element); //Sets some more css values which must be set at the end. Most of the problems here regard IE. 
        return preSize[0] > postSize[0] || preSize[1] > postSize[1] ? true : false;
    };


    var zIndex = 10000;

    //Function called from _setBoundsAsPopup and _setBoundsInside to re-initialize all css properties (div hidden, dimensions -width and height - set to '' etcetera)
    var _preSizeFcn = function ($element) {

        $element.css({
            'display': 'initial', 
            'max-height': '',
            'max-width': '',
            'min-height': '',
            'min-width': '',
            'height': '',
            'width': '',
            'overflow': '',
            'visibility': 'hidden',
            'float': '',
            'zIndex': zIndex,
            'position': 'absolute',
            'box-sizing': 'border-box',
            '-webkit-box-sizing': 'border-box',
            '-moz-box-sizing': 'border-box'
        });

        var size = [$element.width(), $element.height()];

        //place the div in the upperleft corner of the window. This might avoid scrollbars to appear on the wiondow and then disappear
        var bounds = getBoundsOf(); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
        $element.css({
            'left': bounds.x + 'px',
            'top': bounds.y + 'px'
        });

        return size;
    };

    //Function called from _setBoundsAsPopup and _setBoundsInside to set some more css values at the END of the respective functions
    //Most of the problems here regard IE. 
    //Basically, sets the max height of the central div. The width is already been set and is "absolute", whereas the height
    //must take into account also T and B (top and bottom div) after max sizes are set
    var _postSizeFcn = function ($element) {

        return [$element.width(), $element.height()];

    };

    var _getRectangle = function (x, y, w, h, margin) {
        var ispo = $.isPlainObject(margin);
        var insets = {top: 0, bottom: 0, right: 0, left: 0};
        if (ispo) {
            insets.top = margin.top || 0;
            insets.bottom = margin.bottom || 0;
            insets.right = margin.right || 0;
            insets.left = margin.left || 0;
        } else {
            if ($.isArray(margin) && margin.length) {
                if (margin.length === 1) {
                    var v = margin[0];
                    insets.top = insets.bottom = insets.right = insets.left = margin[0];
                } else if (margin.length === 2) {
                    var top_bottom = margin[0];
                    var right_left = margin[1];
                    insets.top = insets.bottom = top_bottom;
                    insets.left = insets.right = right_left;
                } else if (margin.length === 2) {
                    var top = margin[0];
                    var right_left = margin[1];
                    var bottom = margin[2];
                    insets.top = top;
                    insets.bottom = bottom;
                    insets.right = insets.left = right_left;
                } else {
                    insets.top = margin[0];
                    insets.right = margin[1];
                    insets.bottom = margin[2];
                    insets.left = margin[3];
                }
            } else if (typeof (margin) === 'number') {
                insets.top = insets.right = insets.bottom = insets.left = margin;
            }
        }
        var n = 'number';
        for (var v in insets) {
            if (typeof (insets[v]) !== n) {
                insets[v] = 0;
            }
        }
        var max = Math.max;
        var pInt = parseInt;

        if (insets.top > 0 && insets.top < 1) {
            insets.top = h * insets.top;
        }
        //insets.top = max(0, pInt(insets.top));

        if (insets.bottom > 0 && insets.bottom < 1) {
            insets.bottom = h * insets.bottom;
        }
        //insets.bottom = max(0, pInt(insets.bottom));

        if (insets.left > 0 && insets.left < 1) {
            insets.left = w * insets.left;
        }
        //insets.left = max(0, pInt(insets.left));

        if (insets.right > 0 && insets.right < 1) {
            insets.right = w * insets.right;
        }
        //insets.right = max(0, pInt(insets.right));


        return {x: x + insets.left, y: y + insets.top, w: w - (insets.left + insets.right), h: h - (insets.top + insets.bottom)};
    };


    //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
    var getBoundsOf = function ($element) {
        var ret = {
            x: 0,
            y: 0,
            width: 0,
            height: 0
        };
        if (!$element || !($element instanceof $)) {
            $element = $(window);
        }
        if ($element.get(0) === window) {
            ret.x = $element.scrollLeft();
            ret.y = $element.scrollTop();
        } else {
            var offs = $element.offset();
            ret.x = offs.left;
            ret.y = offs.top;
        }
        ret.width = $element.width();
        ret.height = $element.height();
        return ret;
    };

//   

    //parses the arguments to show and close to a valid dict usable for
    //jQuery.hide and jQuery.show
    var _parseShowHideArg = function () {
        var arg = {};
        if (arguments && arguments.length > 0) {
            var len = arguments.length;
            if (len === 1 && $.isPlainObject(arguments[0])) {
                arg = arguments[0];
            } else {
                arg.duration = arguments[0];
                if (len > 2) {
                    arg.complete = arguments[2];
                    arg.easing = arguments[1];
                } else if (len > 1) {
                    arg.complete = arguments[1];
                }
            }
        }
        return arg;
    };
    
    //To get an help on jQuery this, see here:
    //https://remysharp.com/2007/04/12/jquerys-this-demystified
    
    $.fn.popClose = function () {
        //this is a jQuery object
        var fcn = this.data('popup-close-function-name');
        
        this.removeData('popup-close-function-name');
        if(this.data('popup-close-focusin')){
            $(document).off(this.data('popup-close-focusin'));
            this.removeData('popup-close-focusin');
        }
        var duration = undefined;
        if(this.data('popup-close-duration')){
            duration = this.data('popup-close-duration');
            this.removeData('popup-close-duration');
        }
        if(fcn && this[fcn]){
            var argz = _parseShowHideArg(arguments);
            if(duration!==undefined && !('duration' in argz)){
        	argz.duration = duration;
            }
            this[fcn](argz);
            //this[fcn].apply(this.get(0), arguments);
        }
    };

    $.fn.popShow = function () {
        return _show.apply(this, [_parseShowHideArg.apply(this, arguments), 'show']);
        //_parseShowHideArg() defined some lines below, after this.close callback. Returns a plain object
    };

    $.fn.popFadeIn = function () {
        return _show.apply(this, [_parseShowHideArg.apply(this, arguments), 'fadeIn']);
    };
    
    $.fn.popSlideToggle = function () {
        return _show.apply(this, [_parseShowHideArg.apply(this, arguments), 'slideToggle']);
        //_parseShowHideArg() defined some lines below, after this.close callback. Returns a plain object
    };

    $.fn.popSlideDown = function () {
        return _show.apply(this, [_parseShowHideArg.apply(this, arguments), 'slideDown']);
    };
    
    $.fn.popSlideUp = function () {
        return _show.apply(this, [_parseShowHideArg.apply(this, arguments), 'slideUp']);
    };


    function _showOver(elm){
    	var $this = this;
    	var $elm = $(elm);
    	if(!$elm.length){
    		return;
    	}
    	var $parent = $elm.parent();
    	var pos = $elm.position();
    	if(!$parent.length || !($parent.css('position') === 'relative' || $parent.css('position') === 'absolute')){
    		$parent = $(document.body);
    		pos = $elm.offset();
    	} 
    	$this.css({'display':'none','box-sizing':'border-box','margin':0, 
    		'position': 'absolute', 'z-index':100000,'left':pos.left,'top':pos.top, 
    		'width':$elm.outerWidth(true), 'height':$elm.outerHeight(true)});
    	$this.detach();
    	$this.show(); //if it was hidden...
    	$this.appendTo($parent);
    	//$this[showCallbackName](plainobject);
    }
    
    $.fn.showOver = function (elm) {
        return _showOver.apply(this, [elm]);
    };
// End of closure.

})(jQuery);


/**
 * jQuery plugin which, applied to a jQuery element usually wrapping several nodes, 
 * transforms them into a button group, emulating a list of option elements.
 * Obviously, the nodes must be clickable elements (buttons, anchors, input[type=button] etcetera) 
 * This function replaces the select tag in that preserves the same functionality (with some 
 * more effort) and lets you style button group elements  
 * which is not possible with select tags
 * 
 * Usage: 
 * given $elements a group of, e.g., three anchors,
 *  
 *      $elements.asOptions(callback)
 * 
 * Wraps $elements into a button group, i.e., a click on any element sets its selected state 
 * (represented by the class "selected", which can be customized in a stylesheet) 
 * removing the class from the other elements. Any element with class "disabled" 
 * (again, customizable in a stylesheet) does not receive the click nor triggers 
 * the associated callback, if any.
 * The callback argument, if not null (or undefined) takes 
 * two arguments: the clicked element index I and $elements (so that $elements.eq(I) 
 * returns the clicked element). 
 * NOTE: If all $elements are children of the given parent, and all have the 
 * attribute "data-value" ($elements.eq(i).data('value')!==undefined for all i), 
 * then the parent data-value attribute is set as the data value 
 * of the selected index. Therefore, in this case, called p the parent element, 
 * you can check for the selected value with 
 *      parent.data("value") 
 * instead of parent.find('.selected:not(.disabled)').data('value')
 * 
 *      $elements.asOptions(selectedIndex, callback)
 * 
 * As above, BUT $elements.eq(selectedIndex) is selected by default. If the default selected 
 * element has not the class "disabled" (otherwise nothing happens) this means also 
 * programmatically call callback (if non-null or undefined) at the end of the 
 * function with selectedIndex as first argument. 
 * If you want to avoid this, simply manually supply a class "selected" to your 
 * default selected element. 
 * NOTE: See above for element with "data-value" attributes
 * 
 *      $elements.asOptions(selectedIndex, multiSelect, callback)
 * 
 * As above, but, if multiSelect is true, then several elements can be selected, 
 * and re-clicking on an element toggles its selected state leaving other's element 
 * selected state untouched. 
 * Thus, in this case the callback, if given, might also want to check if 
 * $elements.eq(selectedIndex) is selected by testing: 
 * $elements.eq(selectedIndex).hasClass('selected'). 
 * NOTE: See above for element with "data-value" attributes. The difference in this
 * case is that the parent data-value attribute is set as the ARRAY with the data values 
 * of all selected index
 * 
 * NOTE on jQuery11 elm.data(key): it stores data internally, it must be removed with removeData
 * BUT AFTER THAT, if a data-key attribute is set, jQuery.data(key) returns (IN STRING FORMAT) 
 * This function uses jQuery.data, therefore if you supply a data- attribute, note that 
 * it will use the string of that attribute
 * 
 * Examples:
 *  Given:
 *      <a id=anc data-value='[1,2,3]'>
 *  Then:
 *      $('#anc').data('value') returns '[1,2,3]' (string!)
 *  Typing:
 *      $('#anc').data('value') = [1,2,3] 
 *  Then:
 *      $('#anc').data('value') returns [1,2,3] (array!)
 *  Typing:
 *      $('#anc').removeData()
 *  Then:
 *      $('#anc').data('value') returns '[1,2,3]' (string again!)
 *  
 * @param {type} $
 * @returns {undefined}
 */
(function ($) {
    function _asBGroup(selectedIndex, multiSelect, callback) {
        //childrenSelectors = !childrenSelectors ? 'a,input[type=button],button' : childrenSelectors;
        var $elms = this; //.children(childrenSelectors);

        if (!$elms.length) {
            return;
        }

        //check if we need to set the data-value attr on the parent. To do this,
        //all elements must have a data-value attr and be children of the same parent element
        var parentNode = $elms.get(0).parentNode;
        $elms.each(function (i, elm) {
            if (parentNode) {
                var hasDataValue = $(elm).data("value") !== undefined;
                if (hasDataValue) {
                    hasDataValue = elm.parentNode === parentNode;
                }
                if (!hasDataValue) {
                    parentNode = undefined;
                }
            }
            return parentNode ? true : false; //false should stop the iteration
        });

        function selectionChanged() {
            if (parentNode) {
                var $selected = $elms.filter(".selected:not(.disabled)");
                var $parent = $(parentNode);
                var a = [];
                $selected.each(function (i, elm) {
                    a.push($(elm).data("value"));
                });
                $parent.data("value", a && a.length ? (multiSelect ? a : a[0]) : undefined);
            }
        }

        $elms.each(function (i, elm) {
            var $elm = $(elm);
            if ($elm.prop('tagName').toLowerCase() === 'a') {
                $elm.attr('href', '#');
            }

            $elm.click(function () {
                if ($elm.hasClass("disabled")) {
                    return;
                }
                if (multiSelect) {
                    $elm.toggleClass("selected");
                } else {
                    $elms.removeClass('selected'); //for safety
                    $elm.addClass("selected");
                }

                selectionChanged();
                if (callback) {
                    callback(i, $elms);
                }
                return false; //for anchors
            });
        });

        if (selectedIndex || selectedIndex === 0) {
            $elms.removeClass("selected");
            $elms.eq(selectedIndex).click();
        } else {
            selectionChanged(); //updates the data-value attr, if everything is set properly
        }
    }

    $.fn.asOptions = function (selectedIndex, multiSelect, callback) {
        if (arguments.length === 1) {
            callback = selectedIndex;
            selectedIndex = undefined;
            multiSelect = false;
        } else if (arguments.length === 2) {
            callback = multiSelect;
            multiSelect = false;
        }

        return _asBGroup.apply(this, [selectedIndex, multiSelect, callback]);
        //_parseShowHideArg() defined some lines below, after this.close callback. Returns a plain object
    };




// End of closure.

})(jQuery);