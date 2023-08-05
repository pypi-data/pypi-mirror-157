(self["webpackChunkjupyterlab_sql_plugin"] = self["webpackChunkjupyterlab_sql_plugin"] || []).push([["lib_index_js"],{

/***/ "./lib/api/databaseStructure.js":
/*!**************************************!*\
  !*** ./lib/api/databaseStructure.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatabaseStructureResponse": () => (/* binding */ DatabaseStructureResponse),
/* harmony export */   "getDatabaseStructure": () => (/* binding */ getDatabaseStructure)
/* harmony export */ });
/* harmony import */ var _server__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./server */ "./lib/api/server.js");

async function getDatabaseStructure(connectionUrl) {
    const request = {
        method: 'POST',
        body: JSON.stringify({ connectionUrl })
    };
    const response = await _server__WEBPACK_IMPORTED_MODULE_0__.Server.makeRequest('/jupyterlab-sql/database', request);
    if (!response.ok) {
        return Private.createErrorResponse(response.status);
    }
    const data = await response.json();
    return data;
}
var DatabaseStructureResponse;
(function (DatabaseStructureResponse) {
    function createError(message) {
        return {
            responseType: 'error',
            responseData: {
                message
            }
        };
    }
    DatabaseStructureResponse.createError = createError;
    function createNotFoundError() {
        const errorMessage = 'Failed to reach server endpoints. ' +
            'Is the server extension installed correctly?';
        return createError(errorMessage);
    }
    DatabaseStructureResponse.createNotFoundError = createNotFoundError;
    function match(response, onSuccess, onError) {
        if (response.responseType === 'error') {
            return onError(response.responseData);
        }
        else if (response.responseType === 'success') {
            const { responseData } = response;
            const tables = responseData.tables;
            // Backwards compatibility with server: views can be null or undefined.
            // Remove in versions 4.x.
            const views = responseData.views || [];
            const databaseObjects = {
                tables,
                views
            };
            return onSuccess(databaseObjects);
        }
    }
    DatabaseStructureResponse.match = match;
})(DatabaseStructureResponse || (DatabaseStructureResponse = {}));
var Private;
(function (Private) {
    function createErrorResponse(responseStatus) {
        if (responseStatus === 404) {
            return DatabaseStructureResponse.createNotFoundError();
        }
        else {
            const errorMessage = 'Unexpected response status from server';
            return DatabaseStructureResponse.createError(errorMessage);
        }
    }
    Private.createErrorResponse = createErrorResponse;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/api/query.js":
/*!**************************!*\
  !*** ./lib/api/query.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ResponseModel": () => (/* binding */ ResponseModel),
/* harmony export */   "getForQuery": () => (/* binding */ getForQuery)
/* harmony export */ });
/* harmony import */ var _server__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./server */ "./lib/api/server.js");

async function getForQuery(connectionUrl, query) {
    const request = {
        method: 'POST',
        body: JSON.stringify({ connectionUrl, query })
    };
    const response = await _server__WEBPACK_IMPORTED_MODULE_0__.Server.makeRequest('/jupyterlab-sql/query', request);
    if (!response.ok) {
        return Private.createErrorResponse(response.status);
    }
    const data = await response.json();
    return data;
}
var ResponseModel;
(function (ResponseModel) {
    function createError(message) {
        return {
            responseType: 'error',
            responseData: {
                message
            }
        };
    }
    ResponseModel.createError = createError;
    function createNotFoundError() {
        const errorMessage = 'Failed to reach server endpoints. ' +
            'Is the server extension installed correctly?';
        return createError(errorMessage);
    }
    ResponseModel.createNotFoundError = createNotFoundError;
    function match(response, onSuccessWithRows, onSuccessNoRows, onError) {
        if (response.responseType === 'error') {
            return onError(response.responseData);
        }
        // response.responseType === 'success'
        const responseData = response.responseData;
        if (responseData.hasRows) {
            const { keys, rows } = responseData;
            return onSuccessWithRows(keys, rows);
        }
        else {
            return onSuccessNoRows();
        }
    }
    ResponseModel.match = match;
})(ResponseModel || (ResponseModel = {}));
var Private;
(function (Private) {
    function createErrorResponse(responseStatus) {
        if (responseStatus === 404) {
            return ResponseModel.createNotFoundError();
        }
        else {
            const errorMessage = 'Unexpected response status from server';
            return ResponseModel.createError(errorMessage);
        }
    }
    Private.createErrorResponse = createErrorResponse;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/api/server.js":
/*!***************************!*\
  !*** ./lib/api/server.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Server": () => (/* binding */ Server)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


var Server;
(function (Server) {
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    async function makeRequest(endpoint, request) {
        const url = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, endpoint);
        return await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(url, request, settings);
    }
    Server.makeRequest = makeRequest;
})(Server || (Server = {}));


/***/ }),

/***/ "./lib/api/tableStructure.js":
/*!***********************************!*\
  !*** ./lib/api/tableStructure.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TableStructureResponse": () => (/* binding */ TableStructureResponse),
/* harmony export */   "getTableStructure": () => (/* binding */ getTableStructure)
/* harmony export */ });
/* harmony import */ var _server__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./server */ "./lib/api/server.js");

async function getTableStructure(connectionUrl, tableName) {
    const payload = {
        connectionUrl,
        table: tableName
    };
    const request = {
        method: 'POST',
        body: JSON.stringify(payload)
    };
    const response = await _server__WEBPACK_IMPORTED_MODULE_0__.Server.makeRequest('/jupyterlab-sql/table', request);
    if (!response.ok) {
        return Private.createErrorResponse(response.status);
    }
    const data = await response.json();
    return data;
}
var TableStructureResponse;
(function (TableStructureResponse) {
    function createError(message) {
        return {
            responseType: 'error',
            responseData: {
                message
            }
        };
    }
    TableStructureResponse.createError = createError;
    function createNotFoundError() {
        const errorMessage = 'Failed to reach server endpoints. ' +
            'Is the server extension installed correctly?';
        return createError(errorMessage);
    }
    TableStructureResponse.createNotFoundError = createNotFoundError;
    function match(response, onSuccess, onError) {
        if (response.responseType === 'error') {
            return onError(response.responseData);
        }
        // response.responseType === 'success'
        const { keys, rows } = response.responseData;
        return onSuccess(keys, rows);
    }
    TableStructureResponse.match = match;
})(TableStructureResponse || (TableStructureResponse = {}));
var Private;
(function (Private) {
    function createErrorResponse(responseStatus) {
        if (responseStatus === 404) {
            return TableStructureResponse.createNotFoundError();
        }
        else {
            const errorMessage = 'Unexpected response status from server';
            return TableStructureResponse.createError(errorMessage);
        }
    }
    Private.createErrorResponse = createErrorResponse;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/components/PreWidget.js":
/*!*************************************!*\
  !*** ./lib/components/PreWidget.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "PreWidget": () => (/* binding */ PreWidget)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

class PreWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(content) {
        super();
        const element = document.createElement('div');
        const pre = document.createElement('pre');
        pre.innerHTML = content;
        element.appendChild(pre);
        this.node.appendChild(element);
    }
}


/***/ }),

/***/ "./lib/components/ResultsTable.js":
/*!****************************************!*\
  !*** ./lib/components/ResultsTable.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ResultsTable": () => (/* binding */ ResultsTable)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_commands__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/commands */ "webpack/sharing/consume/default/@lumino/commands");
/* harmony import */ var _lumino_commands__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_commands__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _Table__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Table */ "./lib/components/Table.js");




var CommandIds;
(function (CommandIds) {
    CommandIds.copyToClipboard = 'copy-selection-to-clipboard';
})(CommandIds || (CommandIds = {}));
class ResultsTable {
    constructor(keys, data) {
        this._isDisposed = false;
        const contextMenu = this._createContextMenu();
        this._table = _Table__WEBPACK_IMPORTED_MODULE_3__.Table.fromKeysRows(keys, data, { contextMenu });
    }
    get widget() {
        return this._table.widget;
    }
    dispose() {
        this._table.dispose();
        this._isDisposed = true;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    _createContextMenu() {
        const commands = new _lumino_commands__WEBPACK_IMPORTED_MODULE_2__.CommandRegistry();
        commands.addCommand(CommandIds.copyToClipboard, {
            label: 'Copy cell',
            iconClass: 'jp-MaterialIcon jp-CopyIcon',
            execute: () => this._copySelectionToClipboard()
        });
        const menu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Menu({ commands });
        menu.addItem({ command: CommandIds.copyToClipboard });
        return menu;
    }
    _copySelectionToClipboard() {
        const selectionValue = this._table.selectionValue;
        if (selectionValue !== null) {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Clipboard.copyToSystem(String(selectionValue));
        }
    }
}


/***/ }),

/***/ "./lib/components/SingletonPanel.js":
/*!******************************************!*\
  !*** ./lib/components/SingletonPanel.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "SingletonPanel": () => (/* binding */ SingletonPanel)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

class SingletonPanel extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor() {
        super(...arguments);
        this.layout = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.SingletonLayout();
    }
    onResize(_) {
        if (this._item) {
            this._fitCurrentWidget();
        }
    }
    onActivateRequest() {
        const widget = this.layout.widget;
        if (widget) {
            // Focus the content node if we aren't already focused on it or a
            // descendent.
            if (!widget.node.contains(document.activeElement)) {
                widget.node.focus();
            }
            // Activate the content asynchronously (which may change the focus).
            widget.activate();
        }
    }
    set widget(widget) {
        if (!this.isDisposed) {
            this.layout.widget = widget;
            this._item = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.LayoutItem(this.layout.widget);
            this._fitCurrentWidget();
        }
    }
    _fitCurrentWidget() {
        this._item.update(0, 0, this.node.offsetWidth, this.node.offsetHeight);
    }
}


/***/ }),

/***/ "./lib/components/Table.js":
/*!*********************************!*\
  !*** ./lib/components/Table.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Table": () => (/* binding */ Table)
/* harmony export */ });
/* harmony import */ var _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/datagrid */ "webpack/sharing/consume/default/@lumino/datagrid/@lumino/datagrid");
/* harmony import */ var _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../services/dataGridExtensions */ "./lib/services/dataGridExtensions/selectionManager.js");
/* harmony import */ var _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../services/dataGridExtensions */ "./lib/services/dataGridExtensions/events.js");
/* harmony import */ var _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../services/dataGridExtensions */ "./lib/services/dataGridExtensions/columnWidth.js");



var Colors;
(function (Colors) {
    Colors.unselectedBackgroundColor = 'white';
    Colors.selectedBackgroundColor = '#2196f3';
    Colors.unselectedTextColor = 'black';
    Colors.selectedTextColor = 'white';
})(Colors || (Colors = {}));
class Table {
    constructor(model, options) {
        this._dblclickSignal = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._isDisposed = false;
        this._grid = new _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__.DataGrid();
        this._grid.dataModel = model;
        this._options = options;
        this._selectionManager = new _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_2__.SelectionManager(model);
        this._onClick = this._onClick.bind(this);
        this._onContextMenu = this._onContextMenu.bind(this);
        this._onDoubleClick = this._onDoubleClick.bind(this);
        this._selectionManager.selectionChanged.connect(() => {
            this._updateRenderers();
        });
        this._clickEventHandler = _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_3__.addMouseEventListener('click', this._grid, this._onClick);
        this._contextMenuEventHandler = _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_3__.addMouseEventListener('contextmenu', this._grid, this._onContextMenu);
        this._dblclickEventHandler = _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_3__.addMouseEventListener('dblclick', this._grid, this._onDoubleClick);
        this._fitColumnWidths();
    }
    static fromKeysRows(keys, data, options) {
        const model = new TableDataModel(keys, data);
        return new Table(model, options);
    }
    get widget() {
        return this._grid;
    }
    get selection() {
        return this._selectionManager.selection;
    }
    get selectionValue() {
        const selection = this.selection;
        if (selection !== null) {
            return this.getCellValue(selection);
        }
        return null;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    get dblclickSignal() {
        return this._dblclickSignal;
    }
    getCellValue(cellIndex) {
        const { rowIndex, columnIndex } = cellIndex;
        const value = this._grid.dataModel.data('body', rowIndex, columnIndex);
        return value;
    }
    dispose() {
        this._clickEventHandler.dispose();
        this._contextMenuEventHandler.dispose();
        this._dblclickEventHandler.dispose();
        this._grid.dispose();
        this._isDisposed = true;
    }
    _fitColumnWidths() {
        _services_dataGridExtensions__WEBPACK_IMPORTED_MODULE_4__.fitColumnWidths(this._grid, new _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__.TextRenderer());
    }
    _onClick(event) {
        const { row, column } = event;
        this._updateSelection(row, column);
    }
    _onContextMenu(event) {
        const { row, column, rawEvent } = event;
        this._updateSelection(row, column);
        if (this._isInBody(row, column)) {
            this._options.contextMenu.open(rawEvent.clientX, rawEvent.clientY);
            rawEvent.preventDefault();
        }
    }
    _onDoubleClick(event) {
        const { row, column } = event;
        if (this._isInBody(row, column)) {
            const cellIndex = {
                rowIndex: row.index,
                columnIndex: column.index
            };
            this._dblclickSignal.emit(cellIndex);
        }
    }
    _updateSelection(row, column) {
        if (this._isInBody(row, column)) {
            this._selectionManager.selection = {
                rowIndex: row.index,
                columnIndex: column.index
            };
        }
        else {
            this._selectionManager.selection = null;
        }
    }
    _isInBody(row, column) {
        return (row.section === 'row' &&
            column.section === 'column' &&
            row.index !== null &&
            column.index !== null);
    }
    _updateRenderers() {
        const renderer = this._textRendererForSelection(this._selectionManager.selection);
        this._grid.cellRenderers.update({ body: renderer });
    }
    _textRendererForSelection(selectedCell) {
        let backgroundColor;
        let textColor;
        if (selectedCell === null) {
            backgroundColor = Colors.unselectedBackgroundColor;
            textColor = Colors.unselectedTextColor;
        }
        else {
            const selectedRow = selectedCell.rowIndex;
            const selectedColumn = selectedCell.columnIndex;
            backgroundColor = ({ row, column }) => {
                if (row === selectedRow && column === selectedColumn) {
                    return Colors.selectedBackgroundColor;
                }
                else {
                    return Colors.unselectedBackgroundColor;
                }
            };
            textColor = ({ row, column }) => {
                if (row === selectedRow && column === selectedColumn) {
                    return Colors.selectedTextColor;
                }
                else {
                    return Colors.unselectedTextColor;
                }
            };
        }
        return new _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__.TextRenderer({ backgroundColor, textColor });
    }
}
class TableDataModel extends _lumino_datagrid__WEBPACK_IMPORTED_MODULE_0__.DataModel {
    constructor(keys, data) {
        super();
        this._data = data;
        this._keys = keys;
    }
    rowCount(region) {
        return region === 'body' ? this._data.length : 1;
    }
    columnCount(region) {
        return region === 'body' ? this._keys.length : 1;
    }
    data(region, row, column) {
        if (region === 'row-header') {
            return row;
        }
        if (region === 'column-header') {
            return this._keys[column];
        }
        if (region === 'corner-header') {
            return '';
        }
        return this._serializeData(this._data[row][column]);
    }
    _serializeData(data) {
        const _type = typeof data;
        if (_type === 'object') {
            return JSON.stringify(data);
        }
        return data;
    }
}


/***/ }),

/***/ "./lib/components/ToolbarItems.js":
/*!****************************************!*\
  !*** ./lib/components/ToolbarItems.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ToolbarItems": () => (/* binding */ ToolbarItems)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _services__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../services */ "./lib/services/connectionUrl.js");



var ToolbarItems;
(function (ToolbarItems) {
    class TextItem extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
        constructor(value) {
            super();
            this.addClass('p-Sql-Toolbar-text');
            this.node.innerText = value;
        }
    }
    ToolbarItems.TextItem = TextItem;
    class ConnectionUrlItem extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
        constructor(url) {
            super();
            this.addClass('p-Sql-Toolbar-text');
            this.node.innerText = _services__WEBPACK_IMPORTED_MODULE_2__.ConnectionUrl.sanitize(url);
        }
    }
    ToolbarItems.ConnectionUrlItem = ConnectionUrlItem;
    class BackButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton {
        constructor(options) {
            super({
                iconClass: 'jp-UndoIcon jp-Icon jp-Icon-16',
                onClick: options.onClick
            });
        }
    }
    ToolbarItems.BackButton = BackButton;
    class RefreshButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton {
        constructor(options) {
            super({
                iconClass: 'jp-RefreshIcon jp-Icon jp-Icon-16',
                onClick: options.onClick
            });
        }
    }
    ToolbarItems.RefreshButton = RefreshButton;
    class LoadingIcon extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
        constructor() {
            super();
            ['jp-Toolbar-kernelStatus', 'jp-Icon', 'jp-Icon-16'].forEach(className => this.addClass(className));
            this.setLoading(false);
        }
        setLoading(isLoading) {
            if (isLoading) {
                this.removeClass('jp-CircleIcon');
                this.addClass('jp-FilledCircleIcon');
            }
            else {
                this.removeClass('jp-FilledCircleIcon');
                this.addClass('jp-CircleIcon');
            }
        }
    }
    ToolbarItems.LoadingIcon = LoadingIcon;
})(ToolbarItems || (ToolbarItems = {}));


/***/ }),

/***/ "./lib/connection/connectionEditor.js":
/*!********************************************!*\
  !*** ./lib/connection/connectionEditor.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ConnectionEditor": () => (/* binding */ ConnectionEditor),
/* harmony export */   "ConnectionEditorModel": () => (/* binding */ ConnectionEditorModel)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var classnames__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! classnames */ "./node_modules/classnames/index.js");
/* harmony import */ var classnames__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(classnames__WEBPACK_IMPORTED_MODULE_3__);




class ConnectionEditorModel extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.VDomModel {
    constructor(initialConnectionUrl) {
        super();
        this._connectionUrlChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._connect = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._connectionUrl = initialConnectionUrl;
    }
    tryConnect(connectionUrl) {
        this._connect.emit(connectionUrl);
    }
    get connectionUrl() {
        return this._connectionUrl;
    }
    set connectionUrl(newValue) {
        this._connectionUrl = newValue;
        this._connectionUrlChanged.emit(newValue);
    }
    get connect() {
        return this._connect;
    }
    get connectionUrlChanged() {
        return this._connectionUrlChanged;
    }
}
class ConnectionEditor extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.VDomRenderer {
    static withModel(model) {
        const editor = new ConnectionEditor(model);
        return editor;
    }
    onActivateRequest() {
        this.node.querySelector('input').focus();
    }
    render() {
        if (!this.model) {
            return null;
        }
        else {
            const connectionUrl = this.model.connectionUrl;
            return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: "p-Sql-ConnectionInformation-container" },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(ConnectionInformationEdit, { initialConnectionUrl: connectionUrl, onConnectionUrlChanged: newConnectionUrl => (this.model.connectionUrl = newConnectionUrl), onFinishEdit: currentConnectionUrl => this.model.tryConnect(currentConnectionUrl) }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(ConnectionInformationHelper, null)));
        }
    }
}
class ConnectionInformationEdit extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    constructor(props) {
        super(props);
        this.inputRef = react__WEBPACK_IMPORTED_MODULE_0__.createRef();
        this.state = {
            connectionUrl: props.initialConnectionUrl,
            focused: false
        };
    }
    onKeyDown(event) {
        if (event.key === 'Enter') {
            this.finish();
        }
        else if (event.keyCode === 27) {
            // ESC key
            this.cancel();
        }
    }
    onChange(event) {
        const newConnectionUrl = event.target.value;
        this.props.onConnectionUrlChanged(newConnectionUrl);
        this.setState({ connectionUrl: newConnectionUrl });
    }
    start() {
        this.setState({
            focused: true
        });
    }
    finish() {
        this.props.onFinishEdit(this.state.connectionUrl);
        this.setState({
            focused: false
        });
    }
    cancel() {
        const newConnectionUrl = this.props.initialConnectionUrl;
        this.props.onConnectionUrlChanged(newConnectionUrl);
        this.setState({ connectionUrl: newConnectionUrl });
    }
    onInputFocus() {
        this.start();
    }
    onInputBlur() {
        this.setState({
            focused: false
        });
    }
    componentDidMount() {
        this.inputRef.current.focus();
    }
    render() {
        const { connectionUrl, focused } = this.state;
        const inputWrapperClass = classnames__WEBPACK_IMPORTED_MODULE_3___default()('p-Sql-ConnectionInformation-input-wrapper', { 'p-mod-focused': focused });
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: "p-Sql-ConnectionInformation-wrapper" },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: inputWrapperClass },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("input", { className: "p-Sql-ConnectionInformation-text p-Sql-ConnectionInformation-input", value: connectionUrl, ref: this.inputRef, autoFocus: true, onChange: event => this.onChange(event), onKeyDown: event => this.onKeyDown(event), onBlur: () => this.onInputBlur(), onFocus: () => this.onInputFocus() }))));
    }
}
class ConnectionInformationHelper extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("details", { className: "jp-RenderedHTMLCommon" },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("summary", null, "Help"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("p", null,
                "Press ",
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("code", null, "Enter"),
                " to connect to the database."),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("p", null,
                "The URL must be a database URL. Follow the",
                ' ',
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("a", { href: "https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls", target: "_blank" }, "SQLAlchemy guide"),
                ' ',
                "on URLs. For instance:"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("ul", null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("pre", null, "postgres://localhost:5432/postgres")),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("pre", null, "postgres://username:password@localhost:5432/postgres")),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("pre", null, "mysql://localhost/employees")),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("pre", null, "sqlite://")),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("pre", null, "sqlite:///myfile.db")))));
    }
}


/***/ }),

/***/ "./lib/connection/index.js":
/*!*********************************!*\
  !*** ./lib/connection/index.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ConnectionPage": () => (/* binding */ ConnectionPage)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _connectionEditor__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./connectionEditor */ "./lib/connection/connectionEditor.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../page */ "./lib/page.js");
/* harmony import */ var _services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../services */ "./lib/services/signalConnector.js");






class ConnectionPage {
    constructor(options) {
        this.pageName = _page__WEBPACK_IMPORTED_MODULE_3__.PageName.Connection;
        const { initialConnectionString } = options;
        this._content = new Content(initialConnectionString);
        this._connectDatabase = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._content.connectDatabase, this);
        this._connectionUrlChanged = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._content.connectionUrlChanged, this);
        this._toolbar = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Toolbar();
        this._disposables = _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__.DisposableSet.from([this._content, this._toolbar]);
    }
    get content() {
        return this._content;
    }
    get connectDatabase() {
        return this._connectDatabase;
    }
    get connectionUrlChanged() {
        return this._connectionUrlChanged;
    }
    get toolbar() {
        return this._toolbar;
    }
    get isDisposed() {
        return this._disposables.isDisposed;
    }
    dispose() {
        return this._disposables.dispose();
    }
}
class Content extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxPanel {
    constructor(initialConnectionString) {
        super();
        this.addClass('p-Sql-MainContainer');
        const connectionEditorModel = new _connectionEditor__WEBPACK_IMPORTED_MODULE_5__.ConnectionEditorModel(initialConnectionString);
        this._connectionWidget = _connectionEditor__WEBPACK_IMPORTED_MODULE_5__.ConnectionEditor.withModel(connectionEditorModel);
        this.addWidget(this._connectionWidget);
        _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxPanel.setStretch(this._connectionWidget, 1);
        this._connectDatabase = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(connectionEditorModel.connect, this);
        this._connectionUrlChanged = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(connectionEditorModel.connectionUrlChanged, this);
    }
    get connectDatabase() {
        return this._connectDatabase;
    }
    get connectionUrlChanged() {
        return this._connectionUrlChanged;
    }
    onActivateRequest() {
        this._connectionWidget.activate();
    }
}


/***/ }),

/***/ "./lib/databaseSummary/content.js":
/*!****************************************!*\
  !*** ./lib/databaseSummary/content.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatabaseSummaryModel": () => (/* binding */ DatabaseSummaryModel),
/* harmony export */   "DatabaseSummaryWidget": () => (/* binding */ DatabaseSummaryWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var classnames__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! classnames */ "./node_modules/classnames/index.js");
/* harmony import */ var classnames__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(classnames__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);




class DatabaseSummaryModel extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.VDomModel {
    constructor(tables) {
        super();
        this._navigateToTable = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal(this);
        this._navigateToCustomQuery = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal(this);
        this.tables = tables;
        this.onNavigateToTable = this.onNavigateToTable.bind(this);
        this.onNavigateToCustomQuery = this.onNavigateToCustomQuery.bind(this);
    }
    get navigateToTable() {
        return this._navigateToTable;
    }
    get navigateToCustomQuery() {
        return this._navigateToCustomQuery;
    }
    onNavigateToTable(tableName) {
        this._navigateToTable.emit(tableName);
    }
    onNavigateToCustomQuery() {
        this._navigateToCustomQuery.emit(void 0);
    }
}
class DatabaseSummaryWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.VDomRenderer {
    constructor(model) {
        super(model);
        this.addClass('p-Sql-DatabaseSummary-Container');
    }
    static withModel(model) {
        const tableList = new DatabaseSummaryWidget(model);
        return tableList;
    }
    render() {
        if (!this.model) {
            return null;
        }
        else {
            const { tables, onNavigateToTable, onNavigateToCustomQuery } = this.model;
            return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(TableList, { tableNames: tables, onNavigateToTable: onNavigateToTable, onNavigateToCustomQuery: onNavigateToCustomQuery }));
        }
    }
}
class TableList extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedItem: null
        };
        this.onTableItemClick = this.onTableItemClick.bind(this);
    }
    onTableItemClick(itemNumber) {
        this.setState({ selectedItem: itemNumber });
    }
    render() {
        const { tableNames, onNavigateToTable, onNavigateToCustomQuery } = this.props;
        const { selectedItem } = this.state;
        const tableItems = tableNames.map((tableName, i) => (react__WEBPACK_IMPORTED_MODULE_0__.createElement(TableListItem, { tableName: tableName, key: i, onClick: () => this.onTableItemClick(i), onDoubleClick: () => onNavigateToTable(tableName), selected: i === selectedItem })));
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: "p-Sql-TableList-container" },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("ul", { className: "p-Sql-TableList-content" },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(ListHeader, { headerText: "Actions" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(CustomQueryItem, { onClick: onNavigateToCustomQuery }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(ListHeader, { headerText: "Tables" }),
                tableItems)));
    }
}
class TableListItem extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    render() {
        const { tableName, onClick, onDoubleClick, selected } = this.props;
        const classes = classnames__WEBPACK_IMPORTED_MODULE_1___default()('jp-DirListing-item', {
            'jp-mod-selected': selected
        });
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", { onClick: onClick, onDoubleClick: onDoubleClick, className: classes, title: tableName },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-DirListing-itemIcon jp-MaterialIcon jp-SpreadsheetIcon" }),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-DirListing-itemText" }, tableName)));
    }
}
class CustomQueryItem extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    render() {
        const { onClick } = this.props;
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", { onClick: onClick, className: "jp-DirListing-item", title: "Custom SQL query" },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-DirListing-itemIcon jp-MaterialIcon jp-CodeConsoleIcon" }),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-DirListing-itemText" }, "Custom SQL query")));
    }
}
class ListHeader extends react__WEBPACK_IMPORTED_MODULE_0__.Component {
    render() {
        const { headerText } = this.props;
        return react__WEBPACK_IMPORTED_MODULE_0__.createElement("li", { className: "p-Sql-TableList-header" }, headerText);
    }
}


/***/ }),

/***/ "./lib/databaseSummary/index.js":
/*!**************************************!*\
  !*** ./lib/databaseSummary/index.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatabaseSummaryPage": () => (/* binding */ DatabaseSummaryPage)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components */ "./lib/components/SingletonPanel.js");
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../components */ "./lib/components/PreWidget.js");
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../api */ "./lib/api/databaseStructure.js");
/* harmony import */ var _services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../services */ "./lib/services/signalConnector.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../page */ "./lib/page.js");
/* harmony import */ var _toolbar__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./toolbar */ "./lib/databaseSummary/toolbar.js");
/* harmony import */ var _content__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./content */ "./lib/databaseSummary/content.js");








class DatabaseSummaryPage {
    constructor(options) {
        this.pageName = _page__WEBPACK_IMPORTED_MODULE_2__.PageName.DatabaseSummary;
        this._onRefresh = this._onRefresh.bind(this);
        this._content = new Content(options);
        this._toolbar = new _toolbar__WEBPACK_IMPORTED_MODULE_3__.DatabaseSummaryToolbar(options.connectionUrl);
        this._navigateBack = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._toolbar.backButtonClicked, this);
        this._toolbar.refreshButtonClicked.connect(this._onRefresh);
        this._customQueryClicked = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._content.customQueryClicked, this);
        this._navigateToTable = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._content.navigateToTable, this);
        this._disposables = _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__.DisposableSet.from([this._content, this._toolbar]);
        this._onRefresh();
    }
    get content() {
        return this._content;
    }
    get toolbar() {
        return this._toolbar;
    }
    get navigateBack() {
        return this._navigateBack;
    }
    get customQueryClicked() {
        return this._customQueryClicked;
    }
    get navigateToTable() {
        return this._navigateToTable;
    }
    get isDisposed() {
        return this._disposables.isDisposed;
    }
    dispose() {
        return this._disposables.dispose();
    }
    async _onRefresh() {
        this._toolbar.setLoading(true);
        await this._content.refresh();
        this._toolbar.setLoading(false);
    }
}
class Content extends _components__WEBPACK_IMPORTED_MODULE_5__.SingletonPanel {
    constructor(options) {
        super();
        this._databaseSummaryModel = null;
        this._customQueryClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._navigateToTable = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._connectionUrl = options.connectionUrl;
    }
    get customQueryClicked() {
        return this._customQueryClicked;
    }
    get navigateToTable() {
        return this._navigateToTable;
    }
    async refresh() {
        const response = await _api__WEBPACK_IMPORTED_MODULE_6__.getDatabaseStructure(this._connectionUrl);
        this._setResponse(response);
    }
    dispose() {
        this._disposeWidgets();
        super.dispose();
    }
    _setResponse(response) {
        this._disposeWidgets();
        _api__WEBPACK_IMPORTED_MODULE_6__.DatabaseStructureResponse.match(response, ({ tables, views }) => {
            const model = new _content__WEBPACK_IMPORTED_MODULE_7__.DatabaseSummaryModel([...tables, ...views]);
            this.widget = _content__WEBPACK_IMPORTED_MODULE_7__.DatabaseSummaryWidget.withModel(model);
            model.navigateToCustomQuery.connect(() => {
                this._customQueryClicked.emit(void 0);
            });
            model.navigateToTable.connect((_, tableName) => {
                this._navigateToTable.emit(tableName);
            });
            this._databaseSummaryModel = model;
        }, ({ message }) => {
            this.widget = new _components__WEBPACK_IMPORTED_MODULE_8__.PreWidget(message);
        });
    }
    _disposeWidgets() {
        if (this._databaseSummaryModel) {
            _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal.disconnectBetween(this._databaseSummaryModel, this);
            this._databaseSummaryModel.dispose();
        }
    }
}


/***/ }),

/***/ "./lib/databaseSummary/toolbar.js":
/*!****************************************!*\
  !*** ./lib/databaseSummary/toolbar.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatabaseSummaryToolbar": () => (/* binding */ DatabaseSummaryToolbar)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components */ "./lib/components/ToolbarItems.js");



class DatabaseSummaryToolbar extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar {
    constructor(connectionUrl) {
        super();
        this._loadingIcon = new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.LoadingIcon();
        this._backButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._refreshButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._onBackButtonClicked = this._onBackButtonClicked.bind(this);
        this._onRefreshButtonClicked = this._onRefreshButtonClicked.bind(this);
        this.addItem('back', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.BackButton({ onClick: this._onBackButtonClicked }));
        this.addItem('refresh', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.RefreshButton({ onClick: this._onRefreshButtonClicked }));
        this.addItem('spacer', _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar.createSpacerItem());
        this.addItem('url', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.ConnectionUrlItem(connectionUrl));
        this.addItem('loading', this._loadingIcon);
    }
    get backButtonClicked() {
        return this._backButtonClicked;
    }
    get refreshButtonClicked() {
        return this._refreshButtonClicked;
    }
    setLoading(isLoading) {
        this._loadingIcon.setLoading(isLoading);
    }
    _onBackButtonClicked() {
        this._backButtonClicked.emit(void 0);
    }
    _onRefreshButtonClicked() {
        this._refreshButtonClicked.emit(void 0);
    }
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! uuid */ "webpack/sharing/consume/default/uuid/uuid");
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(uuid__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/codeeditor */ "webpack/sharing/consume/default/@jupyterlab/codeeditor");
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _tracker__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./tracker */ "./lib/tracker.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./page */ "./lib/page.js");
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");










function activate(app, palette, launcher, editorServices, restorer, settingRegistry) {
    if (settingRegistry) {
        settingRegistry
            .load(plugin.id)
            .then(settings => {
            console.log('jupyterlab-sql-plugin settings loaded:', settings.composite);
        })
            .catch(reason => {
            console.error('Failed to load settings for jupyterlab-sql-plugin.', reason);
        });
    }
    const tracker = (0,_tracker__WEBPACK_IMPORTED_MODULE_7__.createTracker)();
    const command = 'jupyterlab-sql:open';
    restorer.restore(tracker, {
        command,
        args: widget => ({
            initialWidgetName: widget.name,
            initialPageName: widget.pageName,
            initialConnectionUrl: widget.connectionUrl,
            initialTableName: widget.tableName,
            initialSqlStatement: widget.sqlStatement
        }),
        name: widget => widget.name
    });
    app.commands.addCommand(command, {
        label: ({ isPalette }) => (isPalette ? 'New SQL session' : 'SQL'),
        iconClass: 'p-Sql-DatabaseIcon',
        execute: ({ initialWidgetName, initialPageName, initialConnectionUrl, initialTableName, initialSqlStatement }) => {
            const name = (initialWidgetName || uuid__WEBPACK_IMPORTED_MODULE_0__.v4());
            const pageName = (initialPageName || _page__WEBPACK_IMPORTED_MODULE_8__.PageName.Connection);
            const connectionUrl = ((initialConnectionUrl || 'postgres://localhost:5432/postgres'));
            const tableName = (initialTableName || '');
            const sqlStatement = (initialSqlStatement || '');
            const widget = new _widget__WEBPACK_IMPORTED_MODULE_9__.JupyterLabSqlWidget(editorServices.factoryService, {
                name,
                pageName,
                connectionUrl,
                tableName,
                sqlStatement
            });
            app.shell.add(widget);
            tracker.add(widget);
        }
    });
    palette.addItem({ command, category: 'SQL', args: { isPalette: true } });
    if (launcher) {
        launcher.add({ command, category: 'Other' });
    }
}
/**
 * Initialization data for the jupyterlab-sql-plugin extension.
 */
const plugin = {
    id: 'jupyterlab-sql-plugin:plugin',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ICommandPalette, _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_5__.ILauncher, _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_4__.IEditorServices, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILayoutRestorer],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__.ISettingRegistry],
    activate: activate
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/page.js":
/*!*********************!*\
  !*** ./lib/page.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "PageName": () => (/* binding */ PageName)
/* harmony export */ });
var PageName;
(function (PageName) {
    PageName[PageName["Connection"] = 0] = "Connection";
    PageName[PageName["DatabaseSummary"] = 1] = "DatabaseSummary";
    PageName[PageName["TableSummary"] = 2] = "TableSummary";
    PageName[PageName["CustomQuery"] = 3] = "CustomQuery";
})(PageName || (PageName = {}));


/***/ }),

/***/ "./lib/query/editor.js":
/*!*****************************!*\
  !*** ./lib/query/editor.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Editor": () => (/* binding */ Editor),
/* harmony export */   "EditorWidget": () => (/* binding */ EditorWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/codeeditor */ "webpack/sharing/consume/default/@jupyterlab/codeeditor");
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);


class Editor {
    constructor(initialValue, editorFactory) {
        this._execute = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._valueChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._model = new _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_0__.CodeEditor.Model({ value: initialValue });
        this._widget = new EditorWidget(this._model, editorFactory);
        this._model.value.changed.connect(() => {
            this._valueChanged.emit(this.value);
        });
        this._model.mimeType = 'text/x-sql';
        this._widget.executeCurrent.connect(() => {
            this._execute.emit(this.value);
        });
    }
    get value() {
        return this._model.value.text;
    }
    get widget() {
        return this._widget;
    }
    get execute() {
        return this._execute;
    }
    get valueChanged() {
        return this._valueChanged;
    }
}
class EditorWidget extends _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_0__.CodeEditorWrapper {
    constructor(model, editorFactory) {
        super({
            model,
            factory: editorFactory.newInlineEditor
        });
        this._executeCurrent = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this.editor.addKeydownHandler((_, evt) => this._onKeydown(evt));
        this.addClass('p-Sql-Editor');
    }
    get executeCurrent() {
        return this._executeCurrent;
    }
    _onKeydown(event) {
        if ((event.shiftKey || event.ctrlKey) && event.key === 'Enter') {
            this._executeCurrent.emit(void 0);
            return true;
        }
        return false;
    }
}


/***/ }),

/***/ "./lib/query/index.js":
/*!****************************!*\
  !*** ./lib/query/index.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "QueryPage": () => (/* binding */ QueryPage)
/* harmony export */ });
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! uuid */ "webpack/sharing/consume/default/uuid/uuid");
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(uuid__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../api */ "./lib/api/query.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../page */ "./lib/page.js");
/* harmony import */ var _services__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../services */ "./lib/services/signalConnector.js");
/* harmony import */ var _response__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./response */ "./lib/query/response.js");
/* harmony import */ var _editor__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./editor */ "./lib/query/editor.js");
/* harmony import */ var _toolbar__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./toolbar */ "./lib/query/toolbar.js");










class QueryPage {
    constructor(options) {
        this.pageName = _page__WEBPACK_IMPORTED_MODULE_4__.PageName.CustomQuery;
        this._onExecutionStarted = this._onExecutionStarted.bind(this);
        this._onExecutionFinished = this._onExecutionFinished.bind(this);
        this._content = new Content(options);
        this._toolbar = new _toolbar__WEBPACK_IMPORTED_MODULE_5__.QueryToolbar(options.connectionUrl);
        this._backButtonClicked = (0,_services__WEBPACK_IMPORTED_MODULE_6__.proxyFor)(this._toolbar.backButtonClicked, this);
        this._sqlStatementChanged = (0,_services__WEBPACK_IMPORTED_MODULE_6__.proxyFor)(this._content.sqlStatementChanged, this);
        this._content.executionStarted.connect(this._onExecutionStarted);
        this._content.executionFinished.connect(this._onExecutionFinished);
        this._disposables = _lumino_disposable__WEBPACK_IMPORTED_MODULE_3__.DisposableSet.from([this._content, this._toolbar]);
    }
    get toolbar() {
        return this._toolbar;
    }
    get content() {
        return this._content;
    }
    get backButtonClicked() {
        return this._backButtonClicked;
    }
    get sqlStatementChanged() {
        return this._sqlStatementChanged;
    }
    get isDisposed() {
        return this._disposables.isDisposed;
    }
    dispose() {
        return this._disposables.dispose();
    }
    _onExecutionStarted() {
        this._toolbar.setLoading(true);
    }
    _onExecutionFinished() {
        this._toolbar.setLoading(false);
    }
}
class Content extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.BoxPanel {
    constructor(options) {
        super();
        this._lastRequestId = '';
        this._executionStarted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal(this);
        this._executionFinished = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal(this);
        this.addClass('p-Sql-MainContainer');
        this.editor = new _editor__WEBPACK_IMPORTED_MODULE_7__.Editor(options.initialSqlStatement, options.editorFactory);
        this.response = new _response__WEBPACK_IMPORTED_MODULE_8__.Response();
        this.editor.execute.connect((_, value) => {
            this.updateGrid(options.connectionUrl, value);
        });
        this._sqlStatementChanged = (0,_services__WEBPACK_IMPORTED_MODULE_6__.proxyFor)(this.editor.valueChanged, this);
        this.addWidget(this.editor.widget);
        this.addWidget(this.response.widget);
        _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.BoxPanel.setStretch(this.editor.widget, 1);
        _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.BoxPanel.setStretch(this.response.widget, 3);
    }
    get sqlStatementValue() {
        return this.editor.value;
    }
    get sqlStatementChanged() {
        return this._sqlStatementChanged;
    }
    get executionStarted() {
        return this._executionStarted;
    }
    get executionFinished() {
        return this._executionFinished;
    }
    onActivateRequest(_) {
        this.editor.widget.activate();
    }
    async updateGrid(connectionUrl, sql) {
        this._executionStarted.emit(void 0);
        const thisRequestId = uuid__WEBPACK_IMPORTED_MODULE_0__.v4();
        this._lastRequestId = thisRequestId;
        const data = await _api__WEBPACK_IMPORTED_MODULE_9__.getForQuery(connectionUrl, sql);
        if (this._lastRequestId === thisRequestId) {
            // Only update the response widget if the current
            // query is the last query that was dispatched.
            this.response.setResponse(data);
            this._executionFinished.emit(void 0);
        }
    }
}


/***/ }),

/***/ "./lib/query/response.js":
/*!*******************************!*\
  !*** ./lib/query/response.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Response": () => (/* binding */ Response),
/* harmony export */   "ResponseWidget": () => (/* binding */ ResponseWidget)
/* harmony export */ });
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../components */ "./lib/components/SingletonPanel.js");
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components */ "./lib/components/ResultsTable.js");
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../components */ "./lib/components/PreWidget.js");
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../api */ "./lib/api/query.js");


class Response {
    constructor() {
        this._widget = new ResponseWidget();
    }
    get widget() {
        return this._widget;
    }
    setResponse(response) {
        this._widget.setResponse(response);
    }
}
class ResponseWidget extends _components__WEBPACK_IMPORTED_MODULE_0__.SingletonPanel {
    constructor() {
        super(...arguments);
        this._table = null;
    }
    dispose() {
        if (this._table) {
            this._table.dispose();
        }
        super.dispose();
    }
    setResponse(response) {
        this._disposeTable();
        _api__WEBPACK_IMPORTED_MODULE_1__.ResponseModel.match(response, (keys, rows) => {
            const table = new _components__WEBPACK_IMPORTED_MODULE_2__.ResultsTable(keys, rows);
            this._table = table;
            this.widget = table.widget;
        }, () => {
            const message = 'Command executed successfully';
            this.widget = new _components__WEBPACK_IMPORTED_MODULE_3__.PreWidget(message);
        }, ({ message }) => {
            this.widget = new _components__WEBPACK_IMPORTED_MODULE_3__.PreWidget(message);
        });
    }
    _disposeTable() {
        if (this._table) {
            this._table.dispose();
        }
        this._table = null;
    }
}


/***/ }),

/***/ "./lib/query/toolbar.js":
/*!******************************!*\
  !*** ./lib/query/toolbar.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "QueryToolbar": () => (/* binding */ QueryToolbar)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components */ "./lib/components/ToolbarItems.js");



class QueryToolbar extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Toolbar {
    constructor(connectionUrl) {
        super();
        this._loadingIcon = new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.LoadingIcon();
        this._backButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._onBackButtonClicked = this._onBackButtonClicked.bind(this);
        this.addItem('back', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.BackButton({ onClick: this._onBackButtonClicked }));
        this.addItem('spacer', _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Toolbar.createSpacerItem());
        this.addItem('url', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.ConnectionUrlItem(connectionUrl));
        this.addItem('loading', this._loadingIcon);
    }
    get backButtonClicked() {
        return this._backButtonClicked;
    }
    _onBackButtonClicked() {
        this._backButtonClicked.emit(void 0);
    }
    setLoading(isLoading) {
        this._loadingIcon.setLoading(isLoading);
    }
}


/***/ }),

/***/ "./lib/services/connectionUrl.js":
/*!***************************************!*\
  !*** ./lib/services/connectionUrl.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ConnectionUrl": () => (/* binding */ ConnectionUrl)
/* harmony export */ });
/* harmony import */ var url_parse__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! url-parse */ "./node_modules/url-parse/index.js");
/* harmony import */ var url_parse__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(url_parse__WEBPACK_IMPORTED_MODULE_0__);

var ConnectionUrl;
(function (ConnectionUrl) {
    function sanitize(url) {
        const parsedUrl = url_parse__WEBPACK_IMPORTED_MODULE_0___default()(url);
        const { password } = parsedUrl;
        if (password && password !== '') {
            parsedUrl.set('password', '•••••••');
        }
        return parsedUrl.href;
    }
    ConnectionUrl.sanitize = sanitize;
})(ConnectionUrl || (ConnectionUrl = {}));


/***/ }),

/***/ "./lib/services/dataGridExtensions/columnWidth.js":
/*!********************************************************!*\
  !*** ./lib/services/dataGridExtensions/columnWidth.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "FitColumnWidths": () => (/* binding */ FitColumnWidths),
/* harmony export */   "fitColumnWidths": () => (/* binding */ fitColumnWidths)
/* harmony export */ });
/* harmony import */ var _fontWidth__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./fontWidth */ "./lib/services/dataGridExtensions/fontWidth.js");

function fitColumnWidths(grid, renderer, options = {}) {
    const estimator = new ColumnWidthEstimator(grid.dataModel, renderer, options);
    const widths = estimator.getColumnWidths();
    widths.forEach((width, column) => {
        grid.resizeColumn('body', column, width);
    });
    const headerWidth = estimator.getRowHeaderWidth();
    grid.resizeColumn('row-header', 0, headerWidth);
}
var FitColumnWidths;
(function (FitColumnWidths) {
    FitColumnWidths.defaultRowsToInspect = 100;
    FitColumnWidths.defaultMinWidth = 40;
    FitColumnWidths.defaultMaxWidth = 300;
    FitColumnWidths.characterScaleFactor = 0.65;
})(FitColumnWidths || (FitColumnWidths = {}));
class ColumnWidthEstimator {
    constructor(model, renderer, options = {}) {
        this._model = model;
        this._renderer = renderer;
        this._rowsToInspect =
            options.rowsToInspect || FitColumnWidths.defaultRowsToInspect;
        this._minWidth = options.minWidth || FitColumnWidths.defaultMinWidth;
        this._maxWidth = options.maxWidth || FitColumnWidths.defaultMaxWidth;
        this._characterScaleFactor =
            options.characterScaleFactor || FitColumnWidths.characterScaleFactor;
    }
    getColumnWidths() {
        const numberColumns = this._model.columnCount('body');
        const widths = Array.from({ length: numberColumns }, (_, column) => this._getColumnWidth(column));
        return widths;
    }
    getRowHeaderWidth() {
        if (this._model.columnCount('row-header') !== 1) {
            throw new Error('Unsupported grid: row header does not contain exactly one column');
        }
        const headerData = this._getDataFromRegion('corner-header', 0);
        const bodyData = this._getDataFromRegion('row-header', 0);
        const width = this._measureArrayWidth([...headerData, ...bodyData]);
        return this._clampWidth(width);
    }
    _getColumnWidth(column) {
        const headerData = this._getDataFromRegion('column-header', column);
        const bodyData = this._getDataFromRegion('body', column);
        const width = this._measureArrayWidth([...headerData, ...bodyData]);
        return this._clampWidth(width);
    }
    _getDataFromRegion(region, column) {
        const rowsToCheck = Math.min(this._getRowCount(region), this._rowsToInspect);
        const data = Array.from({ length: rowsToCheck }, (_, idx) => this._model.data(region, idx, column));
        return data;
    }
    _measureArrayWidth(content) {
        const widths = content.map(elementContent => this._measureElementWidth(elementContent));
        if (widths.length === 0) {
            return 0;
        }
        else {
            return Math.max(...widths);
        }
    }
    _measureElementWidth(content) {
        const config = {
            x: 1,
            y: 1,
            height: 100,
            width: 20,
            region: 'body',
            row: 10,
            column: 10,
            metadata: {},
            value: content
        };
        const rendered = this._renderer.format(config);
        const width = (0,_fontWidth__WEBPACK_IMPORTED_MODULE_0__.getFontWidth)('12px sans-serif');
        return rendered.length * width * this._characterScaleFactor;
    }
    _getRowCount(region) {
        if (region === 'corner-header' || region === 'column-header') {
            return this._model.rowCount('column-header');
        }
        else if (region === 'body' || region === 'row-header') {
            return this._model.rowCount('body');
        }
        else {
            throw 'unreachable';
        }
    }
    _clampWidth(width) {
        return Math.max(Math.min(width, this._maxWidth), this._minWidth);
    }
}


/***/ }),

/***/ "./lib/services/dataGridExtensions/events.js":
/*!***************************************************!*\
  !*** ./lib/services/dataGridExtensions/events.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "addMouseEventListener": () => (/* binding */ addMouseEventListener)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);

function addMouseEventListener(eventType, grid, listener) {
    const handler = (rawEvent) => {
        const { clientX, clientY } = rawEvent;
        const row = getRow(grid, clientY);
        const column = getColumn(grid, clientX);
        return listener({ row, column, rawEvent });
    };
    grid.node.addEventListener(eventType, handler);
    return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
        grid.node.removeEventListener(eventType, handler);
    });
}
function getRow(grid, clientY) {
    const { top } = grid.node.getBoundingClientRect();
    const y = clientY - top;
    let section;
    let index;
    if (y >= grid.totalHeight) {
        section = 'outside';
        index = null;
    }
    else if (y < grid.headerHeight) {
        section = 'column-header';
        index = null;
    }
    else {
        const absY = y + grid.scrollY - grid.headerHeight;
        let currentRow = 0;
        let currentTop = 0;
        let nextTop = currentTop + grid.rowSize('body', currentRow);
        while (absY >= nextTop) {
            currentRow++;
            currentTop = nextTop;
            nextTop = currentTop + grid.rowSize('body', currentRow);
        }
        index = currentRow;
        section = 'row';
    }
    return { section, index };
}
function getColumn(grid, clientX) {
    const { left } = grid.node.getBoundingClientRect();
    const x = clientX - left;
    let section = 'row-header';
    let index = null;
    if (x >= grid.totalWidth) {
        section = 'outside';
        index = null;
    }
    else if (x < grid.headerWidth) {
        section = 'row-header';
        index = null;
    }
    else {
        const absX = x + grid.scrollX - grid.headerWidth;
        let currentColumn = 0;
        let currentLeft = 0;
        let nextLeft = currentLeft + grid.columnSize('body', currentColumn);
        while (absX >= nextLeft) {
            currentColumn++;
            currentLeft = nextLeft;
            nextLeft = currentLeft + grid.columnSize('body', currentColumn);
        }
        index = currentColumn;
        section = 'column';
    }
    return { section, index };
}


/***/ }),

/***/ "./lib/services/dataGridExtensions/fontWidth.js":
/*!******************************************************!*\
  !*** ./lib/services/dataGridExtensions/fontWidth.js ***!
  \******************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "getFontWidth": () => (/* binding */ getFontWidth)
/* harmony export */ });
/*
 * Measure the width of an M for that font.
 */
function getFontWidth(font) {
    let width = Private.fontWidthCache[font];
    if (width !== undefined) {
        return width;
    }
    // Normalize the font.
    Private.fontMeasurementGC.font = font;
    const normFont = Private.fontMeasurementGC.font;
    // Set the font on the measurement node.
    Private.fontMeasurementNode.style.font = normFont;
    // Add the measurement node to the document.
    document.body.appendChild(Private.fontMeasurementNode);
    // Measure the node height.
    width = Private.fontMeasurementNode.offsetWidth;
    // Remove the measurement node from the document.
    document.body.removeChild(Private.fontMeasurementNode);
    // Cache the measured height for the font and norm font.
    Private.fontWidthCache[font] = width;
    Private.fontWidthCache[normFont] = width;
    // Return the measured height.
    return width;
}
/**
 * The namespace for the module implementation details.
 */
var Private;
(function (Private) {
    /**
     * A cache of measured font heights.
     */
    Private.fontWidthCache = Object.create(null);
    /**
     * The DOM node used for font height measurement.
     */
    Private.fontMeasurementNode = (() => {
        const node = document.createElement('div');
        node.style.position = 'absolute';
        node.style.top = '-99999px';
        node.style.left = '-99999px';
        node.style.visibility = 'hidden';
        node.textContent = 'M';
        return node;
    })();
    /**
     * The GC used for font measurement.
     */
    Private.fontMeasurementGC = (() => {
        const canvas = document.createElement('canvas');
        canvas.width = 0;
        canvas.height = 0;
        return canvas.getContext('2d');
    })();
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/services/dataGridExtensions/selectionManager.js":
/*!*************************************************************!*\
  !*** ./lib/services/dataGridExtensions/selectionManager.js ***!
  \*************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "SelectionManager": () => (/* binding */ SelectionManager)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

class SelectionManager {
    constructor(model) {
        this._selection = null;
        this._selectionChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._maxRow = model.rowCount('body') - 1;
        this._maxColumn = model.columnCount('body') - 1;
    }
    set selection(value) {
        let newSelection = value;
        if (value !== null) {
            const { rowIndex, columnIndex } = value;
            if (rowIndex > this._maxRow ||
                columnIndex > this._maxColumn ||
                rowIndex < 0 ||
                columnIndex < 0) {
                newSelection = null;
            }
        }
        if (newSelection === this._selection) {
            return;
        }
        this._selection = newSelection;
        this._selectionChanged.emit(value);
    }
    get selection() {
        return this._selection;
    }
    get selectionChanged() {
        return this._selectionChanged;
    }
}


/***/ }),

/***/ "./lib/services/signalConnector.js":
/*!*****************************************!*\
  !*** ./lib/services/signalConnector.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "proxyFor": () => (/* binding */ proxyFor)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

function proxyFor(source, thisArg) {
    const destinationSignal = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(thisArg);
    source.connect((_, arg) => {
        destinationSignal.emit(arg);
    });
    return destinationSignal;
}


/***/ }),

/***/ "./lib/tableSummary/index.js":
/*!***********************************!*\
  !*** ./lib/tableSummary/index.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TableSummaryPage": () => (/* binding */ TableSummaryPage)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components */ "./lib/components/SingletonPanel.js");
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../components */ "./lib/components/ResultsTable.js");
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../components */ "./lib/components/PreWidget.js");
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../api */ "./lib/api/tableStructure.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../page */ "./lib/page.js");
/* harmony import */ var _services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../services */ "./lib/services/signalConnector.js");
/* harmony import */ var _toolbar__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./toolbar */ "./lib/tableSummary/toolbar.js");







class TableSummaryPage {
    constructor(options) {
        this.pageName = _page__WEBPACK_IMPORTED_MODULE_2__.PageName.TableSummary;
        this._onRefresh = this._onRefresh.bind(this);
        this._content = new Content(options);
        this._toolbar = new _toolbar__WEBPACK_IMPORTED_MODULE_3__.TableSummaryToolbar(options.connectionUrl, options.tableName);
        this._navigateBack = (0,_services__WEBPACK_IMPORTED_MODULE_4__.proxyFor)(this._toolbar.backButtonClicked, this);
        this._toolbar.refreshButtonClicked.connect(this._onRefresh);
        this._disposables = _lumino_disposable__WEBPACK_IMPORTED_MODULE_1__.DisposableSet.from([this._content, this._toolbar]);
        this._onRefresh();
    }
    get content() {
        return this._content;
    }
    get toolbar() {
        return this._toolbar;
    }
    get navigateBack() {
        return this._navigateBack;
    }
    get isDisposed() {
        return this._disposables.isDisposed;
    }
    dispose() {
        return this._disposables.dispose();
    }
    async _onRefresh() {
        this._toolbar.setLoading(true);
        await this._content.refresh();
        this._toolbar.setLoading(false);
    }
}
class Content extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxPanel {
    constructor(options) {
        super();
        this._connectionUrl = options.connectionUrl;
        this._tableName = options.tableName;
        this._responseWidget = new ResponseWidget();
        this.addWidget(this._responseWidget);
    }
    async refresh() {
        const response = await _api__WEBPACK_IMPORTED_MODULE_5__.getTableStructure(this._connectionUrl, this._tableName);
        this._responseWidget.setResponse(response);
    }
}
class ResponseWidget extends _components__WEBPACK_IMPORTED_MODULE_6__.SingletonPanel {
    constructor() {
        super(...arguments);
        this._table = null;
    }
    dispose() {
        this._disposeTable();
        super.dispose();
    }
    setResponse(response) {
        this._disposeTable();
        _api__WEBPACK_IMPORTED_MODULE_5__.TableStructureResponse.match(response, (keys, rows) => {
            this._table = new _components__WEBPACK_IMPORTED_MODULE_7__.ResultsTable(keys, rows);
            this.widget = this._table.widget;
        }, ({ message }) => {
            this.widget = new _components__WEBPACK_IMPORTED_MODULE_8__.PreWidget(message);
        });
    }
    _disposeTable() {
        if (this._table) {
            this._table.dispose();
        }
        this._table = null;
    }
}


/***/ }),

/***/ "./lib/tableSummary/toolbar.js":
/*!*************************************!*\
  !*** ./lib/tableSummary/toolbar.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TableSummaryToolbar": () => (/* binding */ TableSummaryToolbar)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components */ "./lib/components/ToolbarItems.js");



class TableSummaryToolbar extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar {
    constructor(connectionUrl, tableName) {
        super();
        this._loadingIcon = new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.LoadingIcon();
        this._backButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._refreshButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._onBackButtonClicked = this._onBackButtonClicked.bind(this);
        this._onRefreshButtonClicked = this._onRefreshButtonClicked.bind(this);
        this.addItem('back', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.BackButton({ onClick: this._onBackButtonClicked }));
        this.addItem('refresh', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.RefreshButton({ onClick: this._onRefreshButtonClicked }));
        this.addItem('spacer', _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar.createSpacerItem());
        this.addItem('url', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.ConnectionUrlItem(connectionUrl));
        this.addItem('table', new _components__WEBPACK_IMPORTED_MODULE_2__.ToolbarItems.TextItem(` ❯ ${tableName}`));
        this.addItem('loading', this._loadingIcon);
    }
    get backButtonClicked() {
        return this._backButtonClicked;
    }
    get refreshButtonClicked() {
        return this._refreshButtonClicked;
    }
    setLoading(isLoading) {
        this._loadingIcon.setLoading(isLoading);
    }
    _onBackButtonClicked() {
        this._backButtonClicked.emit(void 0);
    }
    _onRefreshButtonClicked() {
        this._refreshButtonClicked.emit(void 0);
    }
}


/***/ }),

/***/ "./lib/tracker.js":
/*!************************!*\
  !*** ./lib/tracker.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "createTracker": () => (/* binding */ createTracker)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);

function createTracker() {
    const namespace = 'jupyterlab-sql';
    const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.WidgetTracker({
        namespace
    });
    tracker.widgetAdded.connect((_, widget) => {
        widget.pageChanged.connect(() => {
            tracker.save(widget);
        });
        widget.connectionUrlChanged.connect(() => {
            tracker.save(widget);
        });
        widget.tableNameChanged.connect(() => {
            tracker.save(widget);
        });
        widget.sqlStatementChanged.connect(() => {
            tracker.save(widget);
        });
    });
    return tracker;
}


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "JupyterLabSqlWidget": () => (/* binding */ JupyterLabSqlWidget)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components */ "./lib/components/SingletonPanel.js");
/* harmony import */ var _query__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./query */ "./lib/query/index.js");
/* harmony import */ var _connection__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./connection */ "./lib/connection/index.js");
/* harmony import */ var _databaseSummary__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./databaseSummary */ "./lib/databaseSummary/index.js");
/* harmony import */ var _tableSummary__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./tableSummary */ "./lib/tableSummary/index.js");
/* harmony import */ var _page__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./page */ "./lib/page.js");








class JupyterLabSqlWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(editorFactory, options) {
        super();
        this._toolbar = null;
        this._sqlStatement = '';
        this._page = null;
        this._pageChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._connectionUrlChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._tableNameChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._sqlStatementChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this.addClass('jp-MainAreaWidget');
        this.id = 'jupyterlab-sql';
        this._configureTitle();
        this.content = new _components__WEBPACK_IMPORTED_MODULE_2__.SingletonPanel();
        this.layout = this._createWidgetLayout();
        this.name = options.name;
        this.pageName = options.pageName;
        this._connectionUrl = options.connectionUrl;
        this._tableName = options.tableName;
        this._sqlStatement = options.sqlStatement;
        this.editorFactory = editorFactory;
        this._setInitialPage();
    }
    get connectionUrl() {
        return this._connectionUrl;
    }
    get tableName() {
        return this._tableName;
    }
    get sqlStatement() {
        return this._sqlStatement;
    }
    get pageChanged() {
        return this._pageChanged;
    }
    get connectionUrlChanged() {
        return this._connectionUrlChanged;
    }
    get tableNameChanged() {
        return this._tableNameChanged;
    }
    get sqlStatementChanged() {
        return this._sqlStatementChanged;
    }
    onActivateRequest() {
        this._focusContent();
    }
    onCloseRequest() {
        this.dispose();
    }
    _createWidgetLayout() {
        const layout = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxLayout({ spacing: 0, direction: 'top-to-bottom' });
        _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxLayout.setStretch(this.content, 1);
        layout.addWidget(this.content);
        this.content.node.tabIndex = -1;
        return layout;
    }
    _configureTitle() {
        this.title.label = 'SQL';
        this.title.closable = true;
    }
    _setInitialPage() {
        if (this.pageName === _page__WEBPACK_IMPORTED_MODULE_3__.PageName.Connection) {
            this._loadConnectionPage();
        }
        else if (this.pageName === _page__WEBPACK_IMPORTED_MODULE_3__.PageName.DatabaseSummary) {
            this._loadSummaryPage();
        }
        else if (this.pageName === _page__WEBPACK_IMPORTED_MODULE_3__.PageName.TableSummary) {
            this._loadTableSummaryPage();
        }
        else {
            this._loadQueryPage();
        }
    }
    set toolbar(newToolbar) {
        this._toolbar = newToolbar;
        _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.BoxLayout.setStretch(this._toolbar, 0);
        this.layout.insertWidget(0, this._toolbar);
    }
    set page(newPage) {
        const oldPage = this._page;
        if (oldPage !== newPage) {
            this.content.widget = newPage.content;
            this.toolbar = newPage.toolbar;
            this.pageName = newPage.pageName;
            this._page = newPage;
            this._pageChanged.emit(void 0);
            if (oldPage !== null) {
                oldPage.dispose();
            }
            this.content.activate();
        }
    }
    _setConnectionUrl(newConnectionUrl) {
        if (newConnectionUrl !== this._connectionUrl) {
            this._connectionUrl = newConnectionUrl;
            this._connectionUrlChanged.emit(this._connectionUrl);
        }
    }
    _setTableName(newTableName) {
        if (newTableName !== this._tableName) {
            this._tableName = newTableName;
            this._tableNameChanged.emit(this._tableName);
        }
    }
    _setSqlStatement(newStatement) {
        if (newStatement !== this._sqlStatement) {
            this._sqlStatement = newStatement;
            this._sqlStatementChanged.emit(this._sqlStatement);
        }
    }
    _loadConnectionPage() {
        const initialConnectionString = this._connectionUrl;
        const page = new _connection__WEBPACK_IMPORTED_MODULE_4__.ConnectionPage({
            initialConnectionString
        });
        page.connectDatabase.connect((_, connectionUrl) => {
            this._setConnectionUrl(connectionUrl);
            this._loadSummaryPage();
        });
        page.connectionUrlChanged.connect((_, connectionUrl) => {
            this._setConnectionUrl(connectionUrl);
        });
        this.page = page;
    }
    _loadSummaryPage() {
        const connectionUrl = this._connectionUrl;
        const page = new _databaseSummary__WEBPACK_IMPORTED_MODULE_5__.DatabaseSummaryPage({ connectionUrl });
        page.customQueryClicked.connect(() => {
            this._loadQueryPage();
        });
        page.navigateToTable.connect((_, tableName) => {
            this._setTableName(tableName);
            this._loadTableSummaryPage();
        });
        page.navigateBack.connect(() => {
            this._loadConnectionPage();
        });
        this.page = page;
    }
    _loadQueryPage() {
        const options = {
            connectionUrl: this._connectionUrl,
            initialSqlStatement: this._sqlStatement,
            editorFactory: this.editorFactory
        };
        const page = new _query__WEBPACK_IMPORTED_MODULE_6__.QueryPage(options);
        page.backButtonClicked.connect(() => {
            this._loadSummaryPage();
        });
        page.sqlStatementChanged.connect((_, newStatement) => {
            this._setSqlStatement(newStatement);
        });
        this.page = page;
    }
    _loadTableSummaryPage() {
        const tableName = this._tableName;
        const connectionUrl = this._connectionUrl;
        const page = new _tableSummary__WEBPACK_IMPORTED_MODULE_7__.TableSummaryPage({ connectionUrl, tableName });
        page.navigateBack.connect(() => {
            this._loadSummaryPage();
        });
        this.page = page;
    }
    /**
     * Give focus to the content.
     */
    _focusContent() {
        // Focus the content node if we aren't already focused on it or a
        // descendent.
        if (!this.content.node.contains(document.activeElement)) {
            this.content.node.focus();
        }
        // Activate the content asynchronously (which may change the focus).
        this.content.activate();
    }
}


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, "/*\n    See the JupyterLab Developer Guide for useful CSS Patterns:\n\n    https://jupyterlab.readthedocs.io/en/stable/developer/css.html\n*/\n", "",{"version":3,"sources":["webpack://./style/base.css"],"names":[],"mappings":"AAAA;;;;CAIC","sourcesContent":["/*\n    See the JupyterLab Developer Guide for useful CSS Patterns:\n\n    https://jupyterlab.readthedocs.io/en/stable/developer/css.html\n*/\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!***************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \***************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/getUrl.js */ "./node_modules/css-loader/dist/runtime/getUrl.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _icons_database_svg__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./icons/database.svg */ "./style/icons/database.svg");
/* harmony import */ var _icons_database_svg__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_icons_database_svg__WEBPACK_IMPORTED_MODULE_4__);
// Imports





var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
var ___CSS_LOADER_URL_REPLACEMENT_0___ = _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_3___default()((_icons_database_svg__WEBPACK_IMPORTED_MODULE_4___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, ".p-Sql-MainContainer {\n  padding-left: 10px;\n  padding-right: 10px;\n  padding-top: 10px;\n}\n\n.p-Sql-ConnectionInformation-container {\n  top: 20%;\n  position: absolute;\n  width: 100%;\n}\n\n.p-Sql-ConnectionInformation-wrapper {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  height: 50px;\n}\n\n.p-Sql-ConnectionInformation-input-wrapper {\n  height: 30px;\n  border: 1px solid var(--jp-border-color0);\n  display: inline-block;\n  vertical-align: middle;\n  padding-left: 8px;\n  padding-right: 8px;\n  flex: 1 1 auto;\n}\n\n.p-Sql-ConnectionInformation-input-wrapper.p-mod-focused {\n  border: 1px solid var(--md-blue-500);\n  box-shadow: inset 0 0 4px var(--md-blue-300);\n}\n\n.p-Sql-ConnectionInformation-text {\n  font-size: var(--jp-ui-font-size1);\n  height: 28px;\n  line-height: 28px;\n  color: var(--jp-ui-font-color1);\n  font-weight: 400;\n  overflow: hidden;\n}\n\n.p-Sql-ConnectionInformation-input {\n  padding: 0;\n  border: 0;\n  width: 100%;\n  background: transparent;\n}\n\n.p-Sql-ConnectionInformation-input:focus {\n  outline: none;\n}\n\n.p-Sql-ConnectionInformation-container summary:focus {\n  outline: none;\n}\n\n.p-Sql-Editor {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);\n  border-radius: 0;\n  background: var(--jp-cell-editor-background);\n}\n\n.p-Sql-Editor .CodeMirror {\n  background: transparent;\n}\n\n.p-Sql-Editor.jp-mod-focused {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-active-border-color);\n  background: var(--jp-cell-editor-active-background);\n  box-shadow: var(--jp-input-box-shadow);\n}\n\n.p-Sql-DatabaseIcon {\n  background-image: url(" + ___CSS_LOADER_URL_REPLACEMENT_0___ + ");\n}\n\n.p-Sql-DatabaseSummary-Container {\n  overflow: auto;\n}\n\n.p-Sql-TableList-container {\n  padding-left: 10px;\n  padding-right: 10px;\n  margin-top: 10px;\n}\n\n.p-Sql-TableList-content {\n  font-family: var(--jp-ui-font-family);\n  font-size: var(--jp-ui-font-size1);\n  margin: 0;\n  padding: 0;\n  list-style-type: none;\n  background-color: var(--jp-layout-color1);\n}\n\n.p-Sql-TableList-header {\n  padding: 8px 0 8px 12px;\n  color: var(--jp-ui-font-color1);\n  font-size: var(--jp-ui-font-size0);\n  font-weight: 600;\n  text-transform: uppercase;\n  border-bottom: solid var(--jp-border-width) var(--jp-border-color2);\n  letter-spacing: 1px;\n}\n\n.jp-Toolbar-item.p-Sql-Toolbar-text {\n  line-height: 24px;\n  text-align: center;\n}\n", "",{"version":3,"sources":["webpack://./style/index.css"],"names":[],"mappings":"AAEA;EACE,kBAAkB;EAClB,mBAAmB;EACnB,iBAAiB;AACnB;;AAEA;EACE,QAAQ;EACR,kBAAkB;EAClB,WAAW;AACb;;AAEA;EACE,aAAa;EACb,mBAAmB;EACnB,8BAA8B;EAC9B,YAAY;AACd;;AAEA;EACE,YAAY;EACZ,yCAAyC;EACzC,qBAAqB;EACrB,sBAAsB;EACtB,iBAAiB;EACjB,kBAAkB;EAClB,cAAc;AAChB;;AAEA;EACE,oCAAoC;EACpC,4CAA4C;AAC9C;;AAEA;EACE,kCAAkC;EAClC,YAAY;EACZ,iBAAiB;EACjB,+BAA+B;EAC/B,gBAAgB;EAChB,gBAAgB;AAClB;;AAEA;EACE,UAAU;EACV,SAAS;EACT,WAAW;EACX,uBAAuB;AACzB;;AAEA;EACE,aAAa;AACf;;AAEA;EACE,aAAa;AACf;;AAEA;EACE,uEAAuE;EACvE,gBAAgB;EAChB,4CAA4C;AAC9C;;AAEA;EACE,uBAAuB;AACzB;;AAEA;EACE,8EAA8E;EAC9E,mDAAmD;EACnD,sCAAsC;AACxC;;AAEA;EACE,yDAA6C;AAC/C;;AAEA;EACE,cAAc;AAChB;;AAEA;EACE,kBAAkB;EAClB,mBAAmB;EACnB,gBAAgB;AAClB;;AAEA;EACE,qCAAqC;EACrC,kCAAkC;EAClC,SAAS;EACT,UAAU;EACV,qBAAqB;EACrB,yCAAyC;AAC3C;;AAEA;EACE,uBAAuB;EACvB,+BAA+B;EAC/B,kCAAkC;EAClC,gBAAgB;EAChB,yBAAyB;EACzB,mEAAmE;EACnE,mBAAmB;AACrB;;AAEA;EACE,iBAAiB;EACjB,kBAAkB;AACpB","sourcesContent":["@import url('base.css');\n\n.p-Sql-MainContainer {\n  padding-left: 10px;\n  padding-right: 10px;\n  padding-top: 10px;\n}\n\n.p-Sql-ConnectionInformation-container {\n  top: 20%;\n  position: absolute;\n  width: 100%;\n}\n\n.p-Sql-ConnectionInformation-wrapper {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  height: 50px;\n}\n\n.p-Sql-ConnectionInformation-input-wrapper {\n  height: 30px;\n  border: 1px solid var(--jp-border-color0);\n  display: inline-block;\n  vertical-align: middle;\n  padding-left: 8px;\n  padding-right: 8px;\n  flex: 1 1 auto;\n}\n\n.p-Sql-ConnectionInformation-input-wrapper.p-mod-focused {\n  border: 1px solid var(--md-blue-500);\n  box-shadow: inset 0 0 4px var(--md-blue-300);\n}\n\n.p-Sql-ConnectionInformation-text {\n  font-size: var(--jp-ui-font-size1);\n  height: 28px;\n  line-height: 28px;\n  color: var(--jp-ui-font-color1);\n  font-weight: 400;\n  overflow: hidden;\n}\n\n.p-Sql-ConnectionInformation-input {\n  padding: 0;\n  border: 0;\n  width: 100%;\n  background: transparent;\n}\n\n.p-Sql-ConnectionInformation-input:focus {\n  outline: none;\n}\n\n.p-Sql-ConnectionInformation-container summary:focus {\n  outline: none;\n}\n\n.p-Sql-Editor {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);\n  border-radius: 0;\n  background: var(--jp-cell-editor-background);\n}\n\n.p-Sql-Editor .CodeMirror {\n  background: transparent;\n}\n\n.p-Sql-Editor.jp-mod-focused {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-active-border-color);\n  background: var(--jp-cell-editor-active-background);\n  box-shadow: var(--jp-input-box-shadow);\n}\n\n.p-Sql-DatabaseIcon {\n  background-image: url('./icons/database.svg');\n}\n\n.p-Sql-DatabaseSummary-Container {\n  overflow: auto;\n}\n\n.p-Sql-TableList-container {\n  padding-left: 10px;\n  padding-right: 10px;\n  margin-top: 10px;\n}\n\n.p-Sql-TableList-content {\n  font-family: var(--jp-ui-font-family);\n  font-size: var(--jp-ui-font-size1);\n  margin: 0;\n  padding: 0;\n  list-style-type: none;\n  background-color: var(--jp-layout-color1);\n}\n\n.p-Sql-TableList-header {\n  padding: 8px 0 8px 12px;\n  color: var(--jp-ui-font-color1);\n  font-size: var(--jp-ui-font-size0);\n  font-weight: 600;\n  text-transform: uppercase;\n  border-bottom: solid var(--jp-border-width) var(--jp-border-color2);\n  letter-spacing: 1px;\n}\n\n.jp-Toolbar-item.p-Sql-Toolbar-text {\n  line-height: 24px;\n  text-align: center;\n}\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./index.css */ "./node_modules/css-loader/dist/cjs.js!./style/index.css");

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"], options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"].locals || {});

/***/ }),

/***/ "./style/icons/database.svg":
/*!**********************************!*\
  !*** ./style/icons/database.svg ***!
  \**********************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3Csvg height='1024' width='768' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M384 960C171.969 960 0 902.625 0 832c0-38.625 0-80.875 0-128 0-11.125 5.562-21.688 13.562-32C56.375 727.125 205.25 768 384 768s327.625-40.875 370.438-96c8 10.312 13.562 20.875 13.562 32 0 37.062 0 76.375 0 128C768 902.625 596 960 384 960zM384 704C171.969 704 0 646.625 0 576c0-38.656 0-80.844 0-128 0-6.781 2.562-13.375 6-19.906l0 0C7.938 424 10.5 419.969 13.562 416 56.375 471.094 205.25 512 384 512s327.625-40.906 370.438-96c3.062 3.969 5.625 8 7.562 12.094l0 0c3.438 6.531 6 13.125 6 19.906 0 37.062 0 76.344 0 128C768 646.625 596 704 384 704zM384 448C171.969 448 0 390.656 0 320c0-20.219 0-41.594 0-64 0-20.344 0-41.469 0-64C0 121.34400000000005 171.969 64 384 64c212 0 384 57.344 384 128 0 19.969 0 41.156 0 64 0 19.594 0 40.25 0 64C768 390.656 596 448 384 448zM384 128c-141.375 0-256 28.594-256 64s114.625 64 256 64 256-28.594 256-64S525.375 128 384 128z'/%3E%3C/svg%3E"

/***/ })

}]);
//# sourceMappingURL=lib_index_js.af2355d778bcdf9c10c9.js.map