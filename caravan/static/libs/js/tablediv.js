/**
 * @author Riccardo Zaccarelli, PhD (<riccardo(at)gfz-potsdam.de>, <riccardo.zaccarelli(at)gmail.com>)
 * @date Wed Jul 16 2014, 10:16 AM
 * 
 * setting sort icons: user is responsible for width and height (note: percentages might be harmful!) 
 *
 */
function TableDiv() {
    var $ = jQuery;
    //var win = window;
    //var doc = document;

    /**
     * @returns {String} the id of the html table element
     */
    this.getId = function () {
        if (!this.__id) {
            this.__id = "divtable_" + (new Date().getTime());
        }
        return this.__id;
    };

    this.table = $("<table>").attr("id", this.getId()); //.css('white-space','normal');
    this.thead = $("<thead>");
    var tbody = $("<tbody>"); //.css("overflow", "auto");
    var colgroup = $("<colgroup>");
    this._r = 0;
    this._c = 0;

    /**
     * @returns {Number} the number of rows of this table, excluding the table header row
     */
    this.getRowCount = function () {
        return this._r;
    };
    /**
     * @returns {Number} the number of columns of this table
     */
    this.getColCount = function () {
        return this._c;
    };
    /**
     * Empty method which can be overridden in order to customize a newly added row. 
     * By default, this method does nothing
     * @param {type} $tr the table row in jQuery form
     * @param {type} index the row index
     * @returns {undefined} nothing by default
     */
    this.configureRow = function ($tr, index) {

    };

    /**
     * Function which can be overridden in order to return a custom string for the given cell. 
     * This method is called whenever a cell value is created or modified via this.setValue(row, col, value)
     * By default it returns str_value, which is a string representation of the given value.
     * 
     * @param {type} value the cell value (e.g., a number, a date, or an object)
     * @param {type} str_value the value string representation calculated inside this function. This is value returned by default
     * @param {type} row the cell row index. -1 means: thead cell
     * @param {type} column the column index
     * @param {type} column_type the column type (e.g., "string" , "number" etcetera)
     * @returns {string} str_value
     */
    this.getStrValue = function (value, str_value, row, column, column_type) {
        return str_value;
    };


    var sortable = true;
    /**
     * Returns (no args) or sets the sortable state of this table. If arguments are supplied, it must be a boolean indicating 
     * whether the table is sortable, so that clicks on the table header cells will sort each row acccording to the given clicked column
     * and the column data type. A tablediv is sortable dby default
     * @returns {true|false or this object}
     */
    this.sortable = function () {
        if (arguments && arguments.length && (arguments[0] === true || arguments[0] === false)) {
            if (sortable === arguments[0]) {
                return;
            }
            this.sortindex = -1;
            this.sortorder = false; //so that next toggle set it to false
            sortable = arguments[0];
            this._sortChanged();
            return this;
        } else if (!arguments || !arguments.length) {
            return sortable;
        }
    };

    var selectable = true;
    /**
     * Returns (no args) or sets whether this table is selectable by rows. Passing argument true makes each tr selectable by clicking on it
     * @returns {true|false or this object}
     */
    this.selectable = function () {
        if (arguments && arguments.length && (arguments[0] === true || arguments[0] === false)) {
            var rows = this._getRows();
            this._setSelectAction(rows, arguments[0]);
            selectable = arguments[0];
            return this;
        } else {
            return selectable;
        }
    };

    var synchWidths = 'auto'; /*true: synch cols. False: do not synch. 0..nCols-1 : synch cols AND stretch given col if any space remaining, 
     * -1: do the same but starting from 
     * the last one, 'auto': synch cols and partition remaining space among all cols whose header is bigger than the tbody cells width 
     */

    /**
     * Returns (no args) or sets whether this table will synchronize the width of each header column according to the table body (true by default),
     * or viceversa. If used to set width synchronization, the argument can be
     * <ul>
     * <li>true to indicate that thead cells widths must be synchronized (i.e., make equal) to the relative tbody column widths.
     * <li>false to disable width synchronization. Most likely, thead cells are not aligned with relative tbody columns, and 
     * the user has to manually set widths (The tablediv table implements colgroups. However, note that apparently colgroup cols width 
     * do not work properly, so there is a lot of work to do: scan cells of the tablediv table, check their widths, etcetera)
     * <li>'auto' behaves like true, but if tbody width is shorter than available table width (say there are N pixel available) 
     * N/M is added to the M columns whose cell header width is shortened after applying width synchronization
     * <li>An integer behaves like true, and moreover the column at the given integer index stretches to take all remaining space, if any, 
     * after applying width synchronization
     * </ul>
     * @returns {true|false or this object}
     */
    this.syncWidths = function () {
        if (arguments && arguments.length /*&& (arguments[0] === true || arguments[0] === false)*/) {
            var val = arguments[0];
            if (val === synchWidths) {
                return this;
            }
            synchWidths = val;
            if (val === false) {
                this._resetWidths();
            } else {
                this._syncWidths();
            }
            return this;
        } else {
            return synchWidths;
        }
    };

    /**
     * Sets the sort icons. The icons will be automatically displayed if this object is sortable when clicking on 
     * a table header cell
     * @param {String|JQuery object} ascending the sort icon indicating sort-order ascending. If string S, $(S) will be set as sort icon
     * @param {String|JQuery object} descending the sort icon indicating sort-order descending. If string S, $(S) will be set as sort icon
     * @returns this object
     */
    this.setSortIcons = function (ascending, descending) {
        if (typeof ascending === 'string') {
            ascending = $('<span>').css('display', 'inline-block').html(ascending);
        }
        if (typeof descending === 'string') {
            descending = $('<span>').css('display', 'inline-block').html(descending);
        }

        if (!(ascending instanceof $)) {
            ascending = $('<span>');
        }
        if (!(descending instanceof $)) {
            descending = $('<span>');
        }
//		if(this._sortAscendingElement && this._sortAscendingElement.length){
//			this._sortAscendingElement.remove();
//		}
//		if(this._sortDescendingElement && this._sortDescendingElement.length){
//			this._sortDescendingElement.remove();
//		}

        this._sortAscendingElement = ascending;
        this._sortDescendingElement = descending;

        //update sortIconWidth:
        var getW = function (elm) {
            if (!elm && !elm.length) {
                return 0;
            }
            var parent = elm.parent();
            if (parent && parent.length) {
                return elm.outerWidth(true);
            }
            $(d_.body).append(elm);
            var ret = elm.outerWidth(true);
            elm.remove();
            return ret;
        };

        var w1 = getW(this._sortAscendingElement);
        var w2 = getW(this._sortDescendingElement);
        //this._sortIconWidth = w1>w2 ? w1 : w2;

        ascending.attr('data-sort-icon', 'ascending').removeAttr('data-is-width-ref');
        descending.attr('data-sort-icon', 'descending').removeAttr('data-is-width-ref');

        if (w1 < w2) {
            descending.attr('data-is-width-ref', true);
        } else {
            ascending.attr('data-is-width-ref', true);
        }

        this._sortChanged();
        return this;
    };



    var me = this;
    var d_ = document;
    $(d_).ready(function () {
        if (!me._sortAscendingElement) {
            var supported = d_.createElement('svg').getAttributeNS ? true : false; //check svg suooprt
            me._sortAscendingElement = supported ? me._defaultSortAscendingSVG() : me._defaultSortAscendingText();
            me._sortDescendingElement = supported ? me._defaultSortDescendingSVG() : me._defaultSortDescendingText();
            me.setSortIcons(me._sortAscendingElement, me._sortDescendingElement);
        }
    });

    //this.setSortIcons(this._sortAscendingElement, this._sortDescendingElement); //to update icons

    this.table.append(colgroup).append(this.thead).append(tbody).append($('<tfoot>'));
    //this.table.append($("<tbody>").css("overflow", "auto"));

    //divheader.append(tableheader);
    //divbody.append(tablebody);
    this.table.add(this.thead).add(tbody).css('display', 'block');
    tbody.css({"overflow": "auto"/*, "max-height": '58px'*/}); //two NECESSARY CONDITIONS to show VERTICAL SCROLLBAR (also max-height instead of height might be fine)

    //this.table.css({'overflow-x': 'auto'/*, 'width': '100%'*/}); //two NECESSARY CONDITIONS to show the HORIZONTAL SCROLLBAR


    this.getTable = function () {
        return table;
    };

}

(function (p) {
    var $ = jQuery;
    //var w_ = window;
    //var d_ = document;
    //var wdw = $(w_);
    var pFloat = parseFloat;
    var pInt = parseInt;
    //var mathmin = Math.min;

//    p.alignCells = function(){
//        var oldVal = this._alignCells ? this._alignCells : false;
//        if(arguments && arguments.length){
//            var val = arguments[0] ? true : false;
//            if(val === oldVal){
//                return;
//            }
//            var cols = [];
//            for(var i=0; i<this._c; i++){
//                if(this._getColType(i) === 'number'){
//                    cols.push(i);
//                }
//            }
//            var rows = this._getRows();
//            for(var i=0; i<this._c; i++){
//                
//            }
//        }
//        return oldVal;
//    };


    p._setSelectAction = function ($tr, value) {
        $tr.unbind('click').css('cursor', '');
        if (!value) {
            return;
        }
        var me = this;
        $tr.css('cursor', 'default').click(function () {
            var trs = me.table.children('tbody').find('tr.selected').add($(this));
            trs.toggleClass("selected");
        });
    };

    p._sortChanged = function ($optional_td_header_cell) {
        var sortindex = this.sortindex;
        var sortorder = this.sortorder; //so that next toggle set it to false
        var sortable = this.sortable;
        var header_tds = $optional_td_header_cell ? $optional_td_header_cell : this.__getCells(this._getRow(-1));
        //var shouldDisplay = sortable ? "inline-block" : "none";
        //var icnW = this._sortIconWidth;
        var me = this;
        //this._removeSortIcons();

        var _setSortAction = function ($td, value) {
//        $td.unbind('click').css('cursor', '');
//        if (!value) {
//            return;
//        }
//        var me = this;
//        $td.css('cursor', 'default').click(function() {
//            var oldc = me.sortindex;
//            var c = me.__getCells(me._getRow(-1)).index(this);
//            me._toggleSort(c);
//        });
            var $a = $td.children('a');
            //$a.unbind(9)'click'
            $a.unbind('click').removeAttr('href');
            if (!value) {
                //$a.click(function(){return false;});
                return;
            }
            //var me = this;
            $a.attr('href', '#').click(function () {
                var c = me.__getCells(me._getRow(-1)).index(this.parentNode);
                me._toggleSort(c);
                return false;
            });
        };

        var _getSortElements = function (index) {
            var $ret = me._sortAscendingElement.clone().add(me._sortDescendingElement.clone());
            return me._updateSortElements(index, $ret); //defined few lines below (scroll down...)
        };

        header_tds.each(function (i, elm) {
            var $elm = $(elm);
            _setSortAction($elm, sortable);
            $elm.find("[data-sort-icon]").remove();
            //var child = $elm.children().eq(1);
            //child.remove();
            var newchild = _getSortElements(i);
            $elm.children('a').append(newchild); //append to the first children (an anchor)
            //FIXME: UPDATE WIDTHS
        });
    };

    p._toggleSort = function (colindex  /*=boolean*/) {
        if (!this.sortable()) {
            return;
        }
        if (this.sortorder === undefined) {
            this.sortorder = false;
        }
        //this.sortorder = !this.sortorder; //workaround to make sort work (see below)
        this._sort(colindex, !this.sortorder);
    };

    /**
     * Sorts the table acccording to the data type of the ccolumn at the given colindex. If the table is already sorted according to the 
     * argument, does nothing
     * @param {number} colindex
     * @param {boolean} ascending
     * @returns this objecct
     */
    p.sort = function (colindex, ascending /*=boolean*/) {
        if (!sortable() || (colindex === this.sortindex && ascending === this.sortorder)) {
            return this;
        }
        this._sort(colindex, ascending);
        return this;
    };

    p._sort = function (colindex, ascending /*=boolean*/) {
//        if (!sortable() || (colindex === this.sortindex && ascending === this.sortorder)) {
//            return;
//        }
        var rows = this._getRows();
        var type = this._getColType(colindex);
        var baseCompareFunc = (type === "number") ? this.__rownumcmp : (type === "date") ? this.__rowdatecmp : this.__rowstrcmp;
        //var getValueCallback = this._getValueHTML;

        var me = this;
        var getVal = this.__getValue;
        var compareFunc;

        //writing here bellow the form "ascending ? func1 : func2" 
        //messes up the editor colors in netbeans
        //so we write a "normal" and more verbose if statement...
        if (ascending) {
            compareFunc = function (a, b) {
                var val1 = getVal(me._getCell($(a), colindex));
                var val2 = getVal(me._getCell($(b), colindex));
                return baseCompareFunc(val1, val2);
                //return func.apply(this, a,b,getValueCallback,ascending);
            };
        } else {
            compareFunc = function (a, b) {
                var val1 = getVal(me._getCell($(a), colindex));
                var val2 = getVal(me._getCell($(b), colindex));
                return -baseCompareFunc(val1, val2);
                //return func.apply(this, a,b,getValueCallback,ascending);
            };
        }

        rows.sort(compareFunc);
        rows.detach();
        this.table.append(rows);

        var oldsortindex = this.sortindex;
        this.sortindex = colindex;
        this.sortorder = ascending;

        var headerrow = this._getRow(-1);

        var $ret = this._getCell(headerrow, colindex).find('[data-sort-icon]');
        this._updateSortElements(colindex, $ret);

        if (oldsortindex !== this.sortindex) {
            $ret = this._getCell(headerrow, oldsortindex).find('[data-sort-icon]');
            this._updateSortElements(oldsortindex, $ret);
        }

    };
    
    p._updateSortElements = function (index, $sortElements) {
        var table_is_sortable = this.sortable();
        //var $ret = this._sortAscendingElement.clone().add(this._sortDescendingElement.clone());
        $sortElements.css({'display': 'none', 'visibility': ''});
        var display = 'inline-block'; //'block'
        if (table_is_sortable) {
            if (index === this.sortindex) {
                var idx = this.sortorder ? 0 : 1;
                var sortElm = $sortElements.eq(idx);
//                var diff = sortElm.outerHeight(true)-sortElm.height();
//                var h = $sortElements.eq(idx).parent().height() - diff;
                sortElm.css('display', display)/*.css('height',h)*/;
            } else {
                var elm = $sortElements.eq(0).is('[data-is-width-ref]') ? $sortElements.eq(0) : $sortElements.eq(1);
                elm.css({'display': display, 'visibility': 'hidden'});
            }
        }
        return $sortElements;
    };

    
    p.__rowstrcmp = function (val1, val2) {
        return val1.localeCompare(val2) || -1;
    };
    p.__rownumcmp = function (val1, val2) {
        return (pFloat(val1) - pFloat(val2)) || -1;
    };
    p.__rowdatecmp = function (val1, val2) {
        return (pInt(val1) - pInt(val2)) || -1;
    };

    /**
     * Returns the &lt;tr&gt; jQuery element which is selected, if this table is selectable, or an empty jQuery element otherwise
     * @returns {tablediv_L171.p@call;_getRows@call;find}
     */
    p._getSelectedRow = function () {
        return this.table.children('tbody').find("tr.selected");
    };

    /**
     * Return the DATA selected. A Data object is retrieved taking each selected row T (a jQuery tr element) and converting it to:
     * <ul><li>Array, if the argument is false. The array element at the sepcified index will be the value of the relative column
     * <li>Object, if the argument is true. The object key k will denote the the selected row value under the column with value k
     * </ul>
     * @param {type} asDict if true, the returned value is an array of objects, each object denoting a selected row. Otherwise, it is an array of arrays (each array 
     * denoting a selected row)
     * @returns {Array} an Array of Arrays or Objects indicating the selected rows
     */
    p.getSelectedData = function (asDict) {
        var tr = this._getSelectedRow();
        var getVal = this.__getValue;
        var getCells = this.__getCells;
        if (!asDict) {
            var ret = [];
            tr.each(function (i, elm) {
                var $tr = $(elm);
                var tds = getCells($tr);
                var arr = [];
                tds.each(function (j, elm) {
                    arr.push(getVal($(elm)));
                });
                ret.push(arr);
            });
            return ret;
        }

        var headercells = getCells(this._getRow(-1));
        var keys = [];
        headercells.each(function (i, elm) {
            keys.push(getVal($(elm)));
        });
        //var me = this;
        var ret = [];
        tr.each(function (i, elm) {
            var $tr = $(elm);
            var tds = getCells($tr);
            var arr = {};
            tds.each(function (j, elm) {
                var kkk = keys[j];
                arr[kkk] = getVal($(elm));
            });
            ret.push(arr);
        });
        return ret;
    };

    /**
     * Appends the table to the specified div
     * @param {jQuery div element} div
     * @param {boolean} calculateHeight if true, the tbody height is adjusted to match the div height each time synchWidths is called, 
     * Note that the parent div must have an height set. 
     * Overflows of the tbody will display a vertical scrollbar
     * @returns {tablediv_L148.p}
     */
    p.appendTo = function (div, calculateHeight) {
        if (this.table.parent().length) {
            this.table.remove();
        }
        this.table.appendTo(div);
        this.__autoCalcHeight = calculateHeight ? true : false; //used in synchWidths
        if (calculateHeight) {
            if (this._c < 1) {
                this._needsCalcHeight = true; //means: delegate calcHeight the next time synchWidths is called. But jsut ONCE (the property will be removed)
            } else {
                this._calcHeight(); //calculate height now
            }
        }
        return this;
    };

    p._calcHeight = function () {
        var div = this.table.parent();
        var h0 = this.table.outerHeight(true);
        var h1 = this.table.children('thead').outerHeight(true);
        var h2 = this.table.children('tfoot').outerHeight(true);
        var tbody = this.table.children('tbody');
        var h3 = tbody.outerHeight(true);
        var realh = div.height() - h1 - h2 - (h3 - tbody.height()) - (h0 - this.table.height());
        //tbody.height(realh);
        if (realh < 0) {
            realh = '';
        }
        tbody.css('max-height', realh);
    };

    /**
     * Adds a column to the table, with given name, optional type ('number', 'string' or 'date') at the given optiona index. If the latter is missing, 
     * the new column is appended at the end of the already existing table columns, otherwise it is inserted at the specified index (out of bound indices will return
     * without doing nothing)
     * @param {string} name
     * @param {string} optional_type
     * @param {number} optional_index
     * @returns this object
     */
    p.addCol = function (name, optional_type, optional_index) {
        if (optional_index !== undefined && (optional_index < 0 || optional_index > this._c)) {
            return this;
        }
        var index = optional_index === undefined ? this._c : optional_index;
        var colgroup = this.table.children('colgroup');
        var col_of_colgroup = $('<col>'); //NOTE: col does NOT work for setting width, keep it but set the width in _updateCols
        var me = this;
        var rows = this._getRows();
        var tr = this._getRow(-1);

        var _type = this._getType(name, optional_type);
        var td = this._createCell(name, -1, index, _type);

        //var td = this._createCell(name, index, optional_type);

        tr.append(td);

        if (index === this._c) {
            tr.append(td);
            colgroup.append(col_of_colgroup);
            //add one cell to each row:
            if (rows.length > 0) {
                rows.each(function (i, elm) {
                    //var rowtd = me._createCell("");
                    var rowtd = me._createCell("", i, index, _type);

                    $(elm).append(rowtd);
                });
            }
        } else {
            td.insertBefore(this.__getCells(tr).eq(index));
            colgroup.children('col').eq(index).insertBefore(col_of_colgroup);
            //add one cell to each row:
            if (rows.length > 0) {
                rows.each(function (i, elm) {
                    //var rowtd = me._createCell("");
                    var rowtd = me._createCell("", i, index, _type);
                    rowtd.insertBefore(me.__getCells($(elm)).eq(index));
                });
            }
        }
        //add sort events:

        this._c++;
        if (this._r > 0) {
            this._syncWidths(); //which calls
        }
        if (this._needsCalcHeight && this._r > 0) {
            delete this._needsCalcHeight;
            //the above is a flag saying that we appended the table to a div requiring auto calc height of the tbody, when the table was empty
            //Therefore, we calculate height now that the table is not anymore empty
            //We do it only once by removing the _needsCalcHeight above

            //if this.synchWidths, we already called _calcHeight in _syncWidths above
            if (!this.syncWidths()) {
                this._calcHeight();
            }
        }

        return this;
    };

    /**
     * Removes one or more columns, argument can be one or more numbers denoting the indices of the columns to remove (first index 0).
     * Out of bound indices do nothing. The arguments need not to  be sorted (they will inside this method)
     *  @returns this object
     */
    p.rmCol = function () {

        if (!arguments || !arguments.length) {
            return this;
        }
        var cols_in_colgroup = this.table.children('colgroup').children('col');
        //the arguments behavelike an array but does not seem to have all arrays methods, including sort. The
        //workaround is explained here http://stackoverflow.com/questions/960866/converting-the-arguments-object-to-an-array-in-javascript
        //and implemented below (modification added by me: if arguments has a single element, just build a new array)
        var val = arguments.length === 1 ? [arguments[0]] : Array.prototype.slice.call(arguments, 0).sort();
        //var tds = p._getHeaderTr();
        var rows = this._getRows().add(this._getRow(-1)); //add header
        var c = this._c;
        var deleted = 0;
        var me = this;

        for (var i = val.length - 1; i >= 0; i--) {
            var idx = val[i];
            if (idx < 0 || idx >= c) {
                continue;
            }
            deleted++;
            cols_in_colgroup.eq(idx).remove();
            rows.each(function (i, evt) {
                me._getCell($(evt), idx).remove();
            });
        }

        this._c -= deleted;
        return this;
    };


    /**
     * Sets the data of the table preserving the table header. If columns are zero, does nothing. Arguments can be:
     * <ul>
     * <li>setData(array_or_object1,...,array_or_objectN): appends the arguments as rows to the table. For each array_or_objecti, if it is an array
     * it is supposed to hold the cell elements from 0 to cols (the table number of columns), if it is an object it is a dictionary of key:value pairs where
     * the key are the values of each column header as set in addCol(name). Any row which has more than col elements will be cut, and any row which has less col 
     * elements will be padded with empty cells ("")
     * </ul>
     * Note that if you have an array of objects or elements arg=[a1,...an], you can call table.setData.apply(table,arg) 
     *  @returns this object
     */
    p.setData = function () {
        this.clear();
        if (arguments && arguments.length) {
            this.addRow.apply(this, arguments);
        }
        return this;
    };

    /**
     * Clears the table, if the argument is true clears also the table header
     * @param {boolean} clearTHeaderToo self-explanatory
     *  @returns this object
     */
    p.clear = function (clearTHeaderToo) {
        var rows = this._getRows();
        if (clearTHeaderToo) {
            rows = rows.add(this._getRow(-1));
            this._c = 0;
        }
        rows.remove();
        this._r = 0;
        return this;
    };

    /**
     * Adds a row. If columns are zero, does nothing. Arguments can be:
     * <ul>
     * <li>addRow(): appends an empty row at the end of the rows
     * <li>addRow(number): adds an empty row at the specified index number
     * <li>addRow(number1, number2): adds number2 empty rows at the specified index number
     * <li>addRow(array_or_object1,...,array_or_objectN): appends the arguments as rows to the table. For each array_or_objecti, if it is an array
     * it is supposed to hold the cell elements from 0 to cols (the table number of columns), if it is an object it is a dictionary of key:value pairs where
     * the key are the values of each column header as set in addCol(name). Any row which has more than col elements will be cut, and any row which has less col 
     * elements will be padded with empty cells ("")
     * <li>addRow(number, array_or_object1,...,array_or_objectN): same as above, but it adds all rows at  index number
     * </ul>
     * Note that if you have an array of objects or elements arg=[a1,...an], you can call table.addRow.apply(table,arg) 
     *  @returns this object
     */
    p.addRow = function () {
        var args = [];
        var cols = this._c;
        var rows = this._r;
        var index = rows;
        if (cols < 1) {
            return this;
        }
        var keys2indices = null;
        if (!arguments || !arguments.length) {
            var data = [];//apparently, there are not big differences in preallocating array length.
            //see http://stackoverflow.com/questions/1246408/use-of-javascript-array-new-arrayn-declaration
            //and links there
            for (var i = 0; i < cols; i++) {
                data.push("");
            }
            args.push(data);
        } else if (arguments.length === 1 && (typeof arguments[0] === 'number')) {
            index = pInt(arguments[0]);
        } else if (arguments.length === 2 && (typeof arguments[0] === 'number') && (typeof arguments[1] === 'number')) {
            index = pInt(arguments[0]);
            var count = pInt(arguments[1]);
            for (var u = 0; u < count; u++) {
                var data = [];
                for (var i = 0; i < cols; i++) {
                    data.push("");
                }
                args.push(data);
            }
        } else {
            var startIndex = 0;
            if (typeof arguments[0] === 'number') {
                index = pInt(arguments[0]);
                startIndex++;
            }
            for (var i = startIndex; i < arguments.length; i++) {
                if (arguments[i] instanceof Array) {
                    args.push(arguments[i]);
                } else if ((typeof arguments[i] === 'object') && arguments[i]) { //null is also an object, that's why the second check
                    //build the map keys->indices if not already done:
                    if (!keys2indices) {
                        keys2indices = {};
                        var me = this;
                        this.__getCells(this._getRow(-1)).each(function (i, elm) {
                            keys2indices[me.__getValue($(elm))] = i;
                        });
                    }
                    var arr = [];
                    for (var k = 0; k < cols; k++) {
                        arr.push("");
                    }
                    for (var k in arguments[i]) {
                        if (arguments[i].hasOwnProperty(k)) {
                            var index_ = keys2indices[k];
                            if (typeof index_ === 'number' && index_ >= 0 && index_ < cols) {
                                arr[index_] = arguments[i][k];
                            }
                        }
                    }
                    args.push(arr);
                }
            }
        }
        if (args.length) {
            var me = this;
            var selectable = this.selectable();
            var cTypes = [];//apparently, there are not big differences in preallocating array length.
            //see http://stackoverflow.com/questions/1246408/use-of-javascript-array-new-arrayn-declaration
            //and links there
            for (var i = 0; i < this._c; i++) {
                cTypes.push(this._getColType(i));
            }
            var makeRow = function (row, rowIndex) {
                var tr = $("<tr>");
                var val;
                //var row = args[i];
                var tds = row.length < cols ? row.length : cols; //avoid using math min
                for (var i = 0; i < tds; i++) {
                    val = row[i];
                    //tr.append(me._createCell(val));
                    tr.append(me._createCell(val, rowIndex, i, cTypes[i]));
                }

                for (var i = tds; i < cols; i++) {
                    //tr.append(me._createCell(""));
                    tr.append(me._createCell("", rowIndex, i, cTypes[i]));
                }
                me._setSelectAction(tr, selectable);

                me._r++;
                return tr;
            };

            var configRow = this.configureRow;
            var currentIndex;
            if (index === rows) { //append
                for (var i = 0; i < args.length; i++) {
                    currentIndex = this._r;
                    var tr = makeRow(args[i], currentIndex);
                    this.table.append(tr);
                    configRow.apply(this, [tr, currentIndex]);
                }
            } else { //insert
                var trref = this._getRow(index);
                var currentIndex = index;
                for (var i = 0; i < args.length; i++) {
                    var tr = makeRow(args[i], currentIndex);
                    tr.insertBefore(trref);
                    configRow.apply(this, [tr, currentIndex]);
                    currentIndex++;
                }
            }
            this._syncWidths();
            if (this.sortable() && this.sortindex >= 0 && this.sortorder !== undefined) {
                //do a sort at the end. Maybe it might be faster to sort during insertion but we cannot assess it
                //too many drawbacks implementing it
                this._sort(this.sortindex, this.sortorder); //does nothing if this is 
            }
        }

        if (this._needsCalcHeight /*&& this._c>0*/) {
            delete this._needsCalcHeight;
            this._calcHeight();
        }

        return this;
    };
    /**
     * Removes one or more rows, argument can be one or more numbers denoting the indices of the rows to remove (first index 0).
     * Out of bound indices do nothing
     *  @returns this object
     */
    p.rmRow = function () {

        if (!arguments || !arguments.length) {
            return this;
        }
        //the arguments behavelike an array but does not seem to have all arrays methods, including sort. The
        //workaround is explained here http://stackoverflow.com/questions/960866/converting-the-arguments-object-to-an-array-in-javascript
        //and implemented below (modification added by me: if arguments has a single element, just build a new array)
        var val = arguments.length === 1 ? [arguments[0]] : Array.prototype.slice.call(arguments, 0).sort();
        //var tds = p._getHeaderTr();
        var rows = this._getRows();
        var r = this._r;
        var deleted = 0;
        for (var i = val.length - 1; i >= 0; i--) {
            var idx = val[i];
            if (idx < 0 || idx >= r) {
                continue;
            }
            deleted++;
            rows.eq(idx).remove();
            //rows.splice(idx,1); //no need to splice the array, as we are reversing the loop
        }

        this._r -= deleted;
        this._syncWidths();
        return this;
    };

    //synchronize widths between table and thead, setting the latter cells the same width of the 
    //tbody cells. 
    p._syncWidths = function () {

        //this.table.children('tbody').append(this._getRow(-1).clone());
        var syncWidths = this.syncWidths();

        //if we don't have a auto synch width, return
        if (!syncWidths || (this._r <= 0 && this._c <= 0) || !this.table.parent().length) {
            return;
        }
        //when resizing the thead tr, we change the display properties of thead
        //and trs. This makes tr higher sometimes while adjusting the widths, i.e., 
        //the whole table height might increase. If the parent is in overflow auto,
        //then it displays a vertical scrollbar which takes room. When calling _resize at the end
        //we readjust the tbody height, thus the table height readjusts to its viewport, making 
        //the parent scrollbar disappear, making the tbody cells readjust their WIDTH, making all
        //our efforts unvain. We add also the table for safety. Therefore:
        var tblAndParent = this.table.add(this.table.parent());
        tblAndParent.css('overflow', 'hidden');
        //we will reset it at the end
        var $rowHead = this._getRow(-1);
        var $cellsHead = this.__getCells($rowHead);
        this._resetWidths($rowHead, $cellsHead);
        if (this._r < 1) {
            return;
        }

        var tbody = this.table.children('tbody');

        //FIRST RESIZE THE TBODY TDs IF SYNCHWIDTHS IS "SPECIAL":
        if ((typeof syncWidths === 'number') || syncWidths === 'auto') {
            var trs_ = tbody.children('tr');
            //var remainingSpace = 0;
            var trWidth = trs_.eq(0).outerWidth(true);
            var tbodyWidth = trWidth; //so that by default no resize of tbody cells
            var doCheckAtEnd = true; //see notes below
            if (this.__real_tr_width__) { //what is this? it is a remonder of the 
                //ACTUAL maximum tr width, which might be lower of the tBodyWidth
                //in presence of scrollbars. To detect if scrollbars are present,
                //we run first this function, then at the end if the actual tr width
                //is LOWER than trWidth, it is most likely due to the scrollbars
                //(trWidth does not account for them). In this case, we set
                //this.__real_tr_width__ and we re-run this function
                tbodyWidth = this.__real_tr_width__;
                delete this.__real_tr_width__;
                doCheckAtEnd = false;
            } else {
                tbodyWidth = tbody.width(); //tbody.parent().width();
            }
            var remainingSpace = tbodyWidth - trWidth;
            if (remainingSpace <= 0) {
                doCheckAtEnd = false;
            } else {
                var $cellsBody = tbody.children('tr[custom_width]').children('td');
                if (!$cellsBody.length) {
                    //theoretically, we should always enter here as we called _resetWidths
                    //above. We leave this "if" for safety in order to avoid multiple
                    //tbody cells with custom width
                    $cellsBody = trs_.eq(0).attr('custom_width', 'true').children('td');
                }
                var widths_to_add = [];
                var elements_to_resize;
                if (syncWidths === 'auto') {
                    $cellsHead.each(function (i, elm) {
                        if ($(elm).outerWidth(true) > $cellsBody.eq(i).outerWidth(true)) {
                            if (!elements_to_resize) {
                                elements_to_resize = $cellsBody.eq(i);
                            } else {
                                elements_to_resize = elements_to_resize.add($cellsBody.eq(i));
                            }
                        }
                    });
                    var module = remainingSpace % elements_to_resize.length;
                    var diff = (remainingSpace - module) / elements_to_resize.length;
                    elements_to_resize.each(function (i, elm) {
                        var add = 0;
                        if (module > 0) {
                            add = 1;
                            module--;
                        }
                        widths_to_add.push(diff + add);
                    });
                } else {
                    widths_to_add.push(remainingSpace);
                    elements_to_resize = $cellsBody.eq(syncWidths);
                }
                var len = widths_to_add.length;
                elements_to_resize.each(function (i, elm) {
                    var $elm = $(elm);
                    $elm.css('width', $elm.width() + (len === 1 ? widths_to_add[0] : widths_to_add[i]));
                });
            }
        }

        //NOW RESIZE THEAD CELLS:
        //first set white space nowrap so that header cells do not use newlines
        //NOTE: we do not set display" inline-block,  WHICH IS ABSOLUTELY NECESSARY, because we'll set it later in function setW
        $cellsHead.css('white-space', 'nowrap');
        
        //this makes cells taking their size, otherwise tr has custom algorithms to
        //resize cells in order not to overflow
        $rowHead.css({'display': 'block', 'overflow': 'hidden'});

        var setW = function ($master_td, $slave_td) {
            var w_master = $master_td.outerWidth(true);
            //var w_slave = $slave.outerWidth(true);

            var $slave_span = $slave_td.children('a').eq(0).children('span').eq(0);
//            var disp = $slave_td.css('display');
            $slave_td.css('display', 'inline-block');
            $slave_span.css({'overflow': 'hidden', 'display': 'inline-block', 'text-overflow': 'ellipsis', 'width': ''});

            var set_w = function ($elm, outer_width) {
                var dif_ = $elm.outerWidth(true) - $elm.width();
                $elm.width(outer_width - dif_);
            };

            var oldw = $slave_td.width();
            set_w($slave_td, w_master);

            var diff = $slave_td.width() - oldw;
            $slave_span.width($slave_span.width() + diff);
            $slave_td.css('display', ''); //restore old display? no set it as default (empty string)
        };

        if ($cellsBody === undefined) { //might have already been defined if we entered the if above
            var $cellsBody = tbody.children('tr').eq(0).children('td');
        }

        $cellsBody.each(function (i, elm) {
            setW($(elm), $cellsHead.eq(i));
        });

        //this restores the tr to its original display:table-row.
        //cell sizes are set so apparently this simple call aligns all cells on a single row (if it wasn't)
        $rowHead.css({'display': ''});

        //after all this mess, tr might have changed its height, probably due to the overflow and display settings.
        //If we called appendTo with a second argument true, resize also the body
        //autocalcHeight is also set in refreshSize
        if (this.__autoCalcHeight) {
            this._calcHeight();
        }
        //Restore overflow. See notes above
        tblAndParent.css('overflow', '');

        if (doCheckAtEnd) {
            //Are scrollbars present? In case, we need to re-run this function 
            //telling the REAL trWidth, which we store in the temp variable
            //__real_tr_width__. Note that the presence of scrollbars implies we stretched the tbody 
            //tr of a width bigger than the actual tbody width, so some cells might have their space
            //rearranged (tr width is automatically managed by the browser), not as we expect
            trWidth = trs_.eq(0).outerWidth(true);
            //ww2 = tbody.parent().width();
            remainingSpace = tbodyWidth - trWidth;
            if (remainingSpace > 0) {
                this.__real_tr_width__ = trWidth;
                this._syncWidths(); //redo calculations
            }
        }
    };
    
    
    /**
     * Reset the widths of each table header cell to their natural width
     * arguments either empty or two jquery element indicating a tr and its children td
     * @returns {undefined}
     */
    p._resetWidths = function () {
        //this is a tr in the tbody which we marked with a special attribute
        //if synchWidths is 'auto'. Restore its attribute and their tds widths
        var $cellsBody = this.table.children('tbody').children('tr[custom_width]');
        if ($cellsBody.length) {
            var tdz = $cellsBody.children('td');
            tdz.css('width', '');//reset widths to their natural size
            $cellsBody.removeAttr('custom_width');
        }

        var $cells;
        var $rowHead;
        if (arguments && arguments.length) {
            $rowHead = arguments[0];
            $cells = arguments[1];
        } else {
            $rowHead = this._getRow(-1);
            $cells = this.__getCells($rowHead);
        }

        $rowHead.css({'display': '', 'overflow': ''});
        $cells.css({'display': '', 'overflow': '', 'white-space': '', width: ''});

        $cells.each(function (i, elm) {
            $(elm).children('a').eq(0).children('span').eq(0).css({'overflow': '', 'display': '', 'text-overflow': '', 'width': ''});
        });

    };

    /**
     * Returns the value (in string format) for the corresponding cell (including the table header if rowIndex =-1). 
     * The returned value is the string given as input in the corresponding element of addRow. 
     * If the type of column cType at the given colIndex is "date", the value of the date (in millisecond) is returned. Therefore, to cast the returned 
     * value to the given type, use parseFloat or parseInt for columns of type "numbers", and new Date() for columns of type "date"
     * @param {number} rowIndex the row index. -1 means the table header row
     * @param {number} colIndex
     * @returns {string} the value at the given cell
     */
    p.getValue = function (rowIndex, colIndex) {
        if (rowIndex < -1 || rowIndex > this._r || colIndex < 0 || colIndex > this._c) {
            return undefined;
        }
        return this.__getValue(this._getCell(this._getRow(rowIndex), colIndex));
    };

    /**
     * Sets the value for the corresponding cell at row rowIndex and column colIndex (including the table header cell if rowIndex =-1). 
     * @param {number} rowIndex the row index. -1 means the table header row
     * @param {number} colIndex
     * @param {object} value the value
     * @returns {object} this object
     */
    p.setValue = function (rowIndex, colIndex, value) {
        if (rowIndex < -1 || rowIndex > this._r || colIndex < 0 || colIndex > this._c) {
            return this;
        }
        var $td = this._getCell(this._getRow(rowIndex), colIndex);
        this._setValue($td, value, rowIndex < 0);
        return this;
    };
    /**
     * Creates a new cell. If only first argument is specified, the cell is a table body cell. Otherwise
     * optional_col_index must be a non-negative number and optional_type is the type of column data (if missing it 
     * will be retrieved from the type of value)
     * @param {type} value the value. It will affect the string representation of the cell
     * @param {type} row the row index. -1 indicates the table header cell
     * @param {type} column the column index
     * @param {string} column_type the column type, either "number" "string" or "date"
     * @returns {tablediv_L182.p@call;_setValue}
     */
    p._createCell = function (value, row, column, column_type) {
        var $td = $("<td>");
        if (row < 0) {  //column header. Note the display inline-block so that it behaves "normally", otherwise
            //the width is not properly set
            var $a = $('<a>')/*.css('display', 'inline-block')*/.append('<span>');
            $td.append($a).attr('data-type', this._getType(value, column_type))/*.css('display', 'inline-block')*/;
            //var sortable = this.sortable();
            this._sortChanged($td);
//            this._setSortAction($td, sortable);
            $a.children().css({'vertical-align': 'middle'}); //.css({'display': 'inline-block', 'vertical-align': 'middle'});
        } else {
            $td.append($('<span>').css('display', 'inline-block'));
        }
        $td.addClass('col-type-' + column_type);
        return this._setValue($td, value, row, column, column_type);
    };

    p._setValue = function ($td, value, row, column, column_type) {
        //$td.empty();
        var dataVal;
        var dataName;
        var isCellHeader = row < 0;
//        var $content = $td.children().eq(0); //= $('<span>').css('display', 'inline-block');
        if (isCellHeader) {
            //$content = $('<a>').css('display', 'inline-block').attr('href','#');
            dataVal = "" + value;
            dataName = dataVal;
        } else {
            //$content = $('<span>').css('display', 'inline-block');
            var is_date = (value instanceof Date);
            var is_str_or_number = is_date ? false : typeof value === 'string' || typeof value === 'number';
            dataVal = is_date ? value.getTime() : value;
            dataName = is_date ? value.toLocaleString() : (is_str_or_number ? value + "" : ((value === null || value === undefined) ? "" : JSON.stringify(value)));
            //return value instanceof Date ? $td.append($content.html(value.toLocaleString())).attr('data-val', value.getTime()) : $td.append($content.html(value)).attr('data-val', value);
        }
//        $content.html(dataName);

        dataName = this.getStrValue(value, dataName, row, column, column_type);

        var $content = isCellHeader ? $td.children('a').children().eq(0) : $td.children().eq(0);
        $content.html(dataName);
        if (!$content.find("*[title]").length) {
            $td.attr('title', dataVal);
        }
        //return $td;
        //this._setStrValue($td, dataName, isCellHeader);


        $td.attr('data-val', dataVal);
        return $td;
    };

//    p._setStrValue = function($td, string_value, isCellHeader) {
//        var $content = isCellHeader ? $td.children('a').children().eq(0) : $td.children().eq(0);
//        $content.html(string_value);
//        return $td;
//    };

    //index ==-1 means row header!!!!
    p._getRow = function (index) {
        if (index >= 0) {
            return this._getRows().eq(index);
        }
        //in case of header, assure there is a thead and populate it in case FIXME: improve!!!!
        var trs = this.thead.children('tr');
        var tr;
        if (trs.length === 0) {
            tr = $("<tr>"); //.css({'display':'block'}); //so that it takes the whole width (ps: unused anymore)
            this.thead.append(tr);
        } else {
            tr = trs.eq(0);
            if (trs.length > 1) {
                trs.remove();
                trs.append(tr);
            }
        }
        return tr;
    };

    //returns the rows of the table EXCLUDING the row header (use ._getRow(-1) for that)	
    p._getRows = function () {
        return this.table.children('tbody').children('tr');
    };

    p._getCell = function ($tr, index) {
        return this.__getCells($tr).eq(index); //$tr.children("td").eq(index);
    };

    p.__getCells = function ($tr) {
        return $tr.children("td");
    };

    //gets the value of a JQUERY element 
    p.__getValue = function ($td) {
        return $td.is("[data-val]") ? $td.attr('data-val') : $td.text(); //td.children('span').eq(0).text();
    };

    p._getColType = function (colindex) {
        return this._getCell(this._getRow(-1), colindex).attr('data-type') || "string";
    };

    p._getType = function (value, optional_type) {
        if ((optional_type === 'number') || (optional_type === 'string') || (optional_type === 'date')) {
            return optional_type;
        }
        var ret = typeof value;
        if (ret === 'number' || ret === 'string') {
            return ret;
        } else if (ret instanceof Date) {
            return 'date';
        }
        return 'string';
    };

    p._defaultSortAscendingText = function () {
        return "&darr;";
    };
    p._defaultSortDescendingText = function () {
        return "&uarr;";
    };
    p._defaultSortAscendingSVG = function () {
        return $('<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"\
			width="1em" height="1em" viewBox="0 0 512 512" enable-background="new 0 0 512 512" xml:space="preserve">\
			<path fill-rule="evenodd" clip-rule="evenodd" d="M256,352L96,198.406L141.719,160L256,275.188L370.281,160L416,198.406L256,352z"/>\
			</svg>');
    };
    p._defaultSortDescendingSVG = function () {
        return $('<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"\
			width="1em" height="1em" viewBox="0 0 512 512" enable-background="new 0 0 512 512" xml:space="preserve">\
			<path fill-rule="evenodd" clip-rule="evenodd" d="M256,160l160,153.594L370.281,352L256,236.812L141.719,352L96,313.594L256,160z"/>\
			</svg>');
    };
    //p._sortAscendingElement = p._defaultSortAscendingText;
    //p._sortDescendingElement = p._defaultSortDescendingText;
})(TableDiv.prototype);
