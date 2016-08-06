#!/usr/bin/python
# -*- coding: utf-8 -*-

# * Copyright (c) 2014 Sven Brauch <mail@svenbrauch.de>                       *
# * Copyright (c) 2016 Benjamin Winkel <>                                     *
# *                                                                           *
# * This program is free software; you can redistribute it and/or             *
# * modify it under the terms of the GNU General Public License as            *
# * published by the Free Software Foundation; either version 2 of            *
# * the License, or (at your option) any later version.                       *
# *                                                                           *
# * This program is distributed in the hope that it will be useful,           *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of            *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             *
# * GNU General Public License for more details.                              *
# *                                                                           *
# * You should have received a copy of the GNU General Public License         *
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.     *

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sip
API_NAMES = [
    'QDate', 'QDateTime', 'QString', 'QTextStream',
    'QTime', 'QUrl', 'QVariant'
    ]
API_VERSION = 2
for name in API_NAMES:
    sip.setapi(name, API_VERSION)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import os
import sys
if sys.version_info >= (3, 0):
    from mainwindow_form3 import Ui_MainWindow
    from plotwindow_form3 import Ui_Dialog
else:
    from mainwindow_form import Ui_MainWindow
    from plotwindow_form import Ui_Dialog

from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )

from matplotlib.figure import Figure

from astropy.io import fits as pyfits
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

RAW_DATA_ROLE = Qt.UserRole + 1

FONT = {'family': 'sans', 'weight': 'normal', 'size': 8}

matplotlib.rc('font', **FONT)

PLOT_ACTIONS = [
    ('Plot selection', {}),
    ('Plot with points', {
        'marker': 'o', 'linestyle': 'none', 'markersize': 1
        }),
    ('Plot with dashed line', {'linestyle': 'dashed'}),
    ('Plot with thick line', {'linewidth': 3})
    ]


class MatplotlibCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super(MatplotlibCanvas, self).__init__(self.figure)

        self.reset()
        self.setParent(parent)
        super(MatplotlibCanvas, self).setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
            )
        super(MatplotlibCanvas, self).updateGeometry()

    def reset(self):

        self.figure.clf()
        self.change_layout('1x1')
        self.figure.canvas.draw()

    def change_layout(self, new_layout_string, active_index=1):

        self.figure.clf()
        self.figure_layout = [int(x) for x in new_layout_string.split('x')]
        self.layoutSize = self.figure_layout[0] * self.figure_layout[1]
        self.axes = self.figure.add_subplot(
            self.figure_layout[0], self.figure_layout[1], active_index
            )
        self.figure.canvas.draw()

    def select_subfigure(self, index):

        self.axes = self.figure.add_subplot(
            self.figure_layout[0], self.figure_layout[1], index
            )


class PlotWindow(QtGui.QDialog):

    def __init__(self, parent=None):

        super(PlotWindow, self).__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.canvas = MatplotlibCanvas(self)
        self.ui.plotContainer.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ui.plotContainer.addWidget(self.toolbar)

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(
            self.reset
            )
        self.ui.keepPrevious.clicked.connect(
            self.update_hold, Qt.QueuedConnection
            )
        self.ui.layoutCombo.currentIndexChanged.connect(
            self.on_layout_selected
            )
        self.ui.activeSubfigure.valueChanged.connect(
            self.canvas.select_subfigure
            )

        self.resize(800, 600)
        self.on_layout_selected(0)

        self.setWindowTitle('pyfv: plot selection')

    def reset(self):

        self.canvas.reset()
        self.ui.activeSubfigure.setValue(0)
        self.ui.activeSubfigure.setMaximum(1)
        self.ui.layoutCombo.setCurrentIndex(0)
        self.update_hold()

    def update_hold(self):

        self.canvas.axes.hold(self.ui.keepPrevious.isChecked())

    def on_layout_selected(self, index):

        self.canvas.change_layout(self.ui.layoutCombo.itemText(index))
        self.ui.activeSubfigure.setMaximum(self.canvas.layoutSize)
        self.ui.lockActiveSubfigure.setEnabled(self.canvas.layoutSize > 1)
        self.ui.subfigLabel.setEnabled(self.canvas.layoutSize > 1)
        self.ui.cycleSubfigures.setEnabled(self.canvas.layoutSize > 1)
        self.ui.activeSubfigure.setEnabled(self.canvas.layoutSize > 1)
        self.update_hold()

    def active_plot(self):

        ax = self.canvas.axes

        assert isinstance(ax, plt.Axes)

        return ax

    def make_next_subplot_current(self):

        if self.ui.lockActiveSubfigure.isChecked():
            return

        new = self.ui.activeSubfigure.value() + 1

        if new <= self.canvas.layoutSize:
            self.ui.activeSubfigure.setValue(new)
        elif self.ui.cycleSubfigures.isChecked():
            self.ui.activeSubfigure.setValue(1)


class FitsHeaderListModel(QtCore.QAbstractTableModel):

    def __init__(self, hdulist, parent=None):

        super(FitsHeaderListModel, self).__init__(parent)
        self.hdulist = hdulist

    def rowCount(self, parent):

        try:
            return len(self.hdulist)
        except AttributeError:
            return 0

    def columnCount(self, parent):

        return 2

    def hdu_entry_for_index(self, model_index):

        return self.hdulist[model_index.row()]

    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole and orientation == Qt.Horizontal:

            if section == 0:
                return 'Name'
            if section == 1:
                return 'Shape'

        if role == Qt.DisplayRole and orientation == Qt.Vertical:

            # zero indexing
            try:
                line = super(FitsHeaderListModel, self).headerData(
                    section, orientation, role
                    ).toInt()[0]
            except AttributeError:
                line = super(FitsHeaderListModel, self).headerData(
                    section, orientation, role
                    )

            return line - 1

        return super(FitsHeaderListModel, self).headerData(
            section, orientation, role
            )

    def data(self, index, role):

        if role == Qt.DisplayRole:

            entry = self.hdulist[index.row()]

            if index.column() == 0:
                return entry.name

            if index.column() == 1:
                try:
                    return '{}x{}'.format(len(entry.columns), len(entry.data))
                except AttributeError:
                    return '---'

        if role == Qt.ForegroundRole:

            if index.column() == 1:
                return QtGui.QColor('#8F8F8F')

            if index.column() == 0:
                entry = str(self.hdulist[index.row()].name)
                if entry.find('ARRAYDATA') != -1:
                    return QtGui.QColor('#880064')
                if entry.find('DATAPAR') != -1:
                    return QtGui.QColor('#007BE0')
                if entry.find('MONITOR') != -1:
                    return QtGui.QColor('#004D8C')
                if entry.find('SCAN') != -1:
                    return QtGui.QColor('#881900')

        if role == Qt.FontRole:

            if index.column() == 0:
                f = QtGui.QFont()
                f.setBold(True)
                return f


class FitsHeaderModel(QtCore.QAbstractTableModel):

    def __init__(self, hdu_entry, parent=None):

        super(FitsHeaderModel, self).__init__(parent)
        self.header = hdu_entry.header
        self.keys = list(self.header.keys())
        self.values = list(self.header.values())

        try:
            self.comments = list(self.header.comments)
        except AttributeError:
            self.comments = list()

    def rowCount(self, parent):

        return len(self.header)

    def columnCount(self, parent):

        return 3

    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole and orientation == Qt.Horizontal:

            if section == 0:
                return 'Key'
            if section == 1:
                return 'Value'
            if section == 2:
                return 'Comment'

        return super(FitsHeaderModel, self).headerData(
            section, orientation, role
            )

    def data(self, index, role):

        if role == Qt.DisplayRole:

            if index.column() == 0:
                return self.keys[index.row()]
            if index.column() == 1:
                return self.values[index.row()]
            if index.column() == 2:
                try:
                    return self.header.comments[
                        list(self.header.keys())[index.row()]
                        ]
                except AttributeError:
                    return str()

        if role == Qt.ForegroundRole:

            if index.column() == 1:
                return QtGui.QColor('#900059')
            if index.column() == 2:
                return QtGui.QColor('#8F8F8F')


class FitsDataModel(QtCore.QAbstractTableModel):

    def __init__(self, hdu_entry, parent=None):

        super(FitsDataModel, self).__init__(parent)
        self.fitsdata = hdu_entry.data

    def rowCount(self, parent):

        if self.fitsdata is not None:
            return len(self.fitsdata)

        return 0

    def columnCount(self, parent):

        if self.fitsdata is not None:
            return len(self.fitsdata.columns)

        return 0

    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole and orientation == Qt.Horizontal:

            item = self.fitsdata.columns[section]
            return '{} / {} [{}]'.format(item.name, item.format, item.unit)

        return super(FitsDataModel, self).headerData(
            section, orientation, role
            )

    def data(self, index, role):

        if role == Qt.DisplayRole:
            data = self.fitsdata[index.row()][index.column()]
            return str(data)

        if role == RAW_DATA_ROLE:
            return self.fitsdata[index.row()][index.column()]


class DataSortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent=None):

        super(DataSortFilterProxyModel, self).__init__(parent)
        self.str_columns = []
        self.filter_string = str()

    def filterAcceptsColumn(self, source_column, source_parent):

        return True

    def change_filter(self, new_filter):

        self.filter_string = new_filter
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):

        if not len(self.filter_string):
            return True

        sou_model = self.sourceModel()

        if len(self.str_columns) == 0:
            for column in range(
                    sou_model.columnCount(QtCore.QModelIndex())
                    ):
                index = sou_model.index(0, column, QtCore.QModelIndex())
                if isinstance(sou_model.data(index, RAW_DATA_ROLE), str):
                    self.str_columns.append(column)

        for column in self.str_columns:
            index = sou_model.index(source_row, column, source_parent)
            data = str(sou_model.data(index, RAW_DATA_ROLE))
            if data.find(self.filter_string) != -1:
                return True

        return False


class FitsViewer(QtGui.QMainWindow):

    def __init__(self, parent=None):

        super(FitsViewer, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.current_file = None
        self._do_read_settings = True

        self.file_model = QtGui.QFileSystemModel()

        if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
            components = sys.argv[1].split('/')
            start_dir = '/'.join(components[:-1])
            self.preselect_file = sys.argv[1]

        elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
            start_dir = sys.argv[1]
            self.preselect_file = None

        else:
            start_dir = os.getcwd()
            self.preselect_file = None

        if not os.path.isdir(start_dir):
            start_dir = os.getcwd()

        self.file_model.setRootPath(start_dir)
        self.file_model.setFilter(
            QtCore.QDir.Files | QtCore.QDir.Dirs | QtCore.QDir.NoDot
            )
        self.file_model.directoryLoaded.connect(self.on_dir_loaded)
        self.ui.files.setModel(self.file_model)

        self.ui.url.setText(start_dir)
        self.ui.url.textChanged.connect(self.on_path_changed)
        self.on_path_changed()
        self.ui.files.selectionModel().selectionChanged.connect(
            self.on_file_selected
            )

        self.ui.sections.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.ui.sections.verticalHeader().setDefaultSectionSize(20)
        self.ui.sections.setShowGrid(False)
        self.ui.header.setShowGrid(False)
        self.ui.sections.setStyleSheet('QTableView::item { padding: 25px }')
        self.ui.header.setStyleSheet('QTableView::item { padding: 8px }')
        self.ui.contents.setStyleSheet('QTableView::item { padding: 8px }')

        # self.ui.splitter.setSizes([200, 500])
        # self.ui.splitter_2.setSizes([200, 500])
        # self.ui.splitter_3.setSizes([200, 500])

        menu = QtGui.QMenu()

        for action_name, action_args in PLOT_ACTIONS:
            action = QtGui.QAction(action_name, menu)
            action.setProperty('args', action_args)
            action.triggered.connect(self.on_plot_selection_triggered)
            menu.addAction(action)
            if not self.ui.plotButton.defaultAction():
                self.ui.plotButton.setDefaultAction(action)

        self.ui.plotButton.setMenu(menu)
        self.ui.indicesCheckbox.toggled.connect(self.on_indices_toggled)

        self.ui.contents.pressed.connect(self.on_plot_selection_triggered)

        self.ui.filterHeader.textChanged.connect(self.on_header_filter_changed)
        self.ui.filterData.textChanged.connect(self.on_data_filter_changed)
        self.ui.filterFiles.textChanged.connect(self.on_files_filter_changed)
        self.ui.filterSections.textChanged.connect(
            self.on_hduList_filter_changed
            )
        self.ui.browseDirectoryButton.clicked.connect(
            self.on_browsedir_clicked
            )

        self.data_filter_timer = QtCore.QTimer()
        self.data_filter_timer.setSingleShot(True)
        self.data_filter_timer.setInterval(300)
        self.data_filter_timer.timeout.connect(self.change_data_filter)

        self.active_plot_window = None

    def on_indices_toggled(self, state):

        self.ui.arrayIndices.setEnabled(state)

    def on_dir_loaded(self, directory):

        # we only want this to be called once on startup
        self.file_model.directoryLoaded.disconnect(self.on_dir_loaded)
        if self.preselect_file is None:
            return
        # preselect the given file
        index = self.file_model.index(self.preselect_file)
        self.ui.files.selectionModel().select(
            index, QtGui.QItemSelectionModel.ClearAndSelect
            )

    def on_browsedir_clicked(self):

        directory = QtGui.QFileDialog.getExistingDirectory(
            None, 'Select base FITS directory', self.ui.url.text()
            )
        if len(directory):
            self.ui.url.setText(directory)

    def on_hduList_filter_changed(self, new_text):

        self.hduList_proxy_model.setFilterRegExp(QtCore.QRegExp(
            new_text, Qt.CaseInsensitive, QtCore.QRegExp.RegExp2
            ))

    def on_files_filter_changed(self, new_text):

        self.file_model.setNameFilters([
            '*{}*'.format(item)
            for item in str(new_text).split()
            ])
        self.file_model.setNameFilterDisables(False)

    def on_hdu_selection_changed(self, item):

        real_item = self.hduList_proxy_model.mapToSource(item)
        hdu_entry = self.hduList_model.hdu_entry_for_index(real_item)

        self.hdu_header_proxy_model = QtGui.QSortFilterProxyModel()
        self.hdu_header_proxy_model.setSourceModel(FitsHeaderModel(hdu_entry))
        self.hdu_header_proxy_model.setFilterKeyColumn(0)
        self.ui.header.setModel(self.hdu_header_proxy_model)
        self.ui.header.resizeColumnsToContents()
        self.ui.header.verticalHeader().setDefaultSectionSize(20)
        self.on_header_filter_changed(self.ui.filterHeader.text())

        self.hdu_data_proxymodel = DataSortFilterProxyModel()
        self.hdu_data_proxymodel.setSourceModel(FitsDataModel(hdu_entry))
        self.ui.contents.setModel(self.hdu_data_proxymodel)
        self.ui.contents.resizeColumnsToContents()
        self.ui.contents.verticalHeader().setDefaultSectionSize(20)
        self.change_data_filter()

    def on_plot_selection_triggered(self):

        if (
                not QtGui.QApplication.mouseButtons() & Qt.RightButton and
                not isinstance(self.sender(), QtGui.QPushButton) and
                not isinstance(self.sender(), QtGui.QAction)
                ):

            return

        plot_args = {}
        if hasattr(self.sender(), 'text'):
            try:
                plot_args = list(filter(
                    lambda x: x[0] == self.sender().text(),
                    PLOT_ACTIONS
                    ))[0][1]
            except IndexError:
                pass

        if (
                self.active_plot_window is None or
                self.active_plot_window.isHidden()
                ):
            self.active_plot_window = PlotWindow()

        p = self.active_plot_window.active_plot()
        # needs to be called here so the hold state is correct for the
        # selected subplot
        self.active_plot_window.update_hold()

        selection = self.ui.contents.selectionModel().selectedIndexes()

        if self.ui.indicesCheckbox.isChecked():
            array_fields = self.ui.arrayIndices.value()
        else:
            array_fields = '*'

        def _get_data(index):

            index = self.hdu_data_proxymodel.mapToSource(index)
            data = self.hdu_data_proxymodel.sourceModel().data(
                index, RAW_DATA_ROLE
                )

            if type(data) == np.ndarray and array_fields != '*':

                try:
                    return data[array_fields]
                except ValueError:
                    self.ui.statusbar.showMessage(
                        'out-of-range value in array index field', 10000
                        )

            return data

        def _get_label(column):

            return str(self.hdu_data_proxymodel.sourceModel().headerData(
                column, Qt.Horizontal, Qt.DisplayRole
                ))

        unique_cols_selected = set(item.column() for item in selection)

        if len(selection) == 1:

            p.set_ylabel(_get_label(selection[0].column()))
            p.plot(_get_data(selection[0]), **plot_args)

        elif len(unique_cols_selected) == 2:

            # plot first as x, second as y
            key_col, value_col = unique_cols_selected
            keys = [
                _get_data(index)
                for index in selection
                if index.column() == key_col
                ]
            values = [
                _get_data(index)
                for index in selection
                if index.column() == value_col
                ]
            if np.ndarray in map(type, keys) or np.ndarray in map(type, values):
                self.ui.statusbar.showMessage(
                    "Sorry, don't know how to plot that", 10000
                    )
                return

            p.set_xlabel(_get_label(key_col))
            p.set_ylabel(_get_label(value_col))
            p.plot(keys, values, **plot_args)

        else:

            data_parts = [_get_data(index) for index in selection]
            label = ', '.join(set(
                _get_label(index.column())
                for index in selection
                ))
            p.set_ylabel(label)

            if False not in [
                    isinstance(part, np.ndarray)
                    for part in data_parts
                    ]:
                # all items are arrays -> plot as curves
                for item in data_parts:
                    p.plot(item, **plot_args)
                    # temporarily enable hold so all curves are painted
                    # this is inside the loop so the first call clears the
                    # plot if desired
                    self.active_plot_window.canvas.axes.hold(True)
                self.active_plot_window.update_hold()
            else:
                p.plot(np.array(data_parts), **plot_args)

        if self.active_plot_window.isVisible():
            self.active_plot_window.active_plot().figure.canvas.draw()
        else:
            self.active_plot_window.show()

        self.active_plot_window.make_next_subplot_current()

    def on_header_filter_changed(self, new_text):
        self.hdu_header_proxy_model.setFilterRegExp(QtCore.QRegExp(
            new_text, Qt.CaseInsensitive, QtCore.QRegExp.RegExp2
            ))

    def on_data_filter_changed(self, new_text):

        self.data_filter_timer.text = new_text
        self.data_filter_timer.start()

    def change_data_filter(self):

        if not hasattr(self.data_filter_timer, 'text'):
            return

        self.hdu_data_proxymodel.change_filter(self.data_filter_timer.text)

    def on_file_selected(self):

        files = self.ui.files.selectionModel().selectedIndexes()

        try:
            filename = str(files[0].data(Qt.DisplayRole).toString())
        except AttributeError:
            filename = str(files[0].data(Qt.DisplayRole))
        except IndexError:
            print('No file selected, huh?')
            return

        new_path = self.ui.url.text() + '/' + filename

        if os.path.isdir(new_path):
            # If the item which was clicked was a directory, go there
            self.ui.url.setText(os.path.normpath(str(new_path)))
            return

        self.current_file = new_path

        try:
            hdulist = pyfits.open(str(self.current_file))
        except IOError as e:
            self.ui.statusbar.showMessage(
                'Failed to open {}: {}'.format(self.current_file, str(e)),
                10000
                )
            return

        self.hduList_proxy_model = QtGui.QSortFilterProxyModel()
        self.hduList_model = FitsHeaderListModel(hdulist)
        self.hduList_proxy_model.setSourceModel(self.hduList_model)
        self.on_hduList_filter_changed(self.ui.filterSections.text())

        self.ui.sections.setModel(self.hduList_proxy_model)
        self.ui.sections.resizeColumnsToContents()
        self.ui.sections.selectionModel().currentChanged.connect(
            self.on_hdu_selection_changed
            )
        self.ui.header.setModel(None)
        self.ui.contents.setModel(None)
        self.setWindowTitle('pyfv: {}'.format(self.current_file))

    def on_path_changed(self):

        index = self.file_model.setRootPath(self.ui.url.text())
        self.ui.files.setRootIndex(index)
        self.setWindowTitle('pyfv: {}'.format(self.ui.url.text()))

    def closeEvent(self, event):

        self.write_settings()
        super(FitsViewer, self).closeEvent(event)

    def write_settings(self):
        '''
        Store settings (including layout and window geometry).
        '''

        settings = QtCore.QSettings('RadioTeleskopEffelsberg', 'pyfv')
        settings.setValue(
            'splitter/splitterSizes', self.ui.splitter.saveState()
            )
        settings.setValue(
            'splitter_2/splitterSizes', self.ui.splitter_2.saveState()
            )
        settings.setValue(
            'splitter_3/splitterSizes', self.ui.splitter_3.saveState()
            )
        settings.setValue('pyfv/geometry', self.saveGeometry())
        settings.setValue('pyfv/windowState', self.saveState())

    def read_settings(self):
        '''
        Read stored settings (including layout and window geometry).
        '''

        settings = QtCore.QSettings('RadioTeleskopEffelsberg', 'pyfv')

        self.ui.splitter.restoreState(settings.value('splitter/splitterSizes'))
        self.ui.splitter_2.restoreState(
            settings.value('splitter_2/splitterSizes')
            )
        self.ui.splitter_3.restoreState(
            settings.value('splitter_3/splitterSizes')
            )
        self.restoreGeometry(settings.value('pyfv/geometry'))
        self.restoreState(settings.value('pyfv/windowState'))

    def showEvent(self, se):
        '''
        it is necessary to perform "readSettings" after all of the GUI elements
        were processed and the first showevent occurs otherwise not all
        settings will be processed correctly
        '''

        super(FitsViewer, self).showEvent(se)

        if self._do_read_settings:
            self.read_settings()
            self._do_read_settings = False


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = FitsViewer()
    window.show()
    app.exec_()
