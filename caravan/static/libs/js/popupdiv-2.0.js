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
 * Author: Riccardo Zaccarelli <riccardo.zaccarelli(at)gmail.com>
 */



// Create closure. //See http://learn.jquery.com/plugins/advanced-plugin-concepts/
(function ($) {
    // Plugin definition.
    /**
     * jQuery plugin for showing html content in a non-modal div (i.e., which doesn't "freeze" all user inputs until they it is showing) thus
     * emulating common popup-dialogs for showing messages or processing user input. 
     * <p>Requires jQuery &gt;=1.8. Works in IE8+, FF, Chrome 
     * <p>Usage:
     * <pre>
     * <font color=blue>var</font> var p = $.popupdiv(arg);
     * </pre> 
     * The plugin returns a JavaScript object associated to an absolutely 
     * positioned div D (attached to the document) 
     * which holds three subdivs Top,Content and Bottom ass follows: 
     * <p>D._popupdiv_:<table border=1>
     *      <tr><td>T._popupdiv_header_</td></tr>
     *      <tr><td>C._popupdiv_container_</td></tr>
     *      <tr><td>B._popupdiv_footer_</td></tr>
     * </table>
     * T and B can be hidden (see properties below). 
     * However, the top div T holds by default the title (in the form of a text node) and the 
     * close button, the middle div C container holds P content, 
     * and the bottom div B the Ok button (button stands for 'clickable element', it might
     * be also an anchor or an input element)
     * <p>Basically, after setting p properties (see methods below), 
     * everything is set-up just prior to setting D visible (p.show() or p.fadeIn):
     * First D is positioned in the window according to its  <code>invoker</code> (see below), 
     * then elements inside D with attribute p.getOkInvokerAttrName() are bound via
     * their click event to a function notifying 'Ok' listeners, and elements 
     * with attribute p.getCloseInvokerAttrName() are bound to a function notifying the 
     * 'close' listeners (T close button and B 'Ok' button have such attributes by default).
     * When hidden (either manually via p.close() or via a predefined D button), D is 
     * <b>removed</b> from the document for safety (it should avoid memory leaks).
     * <p>
     * Almost everything is customizable:
     * <h3>Popup functions</h3>
     * P functions can be accessed at any time after P has been created but BEFORE 
     * <code>P.fadeIn(), p.show()</code> have been called, as these methods set up D position and size 
     * before showing D and therefore modification of D content might result in unexpected results 
     * <p><b><code>getDiv()</code></b>: returns D in form of a jQuery element. Manipulation 
     * of the div must take into account that some css properties will be overridden 
     * prior to show (position, float, display properties). T,C and B divs can be accessed 
     * via <code>p.getDiv().children(N)</code>, where N=0 returns T, N=1 returns C, 
     * and N=2 returns B.
     * <p>In order to easily set class on those subdivs, two additional methods are implemented:
     * <p><code><b>addClass(arg)</b></code> and <code><b>removeClass(arg)</b></code>: 
     * if arg is a string, they behave exactly as the same jQuery function applied on 
     * D. Note that this function returns ALWAYS this object (i.e., P, and not the 
     * jQuery element(s) the realtive jQuery function is applied on).
     * This function can be called also with (in brackets the jQuery component to 
     * which addClass/removeClass will be called with the relative string argument):
     * <ul>
     *  <li> two string arguments (T,B). E.g. p.addClass('a b','c') calls T.addClass('a b') and B.addClass('c') 
     *  <li> three string arguments (T,C,B)
     *  <li> four string arguments (P,T,C,B)
     *  <li>a single plain object argument. Its keys must be strings as well as its 
     *  values. The values are the argument to each jquery addClass or removeClass 
     *  function applied to the relative key. The keys can be:
     *      <ul>
     *          <li>'top' or 'header', to indicate T,
     *          <li>'middle' or 'container', to indicate C, 
     *          <li>'bottom' or 'footer', to indicate B 
     *          <li>'popup' or 'main', to indicate P 
     *      </ul>
     * </ul>
     * Any empty string argument (and possibly also with only spaces, needs to see jQuery doc) does not do anything
     * 
     * <p><code><b>bind(eventName, callback)</b></code>: binds a callback to a specified 
     * event: eventName is a string, either 'close' or 'ok' (see <code>onClose</code> 
     * and <code>onOk</code> below for details). 
     * On show, every jQuery element in D (using jQuery <code>find</code>) which has the attribute 
     * <code>P.getOkInvokerAttrName()</code> will notify (through its click event) 
     * listeners added with eventName 'ok', whereas every jQuery element  in D 
     * (using jQuery <code>find</code>) which has the attribute <code>P.getCloseInvokerAttrName()</code> 
     * will notify (through its click event) listeners added with eventName 'close'. 
     * T and B, if visible, already hold anchors with such attributes (T anchor firing 
     * callbacks mapped to the 'close' event name and B anchor firing 
     * callbacks mapped to the 'ok' event name)
     * In any case the callback <code>this</code> keyword refers to P. 
     * <p>For callbacks mapped to 'ok', the callback passed as second argument takes no argument, whereas 
     * for callbacks mapped to 'close' the callback has a string argument
     * which indicates the source cause of the close event and can be 
     * "okClicked", "focusLost", "closeClicked" or "" (or undeinfed)
     * 
     * <p><code><b>unbind(eventName)</b></code>: unbinds all callbacks attached to the 
     * specified event name, which can be 'close' or 'ok' (see onClose and onOk below for details)
     * with no arguments, it unbinds all callbacks to all event names
     * 
     * <p><code><b>trigger(eventName)</b></code>: programmatically triggers the 
     * callbacks attached to the specified event name, which can be 'close' or 'ok'.
     * if 'close', callbacks listeners will be called with an empty argument
     * 
     * <p><code><b>title(jQueryElement [,title])</b></code>Returns the title in jQueryElement, 
     * where a 'title' of an element is retrieved/set by searching for its first text 
     * node child and returning/setting its node value (if no such an element, retrieving the 
     * title returns "", and setting a title does nothing). With no arguments, 
     * returns P title (The text node inside T, which is built by default on P creation), 
     * with one argument as string, sets D title (T text node value). <p>With 
     * one argument as jQuery element E, returns E title, with two arguments, sets the first argument 
     * title equal to the second argument
     * 
     * <p><code><b>show(), fadeIn()</b></code>: Shows D. The function first 
     * resets all css styles, repositioning D, and then shows it. Arguments to these 
     * functions are EXACTLY the same as the jQuery relative function. 
     * As a duration can anyway be specified as argument, it will override the default behaviour of 
     * <code>showhideCommands</code>, if present.
     * <b>Note on the 'complete' callback</b>, if given as argument, will be 
     * executed  at the real end of all showing chain but before assigning the first focusable element in the popup 
     * (if focusable is true, see below). The callback is exactly the same as it 
     * would be passed to jQuery <code>fadeIn</code> 
     * or <code>show</code> functions (e.g., it is not passed any argument) 
     * <b>except that the <code>this</code> 
     * keyword in the callback 
     * refers to this object (P) and NOT to D</b>. The callback is not intended to be 
     * used as D modificator: if you do, D layout (e.g., elements overflow or 
     * not properly displayed) might be messed up
     * 
     * <h3>Popup initialization</h3>
     * <p>In <code>P=$.popup(arg)</code>, the constructor argument, arg, is either 
     * a string, a jquery element or an object. 
     * If string, the argument will be converted to the plain object {content:$(arg), focusable:true}
     * If jQuery element, the argument will be converted to the plain object {content: arg, focusable:true}
     * 
     * <p>If arg is a plain object, it must eb an object with one or more of the following property names. 
     * None of them is mandatory, but
     * at least the property 'content' should be specified (unless showing an empty div is what you want to get).
     * 
     * <p><code><b>content : [string|jQueryObject|Array|PlainObject] (default: "")</b></code>: 
     * the popup content. It can be set also at any time via <code>P.setContent(arg)</code> 
     * when the popup div is not showing prior to calling <code>P.show()</code>
     * <p>It Can be:
     * <ul>
     *  <li> A plain object (form filling popup). Each pair represents a row in the popup. 
     *  The row will be a div with a &lt; span &gt; with innerHTML=key followed 
     *  by an &lt; input &gt; with value = val (&lt; span &gt;s and &lt; input &gt;s 
     *  horizontal alignement is automatically calculated. For extra css, inspect the 
     *  result in a browser debugger and add specified classes. 
     *  The type of &lt; input &gt; is determined as follows:
     *      <ul>
     *          <li> val is boolean: &lt; input type=checkbox &gt;
     *          <li> val is an array of strings: &lt; select &gt; tag (non multi 
     *          select. Yes, it is not an &lt; input &gt; tag in the strict term...)
     *          <li> val is number: &lt; input type=text &gt; with val as value
     *          <li> otherwise: &lt; input type=text &gt; with val.toString as value
     *      </ul>
     *  </li>
     *  If D holds any clickable element with specified attribute marking it as "ok invoker" 
     *  (<code>P.getOkInvokerAttrName()</code>) 
     *  a click on the ok button will trigger the popup onOk callback (see below) with
     *  argument a dictionary of (key: &lt; input &gt; value) pairs. 
     *  If B is shown, its ok button (an anchor by default) has the specified attribute and 
     *  therefore will behave as ok invoker automatially
     *  <li> an array of strings for (list item popup). Each array element S (string) 
     *  will be represented by a row of the popup (internally, an anchor with innerHTML=S). 
     *  A click on each anchor triggers the 
     *  onOk callback (see onOk below), with argument an object of the form {selIndex:N},
     *  where N is the index of the anchor being clicked
     *  <li> a jQuery object: the content will be appended to the popup
     * </ul>
     *  In all of these cases, object inserted in the popup via the content property 
     *  can be retrieved and manipulated via <code>P.getDiv()</code>
     * 
     * <p><code><b>classes : [string|Array_of_strings|PlainObject] (default: '')</b></code>: 
     * The value will be passed as argument to <code>P.addClass</code>, see above.
     * Classes is used instead of 'class' as the latter seems apparently no a valid plain object keyword in IE8
     * <p><code><b>invoker: [jQueryElement] (default: jQuery(window))</b></code>: 
     * If invoker is:
     * <ul>
     *  <li>a clickable element (anchor, button, input of type button or submit), 
     *  then the PopupDiv will behave as a popup dialog of invoker. Thus, when <code>P.show()</code> 
     *  is called, P will calculate the available space nearby invoker to show up 
     *  D in the window corner next to invoker which best fits 
     *  D size. In this case the parameter <code>focusable</code> (see below) 
     *  is usually set to true
     *  <li>Otherwise, D will be centered inside invoker. Note that D is appended to 
     *  the body element, so it will be visually centered in invoker but it does not 
     *  belong to invoker children hierarchy (unless invoker is the jQuery('body') element). 
     * </ul>
     * 
     * <p><code><b>bounds : [Number|Array_of_Numbers|PlainObject]</b></code> (default: <code>{'top':5, 'left':5, 'right':5, 'bottom':5}</code>): 
     * Specifies the
     * insets (margins) of D within invoker <b>relative to the rectangle R 
     * where D will be displayed</b>. The insets of D within R can be considered as 
     * css margins <b>but relative to R edges, so positive values 
     * (negative will default to zero) will reduce R size, basically controlling D 
     * max size</b>. R is calculated according to the value of invoker: 
     * if the latter is undefined, then it is the browser window viewport W, otherwise it is 
     * a portion of W calculated to give D the size and position of a popup menu (relative 
     * to its invoker). This argument is useful to avoid a popup to take the whole 
     * window viewport (if invoker is undefined) or to leave some margin for 
     * css effects like box-shadow.  
     * <p>If Array, each array element controls a given R edge exactly as in css margin, paddding and borders:
     * Consequently, a 4-element array elements control the [top, right, bottom, left] edges, 
     * a 3-element 
     * array elements control the [top, right/left, bottom] edges, a 2-element array 
     * elements control the [top/bottom, right/left] edges,  
     * and a single element array (or a number) sets all edges the given value. 
     * <p>Each element can be in percentage of invoker 
     * size if lower than 1 (eg, bounds.left = 0.25: popup left margin is 25% of 
     * invoker width, and so on) or as pixel measure (if greater than 1)
     * 
     * <p><code><b>focusable [boolean]</b></code> (Default: <code>false</code>):
     * When true, the popup gains the focus when shown, and disappears when looses the focus
     * (<code>P.close()</code> is called, see below). 
     * NOTE: As handling focus event is tricky, so we rely on mouse and key event 
     * bubbled up to the document, but it is anyway a workaround which works in most 
     * - but not all - cases
     * 
     * <p><code><b>onOk [function]</b></code> (default: <code>undefined</code>): 
     * callback to be executed when the ok button is pressed. The callback takes as 
     * argument a dictionary that the popup will build by retrieving all &lt; input &gt; 
     * &lt; select &gt; or &lt; textarea &gt; elements among its children (recursive search): 
     * each element E whith attribute <code>P.getFormDataAttrName()</code> (which defaults 
     * to "data-key", conforming to HTML5), will denote the property [A_value:E_value] 
     * of the dictionary. 
     * <br>Elements with such attributes are automatically created when content (see above) is
     * an object (form fill popup) or an array (listItem popup), but the user might provide its 
     * own custom implementation, providing e.g., input element with the given attribute 
     * (whatever value they have, but <code>true</code> is a good convention).
     * <b>After each onOk callback has been executed, if none of the callbacks returns 
     * the boolean <code>false</code> popup.close() will always be called</b>
     * You can always bind ok callbacks later via <code>P.bind('ok', callback)</code>
     * 
     * <p><code><b>onClose [function]</b></code> (default: <code>undefined</code>): 
     * callback to be executed when the <code>P.close()</code> is called. The callback 
     * must take one argument (string) which  denotes wether the popup is closing  
     * because of 1) the ok button click, 2) a lost of focus, 3) the close button click or 4)
     * another reason (eg, a custom code call to popup.close()). In these cases, 
     * the string argument is 1) "okClicked", 2) "focusLost", 3) "closeClicked" and 4) the empty string "" (or undefined)
     * These callbacks are executed at the end of all close operations, therefore  
     * D might have been removed from the document tree at the time this callback is executed.
     * You can always bind ok callbacks later via <code>P.bind('close', callback)</code>
     * 
     * <p><code><b>header : [function|boolean|string|jQueryElement]</b></code> (default : <code>undefined</code>), and 
     * <br><code><b>footer : [function|boolean|string|jQueryElement]</b></code> (default : <code>undefined</code>)
     * Two callbacks to be executed to customize T and B, respectively. 
     * T and B will be passed as argument to the relative functions, whose <code>this</code>
     * keyword will refer to P.
     * If the argument is a boolean false, then the callback argument $div (T or B depending
     * on the key) will be hidden, i.e. the argument will be converted to the function:
     * <pre>
     * function($div){$div.css('display','none');}
     * </pre>
     * if string, the argument will be converted to the function:
     * <pre>
     * function($div){$div.html($(arg));}
     * </pre>
     * And if jQueryElement, the argument will be converted to the function
     * <pre>
     * function($div){$div.html(arg);}
     * </pre>
     * <p>T by default has an anchor (with style float:right and inner html 'x') for closing the popup, 
     * i.e., with custom attribute <code>this.getCloseInvokerAttrName()</code>, 
     * a text node to display the popup title, and a div with style clear:both 
     * which does nothing but let the text node text wrapping "around" the anchor.
     * <p>B has text-align set to 'right' and an anchor inside it with for perfoming 
     * the ok action, i.e. a custom attribute <code>this.getOkInvokerAttrName()</code>, 
     * and inner html = 'Ok'.
     * 
     * 
     * <p><code><b>zIndex : [Integer]</b></code> (default: <code>10000</code>): the popup zIndex. Should be left untouched unless there are issues with other component with hight zIndex.
     *  
     * <p>And finally, EXAMPLES:</p>
     * Given an anchor &lt; a &gt; (jQuery element)
     *      1) show a popup when clicking  leaving the user choose among three oprions: 'banana', 'orange' and 'apple'. The popup will
     *      behave as a default popup hiding when it looses focus
     *      <pre>//setup parameters
     *      var choices = ['banana','oranges','apples'];
     *      var dict = {
     *          content: choices,
     *          onOk: function(data){
     *              var fruitChosen = choices[data.selIndex];
     *              //.. do something with the selected fruit....
     *          },
     *          focusable: true,
     *          invoker: a
     *      }
     *      //bind the click event of the anchor:
     *      a.click(function(){ new PopupDiv(dict).show();});</pre>
     *
     *      1) show a popup when clicking  leaving the user choose the fruit as text. The popup will close either when ok or close are clicked
     *      <pre>//setup parameters
     *      var choices = {'yourFruit':'banana'}; //banana will be the default value when the popup shows
     *      var dict = {
     *          content: choices,
     *          onOk: function(data){
     *              var fruitChosen = data['yourFruit'];
     *              //.. do something with the selected fruit....
     *          },
     *          invoker: a
     *      }
     *      //bind the click event of the anchor:
     *      a.click(function(){ new PopupDiv(dict).show();});</pre>
     *
     *      3) show a message dialog which expires after 1500 milliseconds. No invoker specified means the popup will be centered in screen
     *      <pre>new PopupDiv({
     *          content: "i'm gonna disappear!", //one could also input "<span>i'm gonna disappear!</span>" or jQuery('<span/>').html("i'm gonna disappear!")
     *          }.show('fast', function(){
     *              var me = this; //this refers to the popup object, not the div being animated
     *              setTimeout(function(){
     *                  me.close();
     *              }, 1500);
     *          });
     *      });</pre>
     */
    function PopupDiv() {
        //var $ = jQuery;
        //var me = this;
        var data = {};
        if (arguments.length && arguments[0]) {
            data = arguments[0];
        }

        if ((typeof data === 'string') || (data instanceof $)) {
            var strd = data;
            data = {'content': strd, 'focusable': true}; //focusable because otherwise there might be theoretically no way to hide it 
        }
        //var wdw = $J(window);
        var div = $('<div/>').addClass('_popupdiv_');


        var header = $('<div/>').addClass('_popupdiv_header_'); //.append(buttClose).append(' ').append($J('<div/>').css('clear', 'both')); //.css('float','right');
        this.header(header);


        var container = $('<div/>').addClass('_popupdiv_container_'); //.css('overflow', 'auto');

        var footer = $('<div/>').addClass('_popupdiv_footer_'); //.append(buttOk);
        this.footer(footer);

        //defining immediately the method getDiv (because it is used below)
        this.getDiv = function () {
            return div;
        };
        //setting functions:

        var listeners = {};
        this.getListeners = function () {
            return listeners;
        };

        div.append(header).append(container).append(footer);

        //setting instance-specific properties:
        //for safetiness, if there is a 'content' property, add it later:
        var contentData = undefined;
        for (var k in data) {
            if (data.hasOwnProperty(k)) {
                if (!(typeof (k) === 'string')) {
                    this[k] = data[k];
                    continue;
                }
                var k_lcase = k.toLowerCase();
                if (k_lcase === 'onok' || k_lcase === 'onclose') {
                    this.bind(k_lcase.substring(2), data[k]);
                } else if (k_lcase === 'content') {
                    contentData = data[k];
                } else {
                    if (k_lcase === 'classes') {
                        this.addClass.apply(this, $.isArray(data[k]) ? data[k] : [data[k]]);
                    } else if (k_lcase === 'title') {
                        this.title(data[k]);
                    } else if (k_lcase === 'header' || k_lcase === 'footer') {
                        if (data[k] === false) {
                            data[k] = function (div) {
                                div.css('display', 'none');
                            };
                        } else {
                            if (typeof (data[k]) === "string") {
                                data[k] = $(data[k]);
                            }
                            if (data[k] instanceof $) {
                                var v = data[k];
                                data[k] = function (div) {
                                    div.empty().append(v);
                                };
                            }
                        }
                        if (typeof data[k] === 'function') {
                            data[k].apply(this, k_lcase === 'header' ? [header] : [footer]);
                        }
                    } else {
                        this[k] = data[k];
                    }
                }
            }
        }

        if (contentData !== undefined) {
            this.setContent(data[k]);
        }
        return this;
    }

    $.popupdiv = function (args) {
        return new PopupDiv(args);
    };

    //populating the prototype object:
    (function (p) {
        //in the functions below, this refers to the new Popup instance, not to the prototype

        //private static variables
        //var $ = jQuery;
        var w_ = window;
        var d_ = document;
        var wdw = $(w_);

        p.header = function (div) {
            //div.css({'text-align': 'right'});
            var btn = $('<a>').attr(this.getCloseInvokerAttrName(), 'true').attr('href', '#').css('float', 'right').html('x');
            div.append(d_.createTextNode(' ')).append(btn).append($('<div>').css('clear', 'both'));
            //div.css('margin-bottom', '1em');
            return div;
        };

        p.footer = function (div) {
            div.css({'text-align': 'right'});
            var btn = $('<a>').attr(this.getOkInvokerAttrName(), 'true').attr('href', '#').html('Ok');
            div.append(btn);
            //div.css('margin-top', '1em');
            return div;
        };

        p.addClass = function () {
            var args = this._parseClassArgs.apply(this, arguments);
            for (var i = 0; i < args.length; i += 2) {
                args[i].addClass(args[i + 1]);
            }
            return this;
        };

        p.removeClass = function () {
            var args = this._parseClassArgs.apply(this, arguments);
            for (var i = 0; i < args.length; i += 2) {
                args[i].removeClass(args[i + 1]);
            }
            return this;
        };

        //parses args for addClass and removeClass functions
        //if not undefined, the returned array is an array of [jQueryElm, string, ....] pairs
        //denoting the elements and relative classes
        p._parseClassArgs = function () {
            if (!arguments || !arguments.length) {
                return undefined;
            }
            var div = this.getDiv();

            if (arguments.length === 1) {
                if (typeof arguments[0] === 'string') {
                    return [div, arguments[0]];
                } else if ($.isPlainObject(arguments[0])) {
                    var a = ["", "", "", ""];
                    for (var key in arguments[0]) {
                        var key_lc = key.toLowerCase();
                        if (key_lc === 'header' || key_lc === 'top') {
                            a[1] = arguments[0][key];
                        } else if (key_lc === 'container' || key_lc === 'middle') {
                            a[2] = arguments[0][key];
                        } else if (key_lc === 'footer' || key_lc === 'bottom') {
                            a[3] = arguments[0][key];
                        } else if (key_lc === 'popup' || key_lc === 'main') {
                            a[0] = arguments[0][key];
                        }
                    }
                    return this._parseClassArgs.apply(this, a);
                }
                return undefined;
            }
            var children = div.children();
            var a = [];
            var assign = function (elm, value, array) {
                if (typeof (value) === 'string') {
                    if (value) {
                        array.push(elm);
                        array.push(value);
                    }
                }
                return array;
            };
            if (arguments.length === 2) {
                a = assign(children.eq(0), arguments[0], a);
                a = assign(children.eq(2), arguments[1], a);
            } else if (arguments.length === 3) {
                a = assign(children.eq(0), arguments[0], a);
                a = assign(children.eq(1), arguments[1], a);
                a = assign(children.eq(2), arguments[2], a);
            } else if (arguments.length > 3) {
                a = assign(div, arguments[0], a);
                a = assign(children.eq(0), arguments[1], a);
                a = assign(children.eq(1), arguments[2], a);
                a = assign(children.eq(2), arguments[3], a);
            }
            return a ? a : undefined;
        };

        var popupStaticId = new Date().getTime();

        //Self explanatory: note that argument must be a jQuery element
        p.isClickElement = function (element) {
            return element && element.length === 1 && element instanceof $ && element[0] !== w_ && element[0] !== d_ &&
                    (element.is('a') || element.is('input[type=button]') || element.is('button') ||
                            element.is('input[type=submit]'));
        };

        p.getId = function () {
            var div = this.getDiv();
            if (!(div.attr('id'))) {
                var pp = popupStaticId;
                var pre = 'popupdiv_';
                var idstr = pre + pp;
                while ($('#' + idstr).length) {
                    popupStaticId++;
                    pp = popupStaticId;
                    idstr = pre + pp;
                }
                div.attr('id', idstr);
            }
            return div.attr('id');
        };


        //default properties which can be overridden
        //p.shadowOffset = 4; //zero means: no shadow
        p.invoker = wdw;
        p.bounds = {
            'top': 5, //0.25,
            'left': 5, //0.25,
            'right': 5, //0.25,
            'bottom': 5 //0.25
        }; //note that sepcifying top+bottom>=1 there is undefined behaviour (in chrome, offset is set but height takes all available space)


        p.focusable = false;
        p.zIndex = 10000;

        //returns the data associated to this popup. Basically, it searches for all input, select or textarea with attribute
        //this.getFormDataAttrName(). The use of a custom attribute is cross browser, note that some attributes, eg name, are
        //not (name is not safe in IE for instance)
        p.getFormData = function () {
            var elms = this.getDiv().find('input,select,textarea');
            var ret = {};
            var att = this.getFormDataAttrName();
            elms.each(function (i, e) {
                var ee = $(e);
                var key = ee.attr(att);
                if (key) {
                    ret[key] = ee.val();
                }
            });
            return ret;
        };

        //Binds the specified callback to the specified eventName
        //eventname: show, close or ok
        p.bind = function (eventName, callback) {
            var listeners = this.getListeners();
            if (listeners.hasOwnProperty(eventName)) {
                listeners[eventName].push(callback);
            } else {
                listeners[eventName] = [callback];
            }
            return this;
        };

        //Unbinds the specified callback to the specified eventName
        //eventname: close or ok
        p.unbind = function (eventName) {
            var listeners = this.getListeners();
            if (eventName && listeners.hasOwnProperty(eventName)) {
                delete listeners[eventName];
            } else if (!eventName) {
                for (var k in listeners) {
                    if (listeners.hasOwnProperty(k)) {
                        delete listeners[k];
                    }
                }
            }
            return this;
        };

        //Triggers the specified callback to the specified eventName
        //eventname: show, close or ok. close accepts a second optional argument which is:
        //1) "okClicked", 2) "focusLost", 3) "closeClicked" and 4) the empty string ""
        p.trigger = function (eventName) {
            var listeners = this.getListeners();
            var me = this;
            if (listeners.hasOwnProperty(eventName)) {
                var callbacks = listeners[eventName];
                var i = 0;
                if (eventName === 'ok') {
                    var data = this.getFormData();
                    var close = true;
                    for (i = 0; i < callbacks.length; i++) {
                        if (callbacks[i].apply(me, [data]) === false) {
                            if (close) {
                                close = false;
                            }
                        }
                    }
                    if (close) {
                        this._closeOrigin = 'okClicked';
                        this.close();
                    }
                } else if (eventName === 'close') {
                    var str = "";
                    if (arguments && arguments.length > 1 && typeof arguments[1] === 'string') {
                        str = arguments[1];
                    }
                    for (i = 0; i < callbacks.length; i++) {
                        callbacks[i].apply(me, [str]);
                    }
                } else {
                    for (i = 0; i < callbacks.length; i++) {
                        callbacks[i].apply(me);
                    }
                }
            }
        };

        p.setContent = function (content) {
            //alert(content + " " + (typeof content))
            var me = this;

            var div = this.getDiv();
            var container = div.children().eq(1);
            //div.appendTo('body'); //necessary to properly display the div size
            container.empty();
            var att = this.getFormDataAttrName();
            //var checkForOkAndCloseInvokers = false;
            if (content instanceof $) {
                container.append(content);
                //checkForOkAndCloseInvokers = true;
            } else if (content instanceof Array) {

                //var name = this.getListItemName();

                //Workaround: use an input of type hidden where to store the selected value:
                var input = $('<input/>').attr('type', 'hidden').attr(att, 'selIndex');
                var setEvents = function (idx, anchor, input) {
                    anchor.click(function () {
                        input.val(idx);
                        me.trigger('ok');
                        return false;
                    }).focus(function () { //focus because we need to get the value if ok is present
                        input.val(idx);
                    });
                };
                var listItems = $([]);
                for (var h = 0; h < content.length; h++) {
                    var item = content[h];
                    var a = $('<a/>').attr('href', '#').html("" + item); //.css('whiteSpace','nowrap');
                    listItems = listItems.add(a);
                    setEvents(h, a, input);
                    container.append(a);
                }
                //set css and class on all listitem anchor:
                //set margin to properly display the outline (border focus)
                //this css can be overridden (see lines below) as it is not strictly necessary
                listItems.css({
                    'margin': '2px'
                });

                //override css which are necessary to properly display the listItem:
                listItems.css({
                    'position': '',
                    'display': 'block'
                });
                container.append(input);
            } else if (content && content.constructor === Object) {
                var leftElements = $([]);
                var rightElements = $([]);
                var maxw = [0, 0];
                var insert = function (e1, e2) {
                    var lineDiv = $('<div/>');
                    if (!e2) {
                        e2 = e1;
                        e1 = $('<span/>');
                    }
                    rightElements = rightElements.add(e2);
                    leftElements = leftElements.add(e1);
                    container.append(lineDiv.append(e1).append(e2));
                    return lineDiv;
                };
                var title, component;

                var max = Math.max; //instantiate once
                var lineDiv = undefined;
                var lineDivs = $([]);
                for (var k in content) {
                    if (content.hasOwnProperty(k)) {
                        var val = content[k];
                        if (typeof val === 'string' /*|| typeof val == 'number'*/) {
                            title = $('<span/>').html(k);
                            maxw[0] = max(maxw[0], k.length);
                            maxw[1] = max(maxw[1], val.length);
                            component = $('<input/>').attr('type', 'text').val(val).attr(att, k);
                            lineDivs = lineDivs.add(insert(title, component));
                        } else if (typeof val === 'number') {
                            title = $('<span/>').html(k);
                            maxw[0] = max(maxw[0], k.length);
                            maxw[1] = max(maxw[1], val.length);
                            component = $('<input/>').attr('type', 'number').val(val).attr(att, k);
                            lineDivs = lineDivs.add(insert(title, component));
                        } else if (val === true || val === false) {
                            var id = this.getId() + "_checkbox";
                            title = $('<input/>').attr('type', 'checkbox').attr(att, k).attr('id', id);
                            if (val) {
                                title.attr('checked', 'checked');
                            } else {
                                title.removeAttr('checked');
                            }
                            component = $('<label/>').attr('for', id).html(k);
                            maxw[1] = max(maxw[1], k.length);
                            lineDivs = lineDivs.add(insert($('<span/>').append(title), component));
                            //Date below is commented out cause date is not still fully compatible across browsers, see doc above
                        }/*else if((val instanceof Date) || ((val instanceof Array) && val.length==2 && (val[0] instanceof Date) && 
                         (val[1]==='date' || val[1]==='datetime' || val[1]==='datetime-local' || val[1]==='month' || val[1]==='time' || val[1]==='time' || 
                         val[1]==='week'))){
                         var type_ = (val instanceof Date) ? 'date' : val[1]
                         val = (val instanceof Date) ? val : val[0]
                         title = $('<span/>').html(k);
                         maxw[0] = max(maxw[0],k.length);
                         maxw[1] = max(maxw[1],val.length);
                         component = $('<input/>').attr('type',type_).val(val).attr(att,k);
                         lineDivs = lineDivs.add(insert(title,component));
                         }*/ else if (val instanceof Array) {
                            title = $('<span/>').html(k);
                            maxw[0] = max(maxw[0], k.length);
                            component = $('<select/>').attr('size', 1).attr(att, k);
                            for (var i = 0; i < val.length; i++) {
                                component.append($('<option/>').val(val[i]).html(val[i]));
                                maxw[1] = max(maxw[1], val[i].length);
                            }
                            lineDivs = lineDivs.add(insert(title, component));
                        }
                        if (lineDiv) {
                            lineDiv.css('marginBottom', '1ex');
                        }
                    }
                }
                lineDivs.css({
                    'white-space': 'nowrap',
                    'marginBottom': '0.5ex'
                });
                //last div erase marginBottom
                $(lineDivs[lineDivs.length - 1]).css('marginBottom', '');


                //display: inline-block below assures that width are properly set
                //IE 6/7 accepts the value only on elements with a natural display: inline.
                //(see http://www.quirksmode.org/css/display.html#t03)
                //span and anchors are among them
                //(see http://www.maxdesign.com.au/articles/inline/)
                leftElements.add(rightElements).css({
                    'display': 'inline-block',
                    'margin': '0px',
                    'padding': '0px'
                });
                leftElements.css({
                    'textAlign': 'right',
                    'marginRight': '0.5ex',
                    'width': Math.round((3 / 5) * maxw[0]) + 'em'
                });
//            rightElements.css({
//                'width':Math.round((3/5)*max(maxw[0], maxw[1]))+'em' //approximate width
//            }); //might be zero if default values are all ""

                rightElements.width(max(maxw[0], maxw[1]));
            } else {
                container.append("" + content);
                //checkForOkAndCloseInvokers = true;
            }

            //if (checkForOkAndCloseInvokers) {

            var isClickElm = this.isClickElement;
            var okInvokers = div.find("[" + me.getOkInvokerAttrName() + "]");
            okInvokers.each(function (i, elm) {
                var $elm = $(elm);
                if (isClickElm($elm)) {
                    $elm.unbind("click").click(function () {
                        me.trigger('ok');
                        return false; //in case of anchor prevents url to have '#' at their end
                    });
//                    me.trigger('ok');
//                    return false; //in case of anchor prevents url to have '#' at their end
                }
                //$(elm).click();
            });
            var closeInvokers = div.find("[" + me.getCloseInvokerAttrName() + "]");
            closeInvokers.each(function (i, elm) {
                var $elm = $(elm);
                if (isClickElm($elm)) {
                    $elm.unbind("click").click(function () {
                        me._closeOrigin = 'closeClicked';
                        me.close();
                        return false; //in case of anchor prevents url to have '#' at their end
                    });
                }
                //$(elm).click();
            });
            //}
            return me;
        };

        p.setFocusCycleRoot = function (value) {
            //var value = this.focusable;

            //We might have several ways to attach focus events to the popup
            //In a first version, we first checked here all input select anchors and textareas, 
            //For each element E, we 
            //1) added E tabindex attribute (which makes the element focusable)
            //for navigation,
            //2) we set on E a custom attribute on them to mark them as popup focusable (pf), and 
            //3)we attached a focuslost event listener, which had to wait x milliseconds to see 
            //which was the new focus owner: if it was NOT a pf, then
            //the popup was closed, invoking popup.close('focusLost'), UNLESS we already were closing it by, e.g., a click on the x button, 
            //in that case this method was generated while closing the popup so we shouldn't call close again
            //
            //There were several cons to this method: 
            //1) the tabindex makes elements which gets the focus having an 
            //"outline" (which had to be cleared via jquery_element.css('outline', '#FFF none 0px');
            //2) new element added to the popup had to be marked as pf. In the first version, popupdiv was conceived to 
            //transform into elements arrays or dictionaries, not to hold custom jquery dynamic data, so that was fine. But in this
            //version we want to implement also the possibility to pass custom jQuery content (potentially dynamically added/removed)

            //So we decided to just not use the pf "mark" but just check if the new focus owner was inside the popup, but this did not 
            //solve the problem that new elements inside the popup which got the focus needed to have the focuslost binding, otherwise
            //moving the focus from them to a non popup div element did not close the popup (as expected)

            //In this final version, we just attach TWO events to the document: keydown and mousedown. When grabbed from the document
            //they are bubbled up from some element within it. So we check if the event.target element is inside the popup: if true, we do not
            //close the popup. The code is also much easier to understand. The only drawback (which we had btw also in the "old" implementation)
            //is for non-popup elements which do NOT bubble up: for them, there is no hope. In any case, a close button visible 
            //would leave the option to close the popup

            var popup = this.getDiv();
            //var focusAttr = this.getFocusAttr();
            var invokerIsClickable = this.isClickElement(this.invoker);
            //var children_ = popup.children();
            var thisID = this.getId();

            var firstFocElm = undefined;

            //set the method returning the first focusable element. It will be used in "show"
            this.getFirstFocusableElement = function () {
                return firstFocElm;
            };

            var doc_ = $(d_);
            var focusNameSpaces = ["keyup." + thisID, "mousedown." + thisID];
            if (!value) {
                for (var i in focusNameSpaces) {
                    doc_.unbind(focusNameSpaces[i]);
                }
                popup.css('outline', ''); //reset prop we might have set below
                return;
            }

            var elementsWithFocus = popup.find(":not(span)");

            if (invokerIsClickable) {
                elementsWithFocus = this.invoker.add(elementsWithFocus);
            }

            elementsWithFocus.each(function (i, element) {
                if (!firstFocElm) {
                    var elc = element.tagName.toLowerCase(); //work with javascript element as it might be faster, we just have to retrieve simple props
                    if ((elc === 'input' && element.getAttribute('type').toLowerCase() !== 'hidden') || elc === 'select' || elc === 'button') {
                        if (!elc.disabled) {
                            firstFocElm = $(elc);
                            return false; //breaks the jQuery each
                        }
                    }
                }
                return true;
            });

            if (!firstFocElm || !firstFocElm.length) { //assign a first focusable element in ANY case
                popup.css('outline', '#FFF none 0px'); //prevent the div to show an outline 
                popup.attr('tabindex', 0); //this makes the element focusable without setting it in a focus cycle root:
                //elements that do not support the tabindex attribute or support it and assign it a value of "0" 
                //are navigated after those which support a positive tabindex. T
                //These elements are navigated in the order they appear in the character stream.
                //(see http://www.w3.org/TR/html401/interact/forms.html#h-17.11.1)
                firstFocElm = popup;
            }

            var isInPopup = function (dom_element) {
                if (dom_element) {
                    var $p = $(dom_element);
                    //try to get the parent: if it is the popup, return again
                    while ($p.length && $p.attr("id") !== thisID) {
                        $p = $p.parent();
                    }
                    if ($p.length && $p.attr("id") === thisID) {
                        return true;
                    }
                }
                return false;
            };
            var me = this;
            var currFocusElm = firstFocElm;
            var fff = function (event) {
                currFocusElm = event.target; //generator of the event
                if (!isInPopup(currFocusElm)) {
                    if (!me.__isClosing) {
                        me._closeOrigin = 'focusLost';
                        me.close();
                    }
                }
            };
            for (var i in focusNameSpaces) {
                doc_.bind(focusNameSpaces[i], fff);
            }
        };

        p.getFirstFocusableElement = function () {
            return undefined;
        };

        //title(): returns this popupdiv title
        //title(div): returns div title
        //title(string) sets this popup div title, returning this object
        //title(div, string), sets the title on div
        //Setting title means retrieving the first text node and, if such a node is found, setting its value to the given string
        //Getting title means retrieving the first text node and, if such a node is found, returning its value, or the empty string
        p.title = function () {
            var with_arg = arguments && arguments.length > 0;
            var subdiv = with_arg && arguments[0] instanceof $ ? arguments[0] : this.getDiv().children().eq(0);

            var text = subdiv.contents().filter(function () {
                return this.nodeType === 3;
            });

            var node = text.length ? text.get(0) : undefined; //returns a node, not a jquery object

            if (!with_arg) {
                if (node) {
                    if (node.textContent) {
                        return node.textContent;
                    } else if (node.nodeValue) {
                        return node.nodeValue;
                    }
                }
                return '';
            }

            var title = with_arg && arguments[0] instanceof $ ? arguments[1] : arguments[0];
            if (typeof (title) === 'string') {
                if (node) {
                    //if title is the empty string, apparently the text node seems to be "deleted", so resetting
                    //the title later has no effect. Setting a white space is not really perfect, as we could have extra space. However,
                    //if assures at least a minimum width if the container is empty
                    if (node.textContent) {
                        node.textContent = title || ' ';
                    } else if (node.nodeValue) {
                        node.nodeValue = title || ' ';
                    }
                }
            }
            return this;
        };

        p.setTitle = function (title) { //DEPRECATED, used for backward compatibility
            return this.title(title);
        };

        p.isShowing = function () {
            return this.getDiv().is(':visible');
        };

        p.show = function () {
            this._show.apply(this, [this._parseShowHideArg.apply(this, arguments), '']);
            //_parseShowHideArg() defined some lines below, after this.close callback. Returns a plain object
        };

        p.fadeIn = function () {
            this._show.apply(this, [this._parseShowHideArg.apply(this, arguments), 'fade']);
            //_parseShowHideArg() defined some lines below, after this.close callback. Returns a plain object
        };


        p._show = function (plainobject, actionCommand) {

//            var _do_show = actionCommand === 'fade' ? function (div, arg) {
//                div.fadeIn(arg);
//            } : function (div, arg) {
//                div.show(arg);
//            };

            var _do_show = function (div, arg) {
                div.show(arg);
            };

            var default_duration = plainobject.duration;

            this._do_hide = function (div, arg) {
                if (!arg.duration && default_duration) {
                    arg.duration = default_duration;
                }
                div.hide(arg);
            };

            if (actionCommand === 'fade') {
                _do_show = function (div, arg) {
                    div.fadeIn(arg);
                };
                this._do_hide = function (div, arg) {
                    if (!arg.duration && default_duration) {
                        arg.duration = default_duration;
                    }
                    div.fadeOut(arg);
                };
            }


            var div = this.getDiv();
            var me = this;
            var invoker = this.invoker;
            var isClickElement = this.isClickElement(invoker);
            //this._isClickElement = isClickElement;
            var setBoundsCallback = isClickElement ? this._setBoundsAsPopup : this._setBoundsInside;
            //this.setOffset = isClickElement ? this._setOffsetAsPopup : this._setOffsetInside;


            var subdiv = div.children();

            if (!div.parent().length) { //to be done before setBounds
                //actually, to be defined before everything, as e.g. the css display (see below) changes in chrome '
                //when a parent is non undefined
                div.appendTo('body');
            }

            this.setFocusCycleRoot(this.focusable); //must be called after the popup is visible

            if (isClickElement) {
                //storing click events, when showing clicking on an event must give the focus to the popup
                //old handlers will be restored in close()
                this['_tmpHandlers' + this.getId()] = undefined;
                var focusElm = this.getFirstFocusableElement();
                if (focusElm) {
                    var oldHandlers = [];
                    var type = 'click';
                    //data("events") removed from jQuery 1.8 on
                    //see http://blog.jquery.com/2012/08/09/jquery-1-8-released/
                    //
                    //therefore, commented this line:
                    //var clickEvents =invoker.data("events")[type];
                    //and added:
                    var clickEvents = invoker.data("events");
                    if (!clickEvents) {
                        clickEvents = $._data(invoker[0], "events");
                    }
                    clickEvents = clickEvents[type];

                    $.each(clickEvents, function (key, value) {
                        oldHandlers.push(value);
                    });
                    invoker.unbind(type); //remove (temporarily) the binding to the event.
                    //for instance, if we show the popup by clicking invoker, when the popup is shown do nothing
                    //on clicking invoker until popup.hide is called

                    this['_tmpHandlers' + this.getId()] = oldHandlers;
                    invoker.unbind(type).bind(type, function (evt) {
                        //let the invoker have focus and let it be recognized as an element which does not blur the popup:
                        //invoker.attr('tabindex',0).attr(focusAttr,'true');
                        //FIXME: THE FACT THAT THE POPUP RECOGNIZES THAT INVOKER FOCUS MUST NOT CLOSE THE POPUP IS SET IN
                        //setFocusCycleRoot, NOT HERE
                        if (div.length && div.is(':visible')) {
                            focusElm.focus();
                            return false;
                        }
                        //something wrong: close the popup and restore the hanlers
                        me.close.apply(me);
                        return false;
                    });
                }

            }

            var overflows = setBoundsCallback.apply(this); //after this call, the main div is set to visible:hidden 
            //(it is absolutely positioned and appended to the document, so it does not move any other component, 
            //and its central component css overflow MUST STILL be set to auto

            //var place = undefined; //  this.setOffset;
            var customShowFunc = undefined; //arg of the show function (defined when parsing show arguemnts below)
            var postShowFcn = function () {
                //resetting overflow: See notes below
                subdiv.eq(1).css('overflow', overflows ? 'auto' : 'visible');

                //
                //adding window resize interval to track window changes
                //when window is resized, try repositioning the popup
                var w = wdw.width();
                var h = wdw.height();
                me._resizeTimeInterval = setInterval(function () { //FIXME: reassing widths and heights!!!
                    var w2 = wdw.width();
                    var h2 = wdw.height();
                    if (w2 !== w || h2 !== h) {
                        w = w2;
                        h = h2;
                        setTimeout(function () {
                            if (!me.isShowing() || me.__isClosing) {
                                return;
                            }
                            if (wdw.width() === w2 && wdw.height() === h2 && setBoundsCallback) {
                                var overflows = setBoundsCallback.apply(me);
                                div.add(div.children()).css('visibility', ''); //restore visibility (set in setBounds's' presizeFcn)
                                subdiv.eq(1).css('overflow', overflows ? 'auto' : 'visible');
                            }
                        }, 100);
                    }
                }, 200);

                if (typeof (customShowFunc) === 'function') {
                    customShowFunc.apply(me);
                }
                var v = me.getFirstFocusableElement();
                if (v) {
                    v.focus();
                }
            };


            //PARSING ARGUMENTS TO BEHAVE AS JQUERY SHOW
            //var arg = this._parseShowHideArg(arguments); //defined some lines below, after this.close callback. Returns a plain object
            var arg = plainobject;
            if (arg.complete) {
                customShowFunc = arg.complete;
            }
            arg.complete = function () {
                postShowFcn();
            };

            div.hide(); //hide popup, without animation
            div.add(div.children()).css('visibility', ''); //restore visibility (set in setBounds's' presizeFcn)

            //NOW PROBLEM        
            //div.show(arg);
            //RESULTS IN THE CENTRAL COMPONENT C SHOWING SCROLLBARS EVEN IF NOT NEEDED. I EXPERIENCED THE FOLLOWING CASES:
            //1) IT HAPPENS 
            //THAT (USING A DEBUGGER) THE DIV CONTAINER CAN BE DISPLAYED WTHOUT SCROLLBARS BEFORE DIV.HIDE ABOVE, AND AND THEN
            //IT HAS THEM AFTER DIV.SHOW. THERE MUST BE SOME ROUNDING PROBLEM IN EITHER SHOW OR BROWSER, OR A PROBLEM IF c HAS OVERFLOW:AUTO 
            //(E.G., SCROLLBARS ARE SHOWN DURING ANIMATION, CAUSE THE CONTENT OVERFLOWS, AND SOMEHOW THE BROWSER "FORGETS" OR IS UNABLE TO HIDE THEM AT THE END OF 
            //THE ANIMATION) OR BOTH
            //2) IN IE, SETTING OVERFLOW:AUTO SEEMS TO ADD SCROLLBARS ANYWAY EVEN IF THE CONTENT DOESNOT OVERFLOWS
            //
            //SOLUTION1: USE FADEIN (SEE BELOW)
            //SOULTION2: CHECK IF CONTENT OVERFLOWS AND SET OVERFLOW AUTO ONLY IN CASE
            //

            //subdiv.eq(1).css('overflow', 'hidden'); //to avoid showing scrollbars. Should we leave as default (it should be set as default value, visible)
            //if we use fadeIn, we could immediately set it as 'auto', and avoid doing it in the postShowFcn above. However, it should be harmless so we prefer 
            //writing less code which would confuse the reader

            _do_show.apply(this, [div, plainobject]);

        };

        p._setBoundsAsPopup = function () {
            var invoker = this.invoker;

            var preSize = this._preSizeFcn();  //re-initializes css display, dimensions (width height) position (top, bottom) of all popup div elements

            var div = this.getDiv();

            var windowRectangle = this.getBoundsOf(wdw); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
//        var div_width = div.outerWidth(false);
//        var div_height = div.outerWidth(false);

            var invokerOffset = invoker.offset();

            var invokerOuterHeight = invoker.outerHeight();
            var spaceAbove = invokerOffset.top - windowRectangle.y;
            var spaceBelow = windowRectangle.height - invokerOuterHeight - spaceAbove;
            var placeAbove = spaceAbove > spaceBelow && div.outerHeight(false) > spaceBelow;

            var invokerOuterWidth = invoker.outerWidth();
            var spaceRight = windowRectangle.x + windowRectangle.width - invokerOffset.left;
            var spaceLeft = invokerOffset.left + invokerOuterWidth - windowRectangle.x;
            var placeLeft = spaceLeft > spaceRight && div.outerWidth(false) > spaceRight;



            var x = placeLeft ? invokerOffset.left + invokerOuterWidth - div.outerWidth(true) : invokerOffset.left;
            var y = (placeAbove ? invokerOffset.top - div.outerHeight(true) :
                    invokerOffset.top + invokerOuterHeight);

            var height = (placeAbove ? spaceAbove : spaceBelow);
            var width = (placeLeft ? spaceLeft : spaceRight);

            var rect = this._getRectangle(x, y, width, height, this.bounds);


            div.css({//THIS SETS THE WIDTH AND HEIGHTS OF THE DIV INCLUDING PADDING AND BOTTOM, AS WE SET THE BOX-SIZING CSS TO BORDERBOX IN _PRESIZEFCN
                'max-width': rect.w + 'px',
                'max-height': rect.h + 'px',
                'min-width': invoker.outerWidth(false) + 'px'
            });

            div.css({//REFER TO DIV LEFT AND TOP MARGIN EDGES, see https://developer.mozilla.org/en-US/docs/Web/CSS/left
                'left': rect.x + 'px',
                'top': rect.y + 'px'
            });

            var postSize = this._postSizeFcn(); //Sets some more css values which must be set at the end. Most of the problems here regard IE. 

            return preSize[0] > postSize[0] || preSize[1] > postSize[1] ? true : false;
        };


        //Sets the popup div dimensions (css width height). See show() for an usage. 
        //inside the popup invoker argument, which is not a clickable element (it might be undefined and in this case it defaults to the window object). 
        //Returns a boolean indicating if the central div overflows
        p._setBoundsInside = function () {
            var parent = this.invoker;
            // var pd = this.bounds;
            //var boundsExact = this.boundsExact;

//        var div = this.getDiv();

            var preSize = this._preSizeFcn(); //re-initializes css display, dimensions (width height) position (top, bottom) of all popup div elements

            var bounds = this.getBoundsOf(parent); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object


            var x = bounds.x;
            var y = bounds.y;
            var w = bounds.width;
            var h = bounds.height;

            var rect = this._getRectangle(x, y, w, h, this.bounds);

            var div = this.getDiv();
            var w = div.outerWidth(true);
            var h = div.outerHeight(true);

            //must be centered, so if the window is shorter shift x and y:
            if (w < rect.w) {
                rect.x += parseInt((rect.w - w) / 2);
            }
            if (h < rect.h) {
                rect.y += parseInt((rect.h - h) / 2);
            }

            div.css({//THIS SETS THE WIDTH AND HEIGHTS OF THE DIV INCLUDING PADDING AND BOTTOM, AS WE SET THE BOX-SIZING CSS TO BORDERBOX IN _PRESIZEFCN
                'max-width': rect.w,
                'max-height': rect.h
            });

            div.css({//REFER TO DIV LEFT AND TOP MARGIN EDGES, see https://developer.mozilla.org/en-US/docs/Web/CSS/left
                'left': rect.x + 'px',
                'top': rect.y + 'px'
            });


            var postSize = this._postSizeFcn(); //Sets some more css values which must be set at the end. Most of the problems here regard IE. 
            return preSize[0] > postSize[0] || preSize[1] > postSize[1] ? true : false;
        };


        //Function called from _setBoundsAsPopup and _setBoundsInside to re-initialize all css properties (div hidden, dimensions -width and height - set to '' etcetera)
        p._preSizeFcn = function () {
            var div = this.getDiv();
            var subdivs = div.children();
            //subdivs.css('display', 'none');
            var subdivsshow = subdivs.eq(1);
            var topdiv = subdivs.eq(0);
            if (topdiv.css('display') !== 'none') { //css gets the COMPUTED style
                subdivsshow = subdivsshow.add(topdiv);
            }
            var bottomdiv = subdivs.eq(2);
            if (bottomdiv.css('display') !== 'none') {
                subdivsshow = subdivsshow.add(bottomdiv);
            }

            subdivsshow = subdivsshow.add(div);
            subdivsshow.css({
                'display': 'block',
                //'float': '',
                //'overflow': 'visible'
                //});

                //FIXME: reset also poosition property?

                //reset properties:
                //subdivsshow.css({
                'max-height': '',
                'max-width': '',
                'min-height': '',
                'min-width': '',
                'height': '',
                'width': '',
                'overflow': '',
                'visibility': 'hidden',
                'float': ''
            });

            div.css({
                //'background-color': '#ff0', //FIXME: remove it, is FOR DEBUG!!!
                //'display' : 'inline-block'
                //'margin': '0px',
                'zIndex': this.zIndex,
                'position': 'absolute',
                'box-sizing': 'border-box',
                '-webkit-box-sizing': 'border-box',
                '-moz-box-sizing': 'border-box'
                        //'box-shadow': '',
                        //'visibility': 'hidden'
            });

            var size = [subdivs.eq(1).width(), subdivs.eq(1).height()];

            //place the div in the upperleft corner of the window. This might avoid scrollbars to appear on the wiondow and then disappear
            var bounds = this.getBoundsOf(); //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
            div.css({
                'left': bounds.x + 'px',
                'top': bounds.y + 'px'
            });

            return size;
        };

        //Function called from _setBoundsAsPopup and _setBoundsInside to set some more css values at the END of the respective functions
        //Most of the problems here regard IE. 
        //Basically, sets the max height of the central div. The width is already been set and is "absolute", whereas the height
        //must take into account also T and B (top and bottom div) after max sizes are set
        p._postSizeFcn = function () {
            var div = this.getDiv();
            var subdivs = div.children();
            var topDiv = subdivs.eq(0);
            var centralDiv = subdivs.eq(1);
            var bottomDiv = subdivs.eq(2);

            //WRONG CODE:!!!
//        var maxHeight = (div.height() - topDiv.outerHeight(true) - bottomDiv.outerHeight(true) -
//                (centralDiv.outerHeight(true) - centralDiv.height()));
            //EXPLANATION:
            //the function above in Chrome calculates the outer height ALSO for elements which are HIDDEN!
            //See http://stackoverflow.com/questions/18135313/jquery-outerheight-return-none-zero-on-hidden-displaynone-element

            var maxHeight = (div.height()
                    - (topDiv.is(':visible') ? topDiv.outerHeight(true) : 0)
                    - (bottomDiv.is(':visible') ? bottomDiv.outerHeight(true) : 0)
                    - (centralDiv.outerHeight(true) - centralDiv.height()));

            //setting centralDiv maxHeight or height is actually the same, we use height to be sure...
            if (maxHeight > 0) {
                centralDiv.css('height', maxHeight + 'px');
            }

            var size = [centralDiv.width(), centralDiv.height()];

            return size;

        };

        p._getRectangle = function (x, y, w, h, bounds) {
            var ispo = $.isPlainObject(bounds);
            var insets = {top: 0, bottom: 0, right: 0, left: 0};
            if (ispo) {
                insets.top = bounds.top || 0;
                insets.bottom = bounds.bottom || 0;
                insets.right = bounds.right || 0;
                insets.left = bounds.left || 0;
            } else {
                if ($.isArray(bounds) && bounds.length) {
                    if (bounds.length === 1) {
                        var v = bounds[0];
                        insets.top = insets.bottom = insets.right = insets.left = bounds[0];
                    } else if (bounds.length === 2) {
                        var top_bottom = bounds[0];
                        var right_left = bounds[1];
                        insets.top = insets.bottom = top_bottom;
                        insets.left = insets.right = right_left;
                    } else if (bounds.length === 2) {
                        var top = bounds[0];
                        var right_left = bounds[1];
                        var bottom = bounds[2];
                        insets.top = top;
                        insets.bottom = bottom;
                        insets.right = insets.left = right_left;
                    } else {
                        insets.top = bounds[0];
                        insets.right = bounds[1];
                        insets.bottom = bounds[2];
                        insets.left = bounds[3];
                    }
                } else if (typeof (bounds) === 'number') {
                    insets.top = insets.right = insets.bottom = insets.left = bounds;
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
            insets.top = max(0, pInt(insets.top));

            if (insets.bottom > 0 && insets.bottom < 1) {
                insets.bottom = h * insets.bottom;
            }
            insets.bottom = max(0, pInt(insets.bottom));

            if (insets.left > 0 && insets.left < 1) {
                insets.left = w * insets.left;
            }
            insets.left = max(0, pInt(insets.left));

            if (insets.right > 0 && insets.right < 1) {
                insets.right = w * insets.right;
            }
            insets.right = max(0, pInt(insets.right));


            return {x: x + insets.left, y: y + insets.top, w: w - (insets.left + insets.right), h: h - (insets.top + insets.bottom)};
        };


        //Returns the bounds of the given argument (in jQueryElement form). If arg is missing it defaults to the window object
        p.getBoundsOf = function (jQueryElement) {
            var ret = {
                x: 0,
                y: 0,
                width: 0,
                height: 0
            };
            if (!jQueryElement || !(jQueryElement instanceof $)) {
                jQueryElement = wdw;
            }
            if (jQueryElement[0] === w_) {
                ret.x = jQueryElement.scrollLeft();
                ret.y = jQueryElement.scrollTop();
            } else {
                var offs = jQueryElement.offset();
                ret.x = offs.left;
                ret.y = offs.top;
            }
            ret.width = jQueryElement.width();
            ret.height = jQueryElement.height();
            return ret;
        };

        p.close = function () {
            if (this.__isClosing) {
                return this;
            }
            this.__isClosing = true;
            if (this._resizeTimeInterval !== undefined) {
                clearInterval(this._resizeTimeInterval);
                delete this._resizeTimeInterval;
            }
            this.setFocusCycleRoot(false);
            var div = this.getDiv();
            var me = this;

            var closeArgForListeners = this._closeOrigin || "";
            delete this._closeOrigin;

            var customHideFunc = undefined;
            var afterCloseCallback = function () {

                //restore event data on invoker, if any
                var id = '_tmpHandlers' + me.getId();
                if (me[id]) {
                    var oldHandlers = me[id];
                    delete me[id];
                    me.invoker.unbind('click');
                    for (var k = 0; k < oldHandlers.length; k++) {
                        var h = oldHandlers[k];
                        me.invoker.bind(h.type + (h.namespace ? "." + h.namespace : ""), h.handler);
                    }
                }

                delete me['__isClosing'];

                var removeCmd = me.removeOnClose;
                //delete me._defaultDomCloseCommand;
                if (removeCmd !== false) {
                    //div.remove();
                //} else if (removeCmd === 'detach') {
                //    div.detach();
                //} else {
                    div.remove();
                }

                me.trigger('close', closeArgForListeners);
                if (typeof (customHideFunc) === 'function') {
                    customHideFunc.apply(this);
                }

            };


            var arg = this._parseShowHideArg.apply(this, arguments);
            if (arg.complete) {
                customHideFunc = arg.complete;
            }
            arg.complete = afterCloseCallback;

            var _hide = this._do_hide; //defined in show
            delete this._do_hide;
            if (typeof _hide === 'function') {
                _hide.apply(this, [div, arg]);
            } else {
                div.hide(arg);
            }
            return this;
        };


        //parses the arguments to show and close to a valid dict usable for
        //jQuery.hide and jQuery.show
        p._parseShowHideArg = function () {
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

        //Returns the attribute name of each select, input or textarea for which the onOk callback builds up a dictionary
        p.getFormDataAttrName = function () {
            //return this.getId()+"_data";
            return "data-key"; //new in HTML5 to denote custom data. 
        };

        //Returns the attribute name of clickable elements which should invoke the onOk callback
        p.getOkInvokerAttrName = function () {
            //return this.getId()+"_data";
            return "data-ok-invoker"; //new in HTML5 to denote custom data. 
        };

        //Returns the attribute name of clickable elements which should invoke the close callback
        p.getCloseInvokerAttrName = function () {
            //return this.getId()+"_data";
            return "data-close-invoker"; //new in HTML5 to denote custom data. 
        };

    })(PopupDiv.prototype);

// End of closure.

})(jQuery);