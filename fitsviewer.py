from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QFileSystemModel, QTableView, QColor, QFont, QPushButton

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QObject

import pyfits
import matplotlib.pyplot as plt
from numpy import array as nparray, ndarray

import mainwindow

import sys
import os

RAW_DATA_ROLE = Qt.UserRole + 1

class FitsHeaderListModel(QAbstractTableModel):
    def __init__(self, fileUrl):
        QAbstractTableModel.__init__(self)
        self.hdulist = pyfits.open(str(fileUrl))

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

class FitsViewer(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.currentFile = None

        self.fileModel = QFileSystemModel()
        startDir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
        self.fileModel.setRootPath(startDir)
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

    def hduSelected(self, item):
        hduEntry = self.hduListModel.hduEntryForIndex(item)
        self.ui.header.setModel(FitsHeaderModel(hduEntry))
        self.ui.header.resizeColumnsToContents()
        self.ui.header.verticalHeader().setDefaultSectionSize(20)

        self.ui.contents.setModel(FitsDataModel(hduEntry))
        self.ui.contents.resizeColumnsToContents()
        self.ui.contents.verticalHeader().setDefaultSectionSize(20)

    def plotSelection(self):
        if not QApplication.mouseButtons() & Qt.RightButton and not isinstance(self.sender(), QPushButton):
            return
        plt.close()

        selection = self.ui.contents.selectionModel().selectedIndexes()

        def getData(index):
            return self.ui.contents.model().data(index, RAW_DATA_ROLE)

        if len(selection) == 1:
            data = getData(selection[0])
            plt.plot(data)
        else:
            dataParts = [getData(index) for index in selection]
            if False not in [isinstance(p, ndarray) for p in dataParts]:
                # all items are arrays -> plot as curves
                for item in dataParts:
                    plt.plot(item)
            else:
                plt.plot(nparray(dataParts))

        plt.show()

    def fileSelected(self):
        files = self.ui.files.selectionModel().selectedIndexes()
        try:
            filename = files[0].data(Qt.DisplayRole).toString()
        except IndexError:
            print "No file selected, huh?"
            return
        self.currentFile = self.ui.url.text() + "/" + filename
        self.hduListModel = FitsHeaderListModel(self.currentFile)

        self.ui.sections.setModel(self.hduListModel)
        self.ui.sections.resizeColumnsToContents()
        self.ui.sections.selectionModel().currentChanged.connect(self.hduSelected)
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
