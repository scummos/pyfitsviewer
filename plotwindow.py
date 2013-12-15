# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwindow.ui'
#
# Created: Sun Dec 15 12:50:56 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(539, 369)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.subdivLabel = QtGui.QLabel(Dialog)
        self.subdivLabel.setObjectName(_fromUtf8("subdivLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.subdivLabel)
        self.figureSizeCombo = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.figureSizeCombo.sizePolicy().hasHeightForWidth())
        self.figureSizeCombo.setSizePolicy(sizePolicy)
        self.figureSizeCombo.setObjectName(_fromUtf8("figureSizeCombo"))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.figureSizeCombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.figureSizeCombo)
        self.subfigLabel = QtGui.QLabel(Dialog)
        self.subfigLabel.setObjectName(_fromUtf8("subfigLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.subfigLabel)
        self.activeSubfigure = QtGui.QSpinBox(Dialog)
        self.activeSubfigure.setMinimum(1)
        self.activeSubfigure.setObjectName(_fromUtf8("activeSubfigure"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.activeSubfigure)
        self.verticalLayout.addLayout(self.formLayout)
        self.plotContainer = QtGui.QVBoxLayout()
        self.plotContainer.setObjectName(_fromUtf8("plotContainer"))
        self.verticalLayout.addLayout(self.plotContainer)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.subdivLabel.setText(_translate("Dialog", "Figure subdivision", None))
        self.figureSizeCombo.setItemText(0, _translate("Dialog", "1x1", None))
        self.figureSizeCombo.setItemText(1, _translate("Dialog", "1x2", None))
        self.figureSizeCombo.setItemText(2, _translate("Dialog", "2x1", None))
        self.figureSizeCombo.setItemText(3, _translate("Dialog", "2x2", None))
        self.figureSizeCombo.setItemText(4, _translate("Dialog", "1x3", None))
        self.figureSizeCombo.setItemText(5, _translate("Dialog", "3x1", None))
        self.subfigLabel.setText(_translate("Dialog", "Active subfigure", None))
        self.activeSubfigure.setPrefix(_translate("Dialog", "Figure ", None))

