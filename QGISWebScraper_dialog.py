# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QGISWebScraper_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QGISWebScraperDialogBase(object):
    def setupUi(self, QGISWebScraperDialogBase):
        QGISWebScraperDialogBase.setObjectName("QGISWebScraperDialogBase")
        QGISWebScraperDialogBase.resize(600, 500)
        
        # Set window icon here
        QGISWebScraperDialogBase.setWindowIcon(QtGui.QIcon('resources/sol_de_mayo.png'))

        self.verticalLayout = QtWidgets.QVBoxLayout(QGISWebScraperDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")

        self.wmsTreeWidget = QtWidgets.QTreeWidget(QGISWebScraperDialogBase)
        self.wmsTreeWidget.setObjectName("wmsTreeWidget")
        self.wmsTreeWidget.setColumnCount(2)
        self.verticalLayout.addWidget(self.wmsTreeWidget)

        self.importButton = QtWidgets.QPushButton(QGISWebScraperDialogBase)
        self.importButton.setObjectName("importButton")
        self.verticalLayout.addWidget(self.importButton)

        self.retranslateUi(QGISWebScraperDialogBase)
        QtCore.QMetaObject.connectSlotsByName(QGISWebScraperDialogBase)

    def retranslateUi(self, QGISWebScraperDialogBase):
        _translate = QtCore.QCoreApplication.translate
        QGISWebScraperDialogBase.setWindowTitle(_translate("QGISWebScraperDialogBase", "ArgentinaGeoServices"))
        self.wmsTreeWidget.setHeaderLabels([_translate("QGISWebScraperDialogBase", "Organismo"), _translate("QGISWebScraperDialogBase", "WMS Link")])
        self.importButton.setText(_translate("QGISWebScraperDialogBase", "Import Selected WMS"))
