from PyQt4.QtGui import QMainWindow, QDialog
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QFileSystemModel, QTableView, QColor, QFont, QPushButton, QFileDialog
from PyQt4.QtGui import QSortFilterProxyModel, QItemSelectionModel
from PyQt4 import QtGui

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QObject, QRegExp, QString, QTimer, QDir
from PyQt4.QtCore import QFile

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import pyfits
import matplotlib.pyplot as plt
from numpy import array as nparray, ndarray

import mainwindow
import plotwindow

import sys
import os

RAW_DATA_ROLE = Qt.UserRole + 1

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.figure)

        self.axes = self.figure.add_subplot(1, 1, 1)
        #self.axes.hold(False)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class PlotWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = plotwindow.Ui_Dialog()
        self.ui.setupUi(self)
        self.canvas = MatplotlibCanvas(self)
        self.ui.plotContainer.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ui.plotContainer.addWidget(self.toolbar)

    def activePlot(self):
        ax = self.canvas.axes
        assert isinstance(ax, plt.Axes)
        return ax

class FitsHeaderListModel(QAbstractTableModel):
    def __init__(self, hdulist):
        QAbstractTableModel.__init__(self)
        self.hdulist = hdulist

    def rowCount(self, parent):
        try:
            return len(self.hdulist)
        except AttributeError:
            return 0

    def columnCount(self, parent):
        return 2

    def hduEntryForIndex(self, modelIndex):
        return self.hdulist[modelIndex.row()]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "Name"
            if section == 1:
                return "Shape"
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            # zero indexing
            return QAbstractTableModel.headerData(self, section, orientation, role).toInt()[0] - 1
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            entry = self.hdulist[index.row()]
            if index.column() == 0:
                return entry.name
            if index.column() == 1:
                try:
                    return "{0}x{1}".format(len(entry.columns), len(entry.data))
                except AttributeError:
                    return "---"
        if role == Qt.ForegroundRole:
            if index.column() == 1:
                return QColor("#8F8F8F")
            if index.column() == 0:
                entry = str(self.hdulist[index.row()].name)
                if entry.find("ARRAYDATA") != -1:
                    return QColor("#880064")
                if entry.find("DATAPAR") != -1:
                    return QColor("#007BE0")
                if entry.find("MONITOR") != -1:
                    return QColor("#004D8C")
                if entry.find("SCAN") != -1:
                    return QColor("#881900")
        if role == Qt.FontRole:
            if index.column() == 0:
                f = QFont()
                f.setBold(True)
                return f

class FitsHeaderModel(QAbstractTableModel):
    def __init__(self, hduentry):
        QAbstractTableModel.__init__(self)
        self.header = hduentry.header

    def rowCount(self, parent):
        return len(self.header)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "Key"
            if section == 1:
                return "Value"
            if section == 2:
                return "Comment"
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.header.keys()[index.row()]
            if index.column() == 1:
                return self.header.values()[index.row()]
            if index.column() == 2:
                return self.header.comments[self.header.keys()[index.row()]]

        if role == Qt.ForegroundRole:
            if index.column() == 1:
                return QColor("#900059")
            if index.column() == 2:
                return QColor("#8F8F8F")

class FitsDataModel(QAbstractTableModel):
    def __init__(self, hduentry):
        QAbstractTableModel.__init__(self)
        self.fitsdata = hduentry.data

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
            return "{0} / {1} [{2}]".format(item.name, item.format, item.unit)
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            data = self.fitsdata[index.row()][index.column()]
            return str(data)
        if role == RAW_DATA_ROLE:
            return self.fitsdata[index.row()][index.column()]

class DataSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        QSortFilterProxyModel.__init__(self)
        self.strColumns = []
        self.filterString = str()

    def filterAcceptsColumn(self, source_column, source_parent):
        return True

    def changeFilter(self, newFilter):
        self.filterString = newFilter
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not len(self.filterString):
            return True

        if len(self.strColumns) == 0:
            for column in range(self.sourceModel().columnCount(QModelIndex())):
                index = self.sourceModel().index(0, column, QModelIndex())
                if isinstance(self.sourceModel().data(index, RAW_DATA_ROLE), str):
                    self.strColumns.append(column)

        for column in self.strColumns:
            index = self.sourceModel().index(source_row, column, source_parent)
            data = str(self.sourceModel().data(index, RAW_DATA_ROLE))
            if data.find(self.filterString) != -1:
                return True
        return False

class FitsViewer(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.currentFile = None

        self.fileModel = QFileSystemModel()
        if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
            components = sys.argv[1].split('/')
            startDir = '/'.join(components[:-1])
            self.preselectFile = sys.argv[1]
        elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
            startDir = sys.argv[1]
            self.preselectFile = None
        else:
            startDir = os.getcwd()
            self.preselectFile = None
        if not os.path.isdir(startDir):
            startDir = os.getcwd()
        self.fileModel.setRootPath(startDir)
        self.fileModel.setFilter(QDir.Files | QDir.Dirs | QDir.NoDot)
        self.fileModel.directoryLoaded.connect(self.filesLoaded)
        self.ui.files.setModel(self.fileModel)

        self.ui.url.setText(startDir)
        self.ui.url.textChanged.connect(self.pathChanged)
        self.pathChanged()
        self.ui.files.selectionModel().selectionChanged.connect(self.fileSelected)

        self.ui.sections.setSelectionBehavior(QTableView.SelectRows)
        self.ui.sections.verticalHeader().setDefaultSectionSize(20)
        self.ui.sections.setShowGrid(False)
        self.ui.header.setShowGrid(False)
        self.ui.sections.setStyleSheet("QTableView::item { padding: 25px }")
        self.ui.header.setStyleSheet("QTableView::item { padding: 8px }")
        self.ui.contents.setStyleSheet("QTableView::item { padding: 8px }")

        self.ui.splitter.setSizes([200, 500])
        self.ui.splitter_2.setSizes([200, 500])
        self.ui.splitter_3.setSizes([200, 500])

        self.ui.plotButton.pressed.connect(self.plotSelection)
        self.ui.contents.pressed.connect(self.plotSelection)

        self.ui.filterHeader.textChanged.connect(self.headerFilterChanged)
        self.ui.filterData.textChanged.connect(self.dataFilterChanged)
        self.ui.filterFiles.textChanged.connect(self.filesFilterChanged)
        self.ui.filterSections.textChanged.connect(self.hduListFilterChanged)
        self.ui.indicesButton.clicked.connect(self.indicesButtonClicked)
        self.ui.browseDirectoryButton.clicked.connect(self.browse)

        self.dataFilterTimer = QTimer()
        self.dataFilterTimer.setSingleShot(True)
        self.dataFilterTimer.setInterval(300)
        self.dataFilterTimer.timeout.connect(self.changeDataFilter)

        self.activePlotWindow = None

    def filesLoaded(self, directory):
        # we only want this to be called once on startup
        self.fileModel.directoryLoaded.disconnect(self.filesLoaded)
        if self.preselectFile is None:
            return
        # preselect the given file
        index = self.fileModel.index(self.preselectFile)
        self.ui.files.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    def browse(self):
        directory = QFileDialog.getExistingDirectory(None, "Select base FITS directory", self.ui.url.text())
        if len(directory):
            self.ui.url.setText(directory)

    def hduListFilterChanged(self, newText):
        self.hduListProxyModel.setFilterRegExp(QRegExp(newText, Qt.CaseInsensitive, QRegExp.RegExp2))

    def filesFilterChanged(self, newText):
        self.fileModel.setNameFilters(["*{0}*".format(item) for item in str(newText).split()])
        self.fileModel.setNameFilterDisables(False)

    def indicesButtonClicked(self):
        self.ui.indicesLineEdit.setText("*")

    def hduSelected(self, item):
        realItem = self.hduListProxyModel.mapToSource(item)
        hduEntry = self.hduListModel.hduEntryForIndex(realItem)
        self.hduHeaderProxyModel = QSortFilterProxyModel()
        self.hduHeaderProxyModel.setSourceModel(FitsHeaderModel(hduEntry))
        self.hduHeaderProxyModel.setFilterKeyColumn(0)
        self.ui.header.setModel(self.hduHeaderProxyModel)
        self.ui.header.resizeColumnsToContents()
        self.ui.header.verticalHeader().setDefaultSectionSize(20)
        self.headerFilterChanged(self.ui.filterHeader.text())

        self.hduDataProxyModel = DataSortFilterProxyModel()
        self.hduDataProxyModel.setSourceModel(FitsDataModel(hduEntry))
        self.ui.contents.setModel(self.hduDataProxyModel)
        self.ui.contents.resizeColumnsToContents()
        self.ui.contents.verticalHeader().setDefaultSectionSize(20)
        self.changeDataFilter()

    def plotSelection(self):
        if not QApplication.mouseButtons() & Qt.RightButton and not isinstance(self.sender(), QPushButton):
            return

        if self.activePlotWindow is None or self.activePlotWindow.isHidden():
            self.activePlotWindow = PlotWindow()
        p = self.activePlotWindow.activePlot()

        selection = self.ui.contents.selectionModel().selectedIndexes()

        arrayFields = self.ui.indicesLineEdit.text()
        def getData(index):
            index = self.hduDataProxyModel.mapToSource(index)
            data = self.hduDataProxyModel.sourceModel().data(index, RAW_DATA_ROLE)
            if type(data) == ndarray and arrayFields != "*":
                try:
                    return data[int(arrayFields)]
                except ValueError:
                    self.ui.statusbar.showMessage("whops, non-integer in array index field", 10000)
            return data
        def getLabel(column):
            return str(self.hduDataProxyModel.sourceModel().headerData(column, Qt.Horizontal, Qt.DisplayRole))

        distinctColsSelected = {item.column() for item in selection}
        if len(selection) == 1:
            p.set_ylabel(getLabel(selection[0].column()))
            p.plot(getData(selection[0]))
        elif len(distinctColsSelected) == 2:
            # plot first as x, second as y
            key_col, value_col = distinctColsSelected
            keys = [getData(index) for index in selection if index.column() == key_col]
            values = [getData(index) for index in selection if index.column() == value_col]
            if ndarray in map(type, keys) or ndarray in map(type, values):
                self.ui.statusbar.showMessage("Sorry, don't know how to plot that", 10000)
                return
            p.set_xlabel(getLabel(key_col))
            p.set_ylabel(getLabel(value_col))
            p.plot(keys, values)
        else:
            dataParts = [getData(index) for index in selection]
            label = ", ".join({getLabel(index.column()) for index in selection})
            p.set_ylabel(label)
            if False not in [isinstance(part, ndarray) for part in dataParts]:
                # all items are arrays -> plot as curves
                for item in dataParts:
                    p.plot(item)
            else:
                p.plot(nparray(dataParts))

        if self.activePlotWindow.isVisible():
            self.activePlotWindow.activePlot().figure.canvas.draw()
        else:
            self.activePlotWindow.show()

    def headerFilterChanged(self, newText):
        self.hduHeaderProxyModel.setFilterRegExp(QRegExp(newText, Qt.CaseInsensitive, QRegExp.RegExp2))

    def dataFilterChanged(self, newText):
        self.dataFilterTimer.text = newText
        self.dataFilterTimer.start()

    def changeDataFilter(self):
        if not hasattr(self.dataFilterTimer, "text"):
            return
        self.hduDataProxyModel.changeFilter(self.dataFilterTimer.text)

    def fileSelected(self):
        files = self.ui.files.selectionModel().selectedIndexes()
        try:
            filename = files[0].data(Qt.DisplayRole).toString()
        except IndexError:
            print "No file selected, huh?"
            return
        newPath = self.ui.url.text() + "/" + filename
        if os.path.isdir(newPath):
            # If the item which was clicked was a directory, switch there and exit
            self.ui.url.setText(os.path.normpath(str(newPath)))
            return
        self.currentFile = newPath
        try:
            hdulist = pyfits.open(str(self.currentFile))
        except IOError as e:
            self.ui.statusbar.showMessage("Failed to open {0}: {1}".format(self.currentFile, str(e)), 10000)
            return
        self.hduListProxyModel = QSortFilterProxyModel()
        self.hduListModel = FitsHeaderListModel(hdulist)
        self.hduListProxyModel.setSourceModel(self.hduListModel)
        self.hduListFilterChanged(self.ui.filterSections.text())

        self.ui.sections.setModel(self.hduListProxyModel)
        self.ui.sections.resizeColumnsToContents()
        self.ui.sections.selectionModel().currentChanged.connect(self.hduSelected)
        self.ui.header.setModel(None)
        self.ui.contents.setModel(None)
        self.setWindowTitle("pyfv: {0}".format(self.currentFile))

    def pathChanged(self):
        index = self.fileModel.setRootPath(self.ui.url.text())
        self.ui.files.setRootIndex(index)
        self.setWindowTitle("pyfv: {0}".format(self.ui.url.text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FitsViewer()
    window.show()
    app.exec_()
