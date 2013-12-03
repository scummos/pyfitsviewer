from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QFileSystemModel, QTableView

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

import pyfits

import mainwindow

import sys
import os

class FitsHeaderModel(QAbstractTableModel):
    def __init__(self, fileUrl):
        QAbstractTableModel.__init__(self)
        self.hdulist = pyfits.open(str(fileUrl))

        self.setHeaderData(0, Qt.Horizontal, "Name")
        self.setHeaderData(1, Qt.Horizontal, "Shape")

    def rowCount(self, parent):
        try:
            return len(self.hdulist)
        except AttributeError:
            return 0

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if role == Qt.DisplayRole:
            entry = self.hdulist[index.row()]
            if index.column() == 0:
                return entry.name
            if index.column() == 1:
                try:
                    return "[{0}x{1}]".format(len(entry.columns), len(entry.data))
                except AttributeError:
                    return "---"
        return None

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

    def fileSelected(self):
        files = self.ui.files.selectionModel().selectedIndexes()
        try:
            filename = files[0].data(Qt.DisplayRole).toString()
        except IndexError:
            print "No file selected, huh?"
            return
        self.currentFile = self.ui.url.text() + "/" + filename
        self.ui.sections.setModel(FitsHeaderModel(self.currentFile))
        self.ui.sections.resizeColumnsToContents()

    def pathChanged(self):
        index = self.fileModel.setRootPath(self.ui.url.text())
        self.ui.files.setRootIndex(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FitsViewer()
    window.show()
    app.exec_()