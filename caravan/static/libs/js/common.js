/**
 * @author Riccardo Zaccarelli, PhD
 * @date Tue Jul 8 2014, 11:07 AM
 * 
 * Base file for all "common" JavaScript functions not necessarily related to this project. 
 * The aim of this file is to make common functions and declarations (those which are  are most likely neede by other projects) 
 * easily exportable  are most likely
 *
 */

/**
 * Returns a function f(value) which will convert a numeric value in [min(src1, src2), max(src1, src2)] into the 
 * corresponding linearly mapped value in [min(dst1, dst2), max(dst1, dst2)]. Example:
 * <pre>getLinearTransform(-1,0,1,2)</pre>
 * will convert 0 to 2
 * <p>Note that the user can also "invert" the direction, e.g.,
 * <pre>getLinearTransform(0,-1,1,2)</pre>
 * will convert 0 to 1
 * 
 * @param {number} src1 the source first bound
 * @param {number} src2 the source second bound
 * @param {number} dst1 the destination first bound, mapped to src1
 * @param {number} dst2 the destination second bound, mapped to src2
 * @returns {Function}
 */
function getLinearTransform(src1, src2, dst1, dst2) {
    //y = minC + (maxC - minC) * (x-min) / (max -min) 
    var dstDenom = dst2 - dst1 + 0.0; //parse to float, right?
    var srcDenom = src2 - src1 + 0.0; //parse to float, right?
    return function (value) {
        return dst1 + (dstDenom * (value - src1) / srcDenom);
    };
}

/**
 * Returns a function f(value) which will convert a numeric value in [min(src1, src2), max(src1, src2)] into the 
 * corresponding linearly/logarithmically/exponentially mapped value in [min(dst1, dst2), max(dst1, dst2)]. Example:
 * <pre>getTransform(-1,0,1,2)</pre>
 * will convert 0 to 2
 * <p>Note that the user can also "invert" the direction, e.g.,
 * <pre>getTransform(0,-1,1,2)</pre>
 * will convert 0 to 1
 * There is a fifth argument, which can be "log" or "exp" (case insensitive), and that, if given, will map 
 * the value logarithmically and exponentially, repspectively.
 * 
 * @param {number} src1 the source first bound
 * @param {number} src2 the source second bound
 * @param {number} dst1 the destination first bound, mapped to src1
 * @param {number} dst2 the destination second bound, mapped to src2
 * @param {string} callbackStr either "log" or "exp" for logarithmic or exponential map. Any other value 
 * (including missing argument) will default to a linear map
 * @returns {Function}
 */
function getTransform(src1, src2, dst1, dst2, callbackStr) {
    var callback = undefined;
    if (callbackStr) {
        callbackStr = callbackStr.toLowerCase();
        if (callbackStr === 'log') {
            //first build a logarithmic transformation from src1, src2 to 0 and 1,
            //and to do this we need a linear transformation from src1, src2 to 1 and 10, respectively, and then take the log
            //This normalizes each log variation within the same range 
            //and we avoid problems when negative or infinity
            var log = Math.log;
            var s1 = src1;
            var s2 = src2;
            var d1 = 1;
            var d2 = 10;
            src1 = log(d1);
            src2 = log(d2);
            var t = getLinearTransform(s1, s2, d1, d2);
            callback = function (val) {
                return log(t(val));
            };
        } else if (callbackStr === 'exp') {
            //first build an exponential transformation from src1, src2 to 1 and e (Math.E),
            //and to do this we need a linear transformation from src1, src2 to 0 and 1, respectively, and then take the exp
            //This normalizes each exp variation within the same range 
            //and we avoid problems when infinity
            var exp = Math.exp;
            var s1 = src1;
            var s2 = src2;
            var d1 = 0;
            var d2 = 1;
            src1 = exp(d1);
            src2 = exp(d2);
            var t = getLinearTransform(s1, s2, d1, d2);
            callback = function (val) {
                return exp(t(val));
            };
        }
    }

    //y = minC + (maxC - minC) * (x-min) / (max -min) 
    var dstDenom = dst2 - dst1 + 0.0; //parse to float, right?
    var srcDenom = src2 - src1 + 0.0; //parse to float, right?

    if (callback) {
        return function (value) {
            return dst1 + (dstDenom * (callback(value) - src1) / srcDenom);
        };
    }

    return function (value) {
        return dst1 + (dstDenom * (value - src1) / srcDenom);
    };
}

/**
 * Parses URL "get" data returning a dictionary with key: value pairs. 
 * Code copied and modified from http://stackoverflow.com/questions/814613/how-to-read-get-data-from-a-url-using-javascript.
 * <h4>Example</h4>:
 * <pre>parseURLQueryStr("http://www.foo.com/bar?a=a+a&b%20b=b&c=1&c=2&d#hash");</pre>
 * returns a an object like this:
 * <pre>{
 * "a"  : ["a a"],     \/* param values are always returned as arrays *\/
 * "b b": ["b"],       \/* param names can have special chars as well *\/
 * "c"  : ["1", "2"]   \/* an URL param can occur multiple times!     *\/
 * "d"  : [undefined]       \/* parameters without values are set to undefined if no second argument is given  *\/ 
 * }</pre> 
 *and
 *<pre>parseURLQueryStr("www.mints.com?name=something")</pre>
 *gives
 *
 *<pre>{name: ["something"]}</pre>
 * 
 * @param {type} url
 * @param {type} valueNotFound the value to be assigned to values not found, including the case where the query string is not present. 
 * Typically, it is omitted (it defaults to undefined) or set to null
 * @returns an Object with key value pairs denoting the url
 */
function parseURLQueryStr(url, valueNotFound) {
    var queryStart = url.indexOf("?");
    if (queryStart < 0) {
        return valueNotFound;
    }

    //if(arguments.length<2){ //for safety (it should be undefined already)
    //    valueNotFound = undefined;
    //}

    var queryEnd = url.indexOf("#") + 1 || url.length + 1,
            query = url.slice(queryStart + 1, queryEnd - 1),
            pairs = query.replace(/\+/g, " ").split("&"),
            i, n, v, nv;

    if (query === url || query === "") {
        return valueNotFound;
    }

    var parms = {};
    var decodeURIComp = decodeURIComponent; //instantiate func ref once (its access might be faster when used in loop below)

    for (i = 0; i < pairs.length; i++) {
        nv = pairs[i].split("=");
        n = decodeURIComp(nv[0]);
        v = decodeURIComp(nv[1]);

        if (!parms.hasOwnProperty(n)) {
            parms[n] = [];
        }

        parms[n].push(nv.length === 2 ? v : valueNotFound);
    }
    return parms;
}

/**
 * Loads an external js or css file appending it to the head. Does NOT require jQuery
 * @param {type} filename the file name
 * @param {type} optional_filetype the file type, supported types are "js" and "css" (case insensitive). If missing, the 
 * type is guessed from filename extension. If the latter matches either "js" or "css", then the file is appended to the body's head
 * @returns {Boolean} true if file was succesfully appended, false otherwise
 */
function loadFile(filename, optional_filetype) {
    if (optional_filetype === undefined) {
        var idx = filename.lastIndexOf('.');
        if (idx > -1 && idx < filename.length - 1) {
            optional_filetype = filename.substring(idx + 1, filename.length);
        }
    }

    if (optional_filetype === undefined) {
        return false;
    }
    var d = document;
    if (optional_filetype.toLowerCase() === "js") { //if filename is a external JavaScript file
        var fileref = d.createElement('script');
        fileref.setAttribute("type", "text/javascript");
        fileref.setAttribute("src", filename);
    } else if (optional_filetype.toLowerCase() === "css") { //if filename is an external CSS file
        var fileref = d.createElement("link");
        fileref.setAttribute("rel", "stylesheet");
        fileref.setAttribute("type", "text/css");
        fileref.setAttribute("href", filename);
    } else {
        return false;
    }

    d.getElementsByTagName("head")[0].appendChild(fileref);
    return true;
}

/**
 * Returns true if the browser supports svg, false otherwise. This method should be used with jQuery as it 
 * should be called once the document is ready ($(document).ready is not trivial without jQuery, see http://stackoverflow.com/questions/799981/document-ready-equivalent-without-jquery)
 * If one or more arguments are specified, jQuery MUST be INSTALLED, and for any argument A which is typeof functions A(supported) will be called once the document is ready, 
 * where supported is the value of the svg support (true or false)
 * @returns {Boolean} true if svg is supported. THIS METHOD SHOULD BE RUN ONCE THE DOCUMENT IS READY, or should be called with callcacks (functions) accepting
 * a boolean argument (true indicating svg support).
 */
function isSVGSupported() {
    var doc = document;
    var supported = function () {
        return doc.createElement('svg').getAttributeNS ? true : false;
    };
    if (arguments && arguments.length) {
        jQuery(doc).ready(function () {
            var supported_ = supported();
            for (var i = 0; i < arguments.length; i++) {
                if (typeof arguments[i] === 'function') {
                    arguments[i](supported_);
                }
            }
        });
    }
    return supported();
}
/**
 * Returns the font size in pixel for a length of 1em on a given element, using getComputedStyle
 * (see https://developer.mozilla.org/en/docs/Web/API/window.getComputedStyle)
 * The returned value is a float.
 * See http://stackoverflow.com/questions/4571813/why-is-this-javascript-function-so-slow-on-firefox
 * @param {type} element
 * @returns {unresolved}
 */
function getEmSize(element) {
    return parseFloat(getComputedStyle(element, "").fontSize.match(/(.*)px/)[1]);
}

/**
 * Adds one or two functions to the window object:
 *      copyHeadTo(iframe [, what])
 * which copies the head children into iframe (which must be an iframe, obviously, inside 
 * the current window and with same domain)
 * 
 * and, if this window is an iframe (it has a parent property)
 *      inheritHead([what])
 * which copies the head children from the parent window into this window
 * 
 * what defines which elements from the head source must be copied to the head destination:
 * if null, copy all, if string, copies elements whose tag name is equal (ignoring case) to the given string 
 * (e.g., "link"), if regexp, copies elements whose tag name matches (ignoring case) the given regexp, e.g. 
 * /link|style|meta/. Note that apparently scripts are not copied, see
 * http://stackoverflow.com/questions/4612374/iframe-inherit-from-parent
 * See also http://stackoverflow.com/questions/1490260/jquery-inserting-all-stylesheets-into-iframe
 * for a jQuery equivalent, which is much faster
 * 
 * NOTE that what applies only to &lt; head &gt; 's children, not their descendants. Once an 
 * &lt; head &gt; 's child has to be copied its cloneNode(true) method is called
 * @param {type} wdw
 * @returns {undefined}
 */

//see also (for closures) http://codereview.stackexchange.com/questions/12511/should-i-put-a-javascript-function-in-a-local-or-global-scope
(function (wdw) {
    //see http://stackoverflow.com/questions/15564029/adding-to-window-onload-event
    function addEvent(element, eventName, fn) {
        if (element.addEventListener) {
            element.addEventListener(eventName, fn, false);
        } else if (element.attachEvent) {
            element.attachEvent('on' + eventName, fn);
        }
    }

    function onload(wdw, callback) {
        //see http://www.stevesouders.com/blog/2014/09/12/onload-in-onload/
        if (wdw.document.readyState === "complete") {
            callback();
        } else {
            addEvent(wdw, 'load', callback);
        }
    }

    function copyHead(srcWindow, what, destWindow) {
        var dest = destWindow.document.getElementsByTagName("head")[0];
        var src = srcWindow.document.getElementsByTagName("head")[0];
        onload(destWindow, function () {
            var nodes = src.childNodes();
            if (!what) {
                for (var i = 0; i < nodes.length; i++) {
                    dest.appendChild(nodes[i].cloneNode(true));
                }
            } else if (typeof (what) === 'string') {
                what = what.toLowerCase();
                for (var i = 0; i < nodes.length; i++) {
                    var node = nodes[i];
                    if (!node.tagName) {
                        continue;
                    }
                    if (node.tagName.toLowerCase() === what) {
                        dest.appendChild(node.cloneNode(true));
                    }
                }
            } else if (what.test) {
                for (var i = 0; i < nodes.length; i++) {
                    var node = nodes[i];
                    if (!node.tagName) {
                        continue;
                    }
                    if (what.test(node.tagName) || what.test(node.tagName.toLowerCase())) {
                        dest.appendChild(node.cloneNode(true));
                    }
                }
            }
        });
    }
    if(wdw.parent){
        wdw.inheritHead = function (what) {
            copyHead(wdw, what, wdw.parent);
        };
    }
    wdw.copyHeadTo = function (dest, what) {
        if(dest.contentWindow){
            copyHead(wdw, what, dest.contentWindow);
        }
    };

})(window);