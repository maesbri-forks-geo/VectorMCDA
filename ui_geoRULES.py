# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geoRULES.ui'
#
# Created: Wed Jan 06 17:46:44 2016
#      by: PyQt4 UI code generator 4.10.2
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
        Dialog.resize(513, 570)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.toolBox = QtGui.QToolBox(Dialog)
        self.toolBox.setStyleSheet(_fromUtf8("\n"
"font: 75 italic 10pt \"MS Shell Dlg 2\";"))
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.settingQTbox = QtGui.QWidget()
        self.settingQTbox.setGeometry(QtCore.QRect(0, 0, 495, 432))
        self.settingQTbox.setObjectName(_fromUtf8("settingQTbox"))
        self.SettingButtonBox = QtGui.QDialogButtonBox(self.settingQTbox)
        self.SettingButtonBox.setGeometry(QtCore.QRect(330, 390, 156, 24))
        self.SettingButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.SettingButtonBox.setObjectName(_fromUtf8("SettingButtonBox"))
        self.DiscretizeGbox = QtGui.QGroupBox(self.settingQTbox)
        self.DiscretizeGbox.setGeometry(QtCore.QRect(10, 230, 471, 131))
        self.DiscretizeGbox.setObjectName(_fromUtf8("DiscretizeGbox"))
        self.spinClasseNum = QtGui.QSpinBox(self.DiscretizeGbox)
        self.spinClasseNum.setEnabled(False)
        self.spinClasseNum.setGeometry(QtCore.QRect(60, 41, 36, 22))
        self.spinClasseNum.setMaximum(15)
        self.spinClasseNum.setProperty("value", 5)
        self.spinClasseNum.setObjectName(_fromUtf8("spinClasseNum"))
        self.ClassNumbLbl = QtGui.QLabel(self.DiscretizeGbox)
        self.ClassNumbLbl.setGeometry(QtCore.QRect(10, 41, 51, 16))
        self.ClassNumbLbl.setObjectName(_fromUtf8("ClassNumbLbl"))
        self.NewFieldNameDiscLbl = QtGui.QLabel(self.DiscretizeGbox)
        self.NewFieldNameDiscLbl.setGeometry(QtCore.QRect(140, 40, 151, 16))
        self.NewFieldNameDiscLbl.setObjectName(_fromUtf8("NewFieldNameDiscLbl"))
        self.cobBoxFieldNameDisc = QtGui.QComboBox(self.DiscretizeGbox)
        self.cobBoxFieldNameDisc.setGeometry(QtCore.QRect(290, 40, 171, 22))
        self.cobBoxFieldNameDisc.setObjectName(_fromUtf8("cobBoxFieldNameDisc"))
        self.EnvLbl_2 = QtGui.QLabel(self.settingQTbox)
        self.EnvLbl_2.setGeometry(QtCore.QRect(10, 20, 71, 19))
        self.EnvLbl_2.setObjectName(_fromUtf8("EnvLbl_2"))
        self.CritMapNameLbl_2 = QtGui.QLabel(self.settingQTbox)
        self.CritMapNameLbl_2.setGeometry(QtCore.QRect(110, 20, 361, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(9)
        self.CritMapNameLbl_2.setFont(font)
        self.CritMapNameLbl_2.setTextFormat(QtCore.Qt.AutoText)
        self.CritMapNameLbl_2.setObjectName(_fromUtf8("CritMapNameLbl_2"))
        self.groupBox = QtGui.QGroupBox(self.settingQTbox)
        self.groupBox.setGeometry(QtCore.QRect(10, 80, 471, 131))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.checkSelected = QtGui.QCheckBox(self.groupBox)
        self.checkSelected.setGeometry(QtCore.QRect(20, 60, 331, 17))
        self.checkSelected.setObjectName(_fromUtf8("checkSelected"))
        self.toolBox.addItem(self.settingQTbox, _fromUtf8(""))
        self.CriteriaQTbox = QtGui.QWidget()
        self.CriteriaQTbox.setGeometry(QtCore.QRect(0, 0, 495, 432))
        self.CriteriaQTbox.setObjectName(_fromUtf8("CriteriaQTbox"))
        self.CritListFieldsCBox = QtGui.QComboBox(self.CriteriaQTbox)
        self.CritListFieldsCBox.setGeometry(QtCore.QRect(80, 30, 181, 20))
        self.CritListFieldsCBox.setObjectName(_fromUtf8("CritListFieldsCBox"))
        self.EnvLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.EnvLbl.setGeometry(QtCore.QRect(2, 0, 71, 19))
        self.EnvLbl.setObjectName(_fromUtf8("EnvLbl"))
        self.CritFieldsLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.CritFieldsLbl.setGeometry(QtCore.QRect(2, 32, 81, 23))
        self.CritFieldsLbl.setObjectName(_fromUtf8("CritFieldsLbl"))
        self.CritMapNameLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.CritMapNameLbl.setGeometry(QtCore.QRect(100, 0, 361, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(9)
        self.CritMapNameLbl.setFont(font)
        self.CritMapNameLbl.setTextFormat(QtCore.Qt.AutoText)
        self.CritMapNameLbl.setObjectName(_fromUtf8("CritMapNameLbl"))
        self.CritTEdit = QtGui.QTextEdit(self.CriteriaQTbox)
        self.CritTEdit.setGeometry(QtCore.QRect(10, 380, 451, 51))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.CritTEdit.sizePolicy().hasHeightForWidth())
        self.CritTEdit.setSizePolicy(sizePolicy)
        self.CritTEdit.setObjectName(_fromUtf8("CritTEdit"))
        self.DeclistFieldsCBox = QtGui.QComboBox(self.CriteriaQTbox)
        self.DeclistFieldsCBox.setGeometry(QtCore.QRect(110, 341, 351, 20))
        self.DeclistFieldsCBox.setObjectName(_fromUtf8("DeclistFieldsCBox"))
        self.DecFieldsLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.DecFieldsLbl.setGeometry(QtCore.QRect(10, 340, 81, 23))
        self.DecFieldsLbl.setObjectName(_fromUtf8("DecFieldsLbl"))
        self.CritExtractBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritExtractBtn.setGeometry(QtCore.QRect(394, 80, 71, 201))
        self.CritExtractBtn.setObjectName(_fromUtf8("CritExtractBtn"))
        self.CritHelpBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritHelpBtn.setGeometry(QtCore.QRect(390, 300, 75, 24))
        self.CritHelpBtn.setObjectName(_fromUtf8("CritHelpBtn"))
        self.CritAddFieldBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritAddFieldBtn.setGeometry(QtCore.QRect(290, 30, 71, 24))
        self.CritAddFieldBtn.setObjectName(_fromUtf8("CritAddFieldBtn"))
        self.critTableWiget = QtGui.QTableWidget(self.CriteriaQTbox)
        self.critTableWiget.setGeometry(QtCore.QRect(0, 70, 361, 251))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(9)
        self.critTableWiget.setFont(font)
        self.critTableWiget.setAutoFillBackground(False)
        self.critTableWiget.setAlternatingRowColors(True)
        self.critTableWiget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.critTableWiget.setShowGrid(False)
        self.critTableWiget.setObjectName(_fromUtf8("critTableWiget"))
        self.critTableWiget.setColumnCount(0)
        self.critTableWiget.setRowCount(0)
        self.toolBox.addItem(self.CriteriaQTbox, _fromUtf8(""))
        self.RoulesQTBox = QtGui.QWidget()
        self.RoulesQTBox.setGeometry(QtCore.QRect(0, 0, 495, 432))
        self.RoulesQTBox.setObjectName(_fromUtf8("RoulesQTBox"))
        self.RulesBtnBox = QtGui.QDialogButtonBox(self.RoulesQTBox)
        self.RulesBtnBox.setGeometry(QtCore.QRect(310, 400, 156, 23))
        self.RulesBtnBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.RulesBtnBox.setObjectName(_fromUtf8("RulesBtnBox"))
        self.RulesListWidget = QtGui.QListWidget(self.RoulesQTBox)
        self.RulesListWidget.setGeometry(QtCore.QRect(10, 11, 471, 281))
        self.RulesListWidget.setAcceptDrops(True)
        self.RulesListWidget.setObjectName(_fromUtf8("RulesListWidget"))
        self.ruleEdit = QtGui.QTextEdit(self.RoulesQTBox)
        self.ruleEdit.setGeometry(QtCore.QRect(10, 310, 471, 71))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.ruleEdit.sizePolicy().hasHeightForWidth())
        self.ruleEdit.setSizePolicy(sizePolicy)
        self.ruleEdit.setObjectName(_fromUtf8("ruleEdit"))
        self.toolBox.addItem(self.RoulesQTBox, _fromUtf8(""))
        self.classifyQTbox = QtGui.QWidget()
        self.classifyQTbox.setGeometry(QtCore.QRect(0, 0, 495, 432))
        self.classifyQTbox.setObjectName(_fromUtf8("classifyQTbox"))
        self.ClassifyRulesWidget = QtGui.QListWidget(self.classifyQTbox)
        self.ClassifyRulesWidget.setGeometry(QtCore.QRect(10, 20, 471, 301))
        self.ClassifyRulesWidget.setAcceptDrops(True)
        self.ClassifyRulesWidget.setObjectName(_fromUtf8("ClassifyRulesWidget"))
        self.reclassButtonBox = QtGui.QDialogButtonBox(self.classifyQTbox)
        self.reclassButtonBox.setGeometry(QtCore.QRect(320, 360, 156, 23))
        self.reclassButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.reclassButtonBox.setObjectName(_fromUtf8("reclassButtonBox"))
        self.toolBox.addItem(self.classifyQTbox, _fromUtf8(""))
        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.CritListFieldsCBox, self.CritAddFieldBtn)
        Dialog.setTabOrder(self.CritAddFieldBtn, self.CritExtractBtn)
        Dialog.setTabOrder(self.CritExtractBtn, self.CritHelpBtn)
        Dialog.setTabOrder(self.CritHelpBtn, self.CritTEdit)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "geoRules", None))
        self.DiscretizeGbox.setTitle(_translate("Dialog", "Discretize", None))
        self.ClassNumbLbl.setText(_translate("Dialog", "Classes", None))
        self.NewFieldNameDiscLbl.setText(_translate("Dialog", "Classification field name", None))
        self.EnvLbl_2.setText(_translate("Dialog", "Active layer     ", None))
        self.groupBox.setTitle(_translate("Dialog", "Features to use", None))
        self.checkSelected.setText(_translate("Dialog", "Use  selected features only", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.settingQTbox), _translate("Dialog", "Setting", None))
        self.EnvLbl.setText(_translate("Dialog", "Active layer     ", None))
        self.CritFieldsLbl.setText(_translate("Dialog", "Active field", None))
        self.DecFieldsLbl.setText(_translate("Dialog", "Decision field", None))
        self.CritExtractBtn.setText(_translate("Dialog", " Extract", None))
        self.CritHelpBtn.setText(_translate("Dialog", "Help", None))
        self.CritAddFieldBtn.setText(_translate("Dialog", "Add", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.CriteriaQTbox), _translate("Dialog", "Criteria", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.RoulesQTBox), _translate("Dialog", "Rules", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.classifyQTbox), _translate("Dialog", "Classify", None))

