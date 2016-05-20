# -*- coding: utf-8 -*-
"""
PKMeter Configuration
"""
import json, keyring, os, shlex
from pkm import APPNAME, CONFIGPATH, SHAREDIR
from pkm import log, utils
from pkm.pkwidgets import PKWidget
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from xml.etree import ElementTree

NAMESPACE_ROLE = 99


class PKConfig(PKWidget):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'config.html')

    def __init__(self, pkmeter, parent=None):
        with open(self.TEMPLATE) as tmpl:
            template = ElementTree.fromstring(tmpl.read())
        PKWidget.__init__(self, template, self, parent)
        self.pkmeter = pkmeter                          # Save reference to pkmeter
        self._init_window()                             # Init ui window elements
        self.values = self.load()                       # Active configuration values
        self.listitems = []                             # List of items in the sidebar
        self.datatable = self._init_datatable()         # Init reusable data table
        self.pconfigs = self._init_pconfigs()           # Reference to each plugin config
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)

    def _init_window(self):
        # Load core stylesheet
        stylepath = os.path.join(SHAREDIR, 'pkmeter.css')
        with open(stylepath) as handle:
            self.setStyleSheet(handle.read())
        # Init self properties
        self.setWindowTitle('PKMeter Preferences')
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('img:logo.png')))
        self.layout().setContentsMargins(10,10,10,10)
        # Init window elements
        self.manifest.tabbar.setExpanding(False)
        self.manifest.tabbar.addTab('Settings')
        self.manifest.tabbar.addTab('Data')
        self.manifest.contents.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding))
        self.manifest.tabbar.currentChanged.connect(self.load_tab)
        # Init the ListWidget
        listwidget = self.manifest.list
        for module in sorted(self.pkmeter.modules.values(), key=self._sortKey):
            if getattr(module, 'Plugin', None) or getattr(module, 'Config', None):
                item = QtWidgets.QListWidgetItem(utils.name(module), parent=listwidget, type=0)
                item.setData(NAMESPACE_ROLE, utils.namespace(module))
                listwidget.addItem(item)
        self.manifest.list.itemSelectionChanged.connect(self.load_tab)

    def _sortKey(self, module):
        name = utils.name(module).lower()
        return '__pkmeter' if name == 'pkmeter' else name

    def _init_datatable(self):
        template = ElementTree.fromstring("""
          <vframe>
            <hframe>
              <QLineEdit id='filter' name='input_xlarge' placeholder='Filter'/>
              <stretch/><pushbutton text='Refresh' click='refresh_datatable'/>
            </hframe>
            <vframe id='table'/>
          </vframe>""")
        # Build the datatable
        self.datatable_wrap = PKWidget(template, self)
        datatable = QtWidgets.QTableWidget(0, 3, parent=None)
        datatable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        datatable.setHorizontalHeaderLabels(['Variable', 'Value', 'Type   '])
        datatable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        datatable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        datatable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        datatable.horizontalHeader().resizeSection(0, 200)
        datatable.verticalHeader().setVisible(False)
        datatable.verticalHeader().setDefaultSectionSize(19)
        datatable.setParent(self.datatable_wrap)
        self.datatable_wrap.manifest.table.layout().addWidget(datatable)
        # Connect the filter input
        self.datatable_wrap.manifest.filter.textChanged.connect(self.filter_datatable)
        return datatable

    def _init_pconfigs(self):
        pconfigs = {}
        for module in filter(lambda m: getattr(m, 'Config', None), self.pkmeter.modules.values()):
            pconfig = module.Config(self.pkmeter, self)
            pconfigs[pconfig.namespace] = pconfig
        return pconfigs

    def btn_reset(self):
        for pconfig in self.pconfigs.values():
            for field in pconfig.fields.values():
                self._reset_field(pconfig, field)

    def _reset_field(self, pconfig, field, index=None):
        from_keyring = field.get('save_to_keyring', False)
        field.value = self.get(pconfig.namespace, field.name, field.get('default'), from_keyring)
        field.lastchecked = field.value
        if field.input: field.input.set_value(field.value)
        if field.status: field.status.setText('')
        if field.help: field.help.setText(field.help_default)

    def btn_apply(self):
        for pconfig in self.pconfigs.values():
            for field in pconfig.fields.values():
                self.set(pconfig.namespace, field.name, field.value)
        self.pkmeter.reload()
        self.save()

    def btn_save(self):
        for pconfig in self.pconfigs.values():
            for field in pconfig.fields.values():
                to_keyring = field.get('save_to_keyring', False)
                self.set(pconfig.namespace, field.name, field.value, to_keyring)
        self.pkmeter.reload()
        self.save()
        self.hide()

    def get(self, namespace, path, default=None, from_keyring=False):
        path = '%s.%s' % (namespace, path)
        if from_keyring:
            value = keyring.get_password(APPNAME, path)
        else:
            value = utils.rget(self.values, path)
        return value if value is not None else default

    def load(self):
        self.values = getattr(self, 'values', {})
        log.info('Loading config: %s' % CONFIGPATH)
        if os.path.isfile(CONFIGPATH):
            with open(CONFIGPATH, 'r') as handle:
                self.values.update(json.load(handle))
        return self.values

    def save(self):
        log.info('Saving config: %s' % CONFIGPATH)
        os.makedirs(os.path.dirname(CONFIGPATH), exist_ok=True)
        self.set('pkmeter', 'positions', [w.position() for w in self.pkmeter.widgets])
        with open(CONFIGPATH, 'w') as handle:
            json.dump(self.values, handle, indent=2, sort_keys=True)

    def set(self, namespace, path, value, to_keyring=False):
        path = '%s.%s' % (namespace, path)
        if to_keyring:
            keyring.set_password(APPNAME, path, value)
        else:
            utils.rset(self.values, path, value)

    def show(self):
        self.btn_reset()
        self.resize(*self.initsize)
        self.manifest.list.setCurrentRow(0)
        self.load_tab()
        PKWidget.show(self)

    def load_tab(self, index=None, refresh=False):
        self.manifest.tabbar.setTabText(0, '%s Settings' % self.manifest.list.currentItem().text())
        tab = self.manifest.tabbar.currentIndex()
        utils.remove_children(self.manifest.contents)
        self.load_tab_settings(refresh) if tab == 0 else self.load_tab_data(refresh)

    def load_tab_settings(self, refresh=False):
        namespace = self.manifest.list.currentItem().data(NAMESPACE_ROLE)
        pconfig = self.pconfigs.get(namespace)
        if not pconfig:
            return self.load_message('No configuration for this module.')
        for field in pconfig.fields.values():
            pconfig._validate(field, force=True)
        pconfig.setParent(self.manifest.contents)
        self.manifest.contents.layout().addWidget(pconfig)

    def load_tab_data(self, refresh=False):
        namespace = self.manifest.list.currentItem().data(NAMESPACE_ROLE)
        data = self.pkmeter.data.get(namespace, {})
        data = utils.flatten_datatree(data, namespace)
        if not data:
            return self.load_message('Data not available for this module.')
        self.datatable.setRowCount(len(data))
        for row in range(len(data)):
            for col in range(3):
                item = QtWidgets.QTableWidgetItem(data[row][col], 0)
                self.datatable.setItem(row, col, item)
        if not refresh:
            self.datatable_wrap.manifest.filter.setText('')
        else:
            self.filter_datatable()
        self.datatable_wrap.setParent(self.manifest.contents)
        self.manifest.contents.layout().addWidget(self.datatable_wrap)

    def filter_datatable(self, _=None):
        try:
            text = self.datatable_wrap.manifest.filter.text()
            searches = shlex.split(text.lower().strip())
        except:
            searches = text.lower().strip()
        for row in range(self.datatable.rowCount()):
            teststrs = []
            for col in range(self.datatable.columnCount()):
                teststrs.append(self.datatable.item(row, col).text().lower())
            teststr = '||'.join(teststrs)
            showit = True
            for search in searches:
                if ((search.startswith('-') and search[1:] in teststr) or
                   (not search.startswith('-') and search not in teststr)):
                    showit = False
            self.datatable.setRowHidden(row, not showit)

    def refresh_datatable(self, event):
        self.load_tab(1, refresh=True)

    def load_message(self, message):
        layout = self.manifest.contents.layout()
        layout.addWidget(QtWidgets.QLabel(message, parent=self.manifest.contents))
        layout.addStretch(1)
