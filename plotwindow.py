# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwindow.ui'
#
# Created: Sun Dec 15 17:02:15 2013
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
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.subdivLabel = QtGui.QLabel(Dialog)
        self.subdivLabel.setObjectName(_fromUtf8("subdivLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.subdivLabel)
        self.layoutCombo = QtGui.QComboBox(Dialog)
        self.layoutCombo.setObjectName(_fromUtf8("layoutCombo"))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.layoutCombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.layoutCombo)
        self.subfigLabel = QtGui.QLabel(Dialog)
        self.subfigLabel.setObjectName(_fromUtf8("subfigLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.subfigLabel)
        self.keepPreviousLabel = QtGui.QLabel(Dialog)
        self.keepPreviousLabel.setObjectName(_fromUtf8("keepPreviousLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.keepPreviousLabel)
        self.keepPrevious = QtGui.QCheckBox(Dialog)
        self.keepPrevious.setChecked(True)
        self.keepPrevious.setObjectName(_fromUtf8("keepPrevious"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.keepPrevious)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.activeSubfigure = QtGui.QSpinBox(Dialog)
        self.activeSubfigure.setMinimum(1)
        self.activeSubfigure.setObjectName(_fromUtf8("activeSubfigure"))
        self.horizontalLayout.addWidget(self.activeSubfigure)
        self.lockActiveSubfigure = QtGui.QPushButton(Dialog)
        self.lockActiveSubfigure.setCheckable(True)
        self.lockActiveSubfigure.setObjectName(_fromUtf8("lockActiveSubfigure"))
        self.horizontalLayout.addWidget(self.lockActiveSubfigure)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.plotContainer = QtGui.QVBoxLayout()
        self.plotContainer.setObjectName(_fromUtf8("plotContainer"))
        self.verticalLayout.addLayout(self.plotContainer)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.keepPreviousLabel.setBuddy(self.keepPrevious)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.subdivLabel.setText(_translate("Dialog", "Layout", None))
        self.layoutCombo.setToolTip(_translate("Dialog", "Select a different layout here to show multiple plots side-by-side", None))
        self.layoutCombo.setItemText(0, _translate("Dialog", "1x1", None))
        self.layoutCombo.setItemText(1, _translate("Dialog", "2x1", None))
        self.layoutCombo.setItemText(2, _translate("Dialog", "1x2", None))
        self.layoutCombo.setItemText(3, _translate("Dialog", "2x2", None))
        self.layoutCombo.setItemText(4, _translate("Dialog", "3x1", None))
        self.layoutCombo.setItemText(5, _translate("Dialog", "1x3", None))
        self.subfigLabel.setText(_translate("Dialog", "Active subfigure", None))
        self.keepPreviousLabel.setText(_translate("Dialog", "Keep previous curves", None))
        self.keepPrevious.setToolTip(_translate("Dialog", "Keep the curves already in the plot when drawing a new one", None))
        self.keepPrevious.setText(_translate("Dialog", "Enabled", None))
        self.activeSubfigure.setToolTip(_translate("Dialog", "Select the subplot to be used for the next draw request", None))
        self.activeSubfigure.setPrefix(_translate("Dialog", "Figure ", None))
        self.lockActiveSubfigure.setToolTip(_translate("Dialog", "Lock the active subfigure value, so subsequent draw requests are drawn into the same figure", None))
        self.lockActiveSubfigure.setText(_translate("Dialog", "Lock", None))
        self.buttonBox.setToolTip(_translate("Dialog", "Reset the layout and clear all plots", None))

