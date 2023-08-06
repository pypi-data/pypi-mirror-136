#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Copyright (C) 2007-2022 Gaetan Delannay

# This file is part of Appy.

# Appy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Appy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# Appy. If not, see <http://www.gnu.org/licenses/>.

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import copy
from persistent.list import PersistentList

from appy.px import Px
from appy.model.fields import Field
from appy.model.utils import Object as O
from appy.ui.layout import Layout, Layouts

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Total:
    '''Represents a computation that will be executed on a series of cells
       within a List field.'''
    def __init__(self, name, field, initValue):
        self.name = name # The sub-field name
        self.field = field # field.name is prefixed with the main field name
        self.value = initValue

    def __repr__(self):
        return '<Total %s=%s>' % (self.name, str(self.value))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Totals:
    '''If you want to add rows representing totals computed from regular List
       rows, specify it via Totals instances (see List attribute "totalRows"
       below).'''
    def __init__(self, id, label, subFields, onCell, initValue=0.0):
        # "id" must hold a short name or acronym and must be unique within all
        # Totals instances defined for a given List field.
        self.id = id
        # "label" is a i18n label that will be used to produce a longer name
        # that will be shown at the start of the total row.
        self.label = label
        # "subFields" is a list or tuple of sub-field names for which totals
        # must be computed.
        self.subFields = subFields
        # "onCell" stores a method that will be called every time a cell
        # corresponding to a field listed in self.subFields is walked in the
        # list. It will get these args:
        # * row      the current row as an Object instance;
        # * total    the Total instance (see above) corresponding to the current
        #            column;
        # * last     a boolean that is True if we are walking the last row.
        self.onCell = onCell
        # "initValue" is the initial value given to created Total instances
        self.initValue = initValue

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class List(Field):
    '''A list, stored as a list of Object instances ~[Object]~. Every object in
       the list has attributes named according to the sub-fields defined in this
       List.'''
    Totals = Totals

    # List is an "outer" field, made of inner fields
    outer = True

    class Layouts(Layouts):
        '''List-specific layouts'''
        g = Layouts(edit=Layout('f;rv=', width=None), view='fl')
        gd = Layouts(edit=Layout('d;v=f;', width=None), view='fl')
        # Default layouts for sub-fields
        sub = Layouts(Layout('frv', width=None))

        @classmethod
        def getDefault(class_, field):
            '''Default layouts for this List p_field'''
            return class_.g if field.inGrid() else super().getDefault(field)

    # A 1st invisible cell containing a virtual field allowing to detect this
    # row at server level.
    pxFirstCell = Px('''<td style="display: none">
     <table var="rid='%s*-row-*%s' % (field.name, rowId)"
            id=":'%d_%s' % (o.iid, rid)">
      <tr><td><input type="hidden" id=":rid" name=":rid"/></td></tr>
     </table></td>''')

    # PX for rendering a single row
    pxRow = Px('''
     <tr valign="top" style=":'display:none' if rowId == -1 else ''"
         class=":'odd' if loop.row.odd else 'even'">
      <x if="not isCell">:field.pxFirstCell</x>
      <td if="showTotals"></td>
      <td for="info in subFields" if="info[1]"
          var2="x=field.updateTotals(totals, o, info, row, loop.row.last);
                field=info[1];
                minimal=isCell;
                fieldName='%s*%d' % (field.name, rowId)">:field.pxRender</td>
      <!-- Icons -->
      <td if="isEdit" align=":dright">
       <img class="clickable iconS" src=":svg('deleteS')"
            title=":_('object_delete')"
            onclick=":field.jsDeleteConfirm(q, tableId)"/>
       <img class="clickable iconS" src=":svg('arrow')"
            style="transform: rotate(180deg)" title=":_('move_up')"
            onclick=":'moveRow(%s,%s,this)' % (q('up'), q(tableId))"/>
       <img class="clickable iconS" src=":svg('arrow')"
            title=":_('move_down')"
            onclick=":'moveRow(%s,%s,this)' % (q('down'), q(tableId))"/>
       <input class="clickable" type="image" tabindex="0"
              src=":url('addBelow')" title=":_('object_add_below')"
              onclick=":'insertRow(%s,this); return false' % q(tableId)"/>
      </td></tr>''')

    # Display totals (on view only) when defined
    pxTotals = Px('''
     <tr for="totalRow in field.totalRows" var2="total=totals[totalRow.id]">
      <th>:_(totalRow.label)</th>
      <th for="info in subFields">:field.getTotal(total, info)</th>
     </tr>''')

    # PX for rendering the list (shared between pxView, pxEdit and pxCell)
    pxTable = Px('''
     <table var="isEdit=layout == 'edit';
                 isCell=layout == 'cell';
                 tableId='list_%s' % name" if="isEdit or value"
            id=":tableId" width=":field.width" class="grid"
            var2="subFields=field.getSubFields(o, layout);
                  swidths=field.getWidths(subFields);
                  totals=field.createTotals(isEdit);
                  showTotals=not isEdit and totals">
      <!-- Header -->
      <thead>
       <tr valign="middle">
        <th if="showTotals"></th>
        <th for="name, sub in subFields" if="sub"
            width=":swidths[loop.name.nb]">
         <x var="field=sub">::field.getListHeader(_ctx_)</x></th>
        <!-- Icon for adding a new row -->
        <th if="isEdit">
         <img class="clickable" src=":url('plus')" title=":_('object_add')"
              onclick=":'insertRow(%s)' % q(tableId)"/>
        </th>
       </tr>
      </thead>

      <!-- Template row (edit only) -->
      <x var="rowId=-1" if="isEdit">:field.pxRow</x>

      <!-- Rows of data -->
      <x var="rows=field.getInputValue(inRequest, requestValue, value)"
         for="row in rows" var2="rowId=loop.row.nb">:field.pxRow</x>

      <!-- Totals -->
      <x if="showTotals">:field.pxTotals</x>
     </table>''')

    view = cell = Px('''<x>:field.pxTable</x>''')
    edit = Px('''<x>
     <!-- This input makes Appy aware that this field is in the request -->
     <input type="hidden" name=":name" value=""/><x>:field.pxTable</x>
    </x>''',

     js='''
       updateRowNumber = function(row, rowIndex, action) {
         /* Within p_row, we must find tables representing fields. Every such
            table has an id of the form [objectId]_[field]*[subField]*[i].
            Within this table, for every occurrence of this string, the "[i]"
            must be replaced with an updated index. If p_action is 'set',
            p_rowIndex is this index. If p_action is 'add', the index must
            become [i] + p_rowIndex. */

         // Browse tables representing fields
         var fields = row.getElementsByTagName('table'),
             tagTypes = ['input', 'select', 'img', 'textarea', 'a', 'script'],
             newIndex = -1, id, old, elems, neww, val, w, oldIndex;

         // Patch fields
         for (var i=0; i<fields.length; i++) {
           // Extract, from the table ID, the field identifier
           id = fields[i].id;
           if ((!id) || (id.indexOf('_') == -1)) continue;
           // Extract info from the field identifier
           old = id.split('_')[1];
           elems = old.split('*');
           /* Get "old" as a regular expression: we may need multiple
              replacements. */
           old = new RegExp(old.replace(/\\*/g, '\\\\*'), 'g');
           // Compute the new index (if not already done) and new field ID
           if (newIndex == -1) {
             oldIndex = parseInt(elems[2]);
             newIndex = (action == 'set')? rowIndex: oldIndex + rowIndex;
           }
           neww = elems[0] + '*' + elems[1] + '*' + newIndex;
           // Replace the table ID with its new ID
           fields[i].id = fields[i].id.replace(old, neww);
           // Find sub-elements mentioning "old" and replace it with "neww"
           val = w = null;
           for (var j=0; j<tagTypes.length; j++) {
             var widgets = fields[i].getElementsByTagName(tagTypes[j]);
             for (var k=0; k<widgets.length; k++) {
               w = widgets[k];
               // Patch id
               val = w.id;
               if (val) w.id = val.replace(old, neww);
               // Patch name
               val = w.name;
               if (val) w.name = val.replace(old, neww);
               // Patch href
               if ((w.nodeName == 'A') && w.href)
                 { w.href = w.href.replace(old, neww); }
               // Patch (and reeval) script
               if (w.nodeName == 'SCRIPT') {
                 w.text = w.text.replace(old, neww);
                 eval(w.text);
               }
             }
           }
         }
       }

       insertRow = function(tableId, previous) {
         /* Add a new row in table with ID p_tableId, after p_previous row or at
            the end if p_previous is null. */
         var table = document.getElementById(tableId),
             body = table.tBodies[0],
             rows = table.rows,
             newRow = rows[1].cloneNode(true),
             next = (previous)? \
                    previous.parentNode.parentNode.nextElementSibling : null;
         newRow.style.display = 'table-row';
         if (next) {
           var newIndex = next.rowIndex;
           // We must insert the new row before it
           body.insertBefore(newRow, next);
           // The new row takes the index of "next" (- the 2 unsignificant rows)
           updateRowNumber(newRow, newIndex-2, 'set');
           // Row numbers for "next" and the following rows must be incremented
           for (var i=newIndex+1; i < rows.length; i++) {
             updateRowNumber(rows[i], 1, 'add');
           }
         }
         else {
           // We must insert the new row at the end
           body.appendChild(newRow);
           // Within newRow, incorporate the row nb within field names and ids
           updateRowNumber(newRow, rows.length-3, 'set');
         }
       }

       deleteRow = function(tableId, deleteImg, ask, rowIndex) {
         var table = document.getElementById(tableId),
             rows = table.rows,
             row = (deleteImg)? deleteImg.parentNode.parentNode: rows[rowIndex];
             rowIndex = row.rowIndex;
         // Must we ask the user to confirm this action ?
         if (ask) {
             askConfirm('script',
                        'deleteRow("'+tableId+'",null,false,'+rowIndex+')');
             return;
         }
         // Decrement higher row numbers by 1 because of the deletion
         for (var i=rowIndex+1; i < rows.length; i++) {
           updateRowNumber(rows[i], -1, 'add');
         }
         table.deleteRow(rowIndex);
       }

       moveRow = function(direction, tableId, moveImg) {
         var row = moveImg.parentNode.parentNode,
             body = document.getElementById(tableId).tBodies[0], sibling;
         // Move up or down
         if (direction == 'up') {
           sibling = row.previousElementSibling;
           if (sibling && sibling.style.display != 'none') {
             updateRowNumber(row, -1, 'add');
             updateRowNumber(sibling, 1, 'add');
             body.insertBefore(row, sibling);
           }
         }
         else if (direction == 'down') {
           sibling = row.nextElementSibling;
           if (sibling) {
             updateRowNumber(row, 1, 'add');
             updateRowNumber(sibling, -1, 'add');
             // If sibling is null, row will be added to the end
             sibling = sibling.nextElementSibling;
             body.insertBefore(row, sibling);
           }
         }
       }''')

    search = ''

    def __init__(self, fields, validator=None, multiplicity=(0,1), default=None,
      defaultOnEdit=None, show=True, page='main', group=None, layouts=None,
      move=0, readPermission='read', writePermission='write', width='',
      height=None, maxChars=None, colspan=1, master=None, masterValue=None,
      focus=False, historized=False, mapping=None, generateLabel=None,
      label=None, subLayouts=Layouts.sub, widths=None, view=None, cell=None,
      edit=None, xml=None, translations=None, deleteConfirm=False,
      totalRows=None):
        Field.__init__(self, validator, multiplicity, default, defaultOnEdit,
         show, page, group, layouts, move, False, True, None, None, False, None,
         readPermission, writePermission, width, height, None, colspan, master,
         masterValue, focus, historized, mapping, generateLabel, label, None,
         None, None, None, True, False, view, cell, edit, xml, translations)
        self.validable = True
        # Tuple of elements of the form (name, Field instance) determining the
        # format of every element in the list. It can also be a method returning
        # this tuple. In that case, however, no i18n label will be generated for
        # the sub-fields: these latters must be created with a value for
        # attribute "translations".
        self.fields = fields
        # Force some layouting for sub-fields, if p_subLayouts are passed. If
        # you want freedom to tune layouts at the field level, you must specify
        # p_subLayouts=None.
        self.subLayouts = subLayouts
        # One may specify the width of every column in the list. Indeed, using
        # widths and layouts at the sub-field level may not be sufficient.
        self.widths = widths
        # Initialize sub-fields, if statically known
        if not callable(fields):
            self.initSubFields(fields)
        # When deleting a row, must we display a popup for confirming it ?
        self.deleteConfirm = deleteConfirm
        # If you want to specify additional rows representing totals, give in
        # "totalRows" a list of Totals instances (see above).
        self.totalRows = totalRows or []

    def initSubFields(self, subFields):
        '''Initialises sub-fields' attributes'''
        # Initialise sub-layouts
        subLayouts = self.subLayouts
        if subLayouts:
            for name, field in subFields:
                field.layouts = Layouts.getFor(self, subLayouts)

    def lazyInitSubFields(self, subFields, class_):
        '''Lazy-initialise sub-fields, when known'''
        # It can be at server startup, if sub-fields are statically defined, or
        # everytime a List field is solicited, if sub-fields are dynamically
        # computed.
        for sub, field in subFields:
            fullName = '%s_%s' % (self.name, sub)
            field.init(class_, fullName)
            field.name = '%s*%s' % (self.name, sub)

    def init(self, class_, name):
        '''List-specific lazy initialisation'''
        Field.init(self, class_, name)
        subs = self.fields
        if not callable(subs):
            self.lazyInitSubFields(subs, class_)

    def getWidths(self, subFields):
        '''Get the widths to appply to these p_subFields'''
        return self.widths or [''] * len(subFields)

    def getField(self, name):
        '''Gets the field definition whose name is p_name'''
        for n, field in self.fields:
            if n == name: return field

    def getSubFields(self, o, layout=None):
        '''Returns the sub-fields, as a list of tuples ~[(s_name, Field)]~,
           being showable, among p_self.fields on this p_layout. Fields that
           cannot appear in the result are nevertheless present as a tuple
           (s_name, None). This way, it keeps a nice layouting of the table.'''
        fields = self.fields
        if callable(fields):
            # Dynamically computed fields: get and completely initialise them
            fields = self.getAttribute(o, 'fields') # Involves caching
            self.initSubFields(fields)
            self.lazyInitSubFields(fields, o.class_)
        # Stop here if no p_layout is passed
        if layout is None: return fields
        # Retain only sub-fields being showable on this p_layout
        r = []
        for n, field in fields:
            f = field if field.isShowable(o, layout) else None
            r.append((n, f))
        return r

    def getRequestValue(self, o, requestName=None):
        '''Concatenates the list from distinct form elements in the request'''
        req = o.req
        name = requestName or self.name # A List may be into another List (?)
        prefix = name + '*-row-*' # Allows to detect a row of data for this List
        r = {}
        isDict = True # We manage both List and Dict
        for key in req.keys():
            if not key.startswith(prefix): continue
            # I have found a row: get its index
            row = O()
            rowId = key.split('*')[-1]
            if rowId == '-1': continue # Ignore the template row
            for subName, subField in self.getSubFields(o):
                keyName = '%s*%s*%s' % (name, subName, rowId)
                if keyName + subField.getRequestSuffix() in req:
                    v = subField.getRequestValue(o, requestName=keyName)
                    setattr(row, subName, v)
            if rowId.isdigit():
                rowId = int(rowId)
                isDict = False
            else:
                # Remove the -d- prefix
                rowId = rowId[3:]
            r[rowId] = row
        # Produce a sorted list (List only)
        if not isDict:
            keys = list(r.keys())
            keys.sort()
            r = [r[key] for key in keys]
        # I store in the request this computed value. This way, when individual
        # subFields will need to get their value, they will take it from here,
        # instead of taking it from the specific request key. Indeed, specific
        # request keys contain row indexes that may be wrong after row deletions
        # by the user.
        if r: req[name] = r
        return r

    def setRequestValue(self, o):
        '''Sets in the request, the field value on p_o in its "request-
           carriable" form.'''
        value = self.getValue(o)
        if value is not None:
            req = o.req
            name = self.name
            i = 0
            for row in value:
                req['%s*-row-*%d' % (name, i)] = ''
                for n, v in row.d().items():
                    key = '%s*%s*%d' % (name, n, i)
                    req[key] = v
                i += 1

    def getStorableRowValue(self, o, requestValue):
        '''Gets a ready-to-store Object instance representing a single row,
           from p_requestValue.'''
        r = O()
        for name, field in self.getSubFields(o):
            if not hasattr(requestValue, name) and \
               not field.isShowable(o, 'edit'):
                # Some fields, although present on "edit", may not be part of
                # the p_requestValue (ie, a "select multiple" with no value at
                # all will not be part of the POST HTTP request). If we want to
                # know if the field was in the request or not, we must then
                # check if it is showable on layout "edit".
                continue
            subValue = getattr(requestValue, name, None)
            try:
                setattr(r, name,
                        field.getStorableValue(o, subValue, single=True))
            except ValueError:
                # The value for this field for this specific row is incorrect.
                # It can happen in the process of validating the whole List
                # field (a call to m_getStorableValue occurs at this time). We
                # don't care about it, because later on we will have sub-field
                # specific validation that will also detect the error and will
                # prevent storing the wrong value in the database.
                setattr(r, name, subValue)
        return r

    def getStorableValue(self, o, value, single=False):
        '''Gets p_value in a form that can be stored in the database'''
        return [self.getStorableRowValue(o, v) for v in value]

    def getCopyValue(self, o):
        '''Return a (deep) copy of field value on p_obj''' 
        r = getattr(o, self.name, None)
        if r: return copy.deepcopy(r)

    def getCss(self, o, layout, r):
        '''Gets the CSS required by sub-fields if any'''
        for name, field in self.getSubFields(o, layout):
            if field:
                field.getCss(o, layout, r)

    def getJs(self, o, layout, r, config):
        '''Gets the JS required by sub-fields if any'''
        for name, field in self.getSubFields(o, layout):
            if field:
                field.getJs(o, layout, r, config)

    def jsDeleteConfirm(self, q, tableId):
        '''Gets the JS code to call when the user wants to delete a row'''
        confirm = 'true' if self.deleteConfirm else 'false'
        return 'deleteRow(%s,this,%s)' % (q(tableId), confirm)

    def subValidate(self, o, value, errors):
        '''Validates inner fields'''
        i = -1
        for row in value:
            i += 1
            for name, subField in self.getSubFields(o):
                message = subField.validate(o, getattr(row, name, None))
                if message:
                    setattr(errors, '%s*%d' % (subField.name, i), message)

    def createTotals(self, isEdit):
        '''When rendering the List field, if total rows are defined, create a
           Total instance for every sub-field for which a total must be
           computed.'''
        if isEdit or not self.totalRows: return
        r = {} # Keyed by Totals.name
        for totals in self.totalRows:
            subTotals = O()
            for name in totals.subFields:
                totalObj = Total(name, self.getField(name), totals.initValue)
                setattr(subTotals, name, totalObj)
            r[totals.id] = subTotals
        return r

    def updateTotals(self, totals, o, info, row, last):
        '''Every time a cell is encountered while rendering the List, this
           method is called to update totals when needed'''
        if not totals: return
        # Browse Totals instances
        for totalRow in self.totalRows:
            # Are there totals to update ?
            total = getattr(totals[totalRow.id], info[0], None)
            if total:
                totalRow.onCell(o, row, total, last)

    def getTotal(self, totals, info):
        '''Get the total for the field p_info if available'''
        total = getattr(totals, info[0], None)
        if total: return total.value
        return ''
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
