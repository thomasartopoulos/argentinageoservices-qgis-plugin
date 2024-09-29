import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidgetItem
import pandas as pd
from .wms_checker import check_wms_availability

logger = logging.getLogger(__name__)

class QGISWebScraperDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArgentinaGeoServices")
        self.setWindowIcon(QtGui.QIcon('resources/sol_de_mayo.png'))
        self.resize(700, 500)

        layout = QVBoxLayout(self)
        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)

        buttonLayout = QHBoxLayout()
        self.importButton = QtWidgets.QPushButton("Import Selected WMS")
        self.checkStatusButton = QtWidgets.QPushButton("Check Selected WMS Status")
        buttonLayout.addWidget(self.importButton)
        buttonLayout.addWidget(self.checkStatusButton)
        layout.addLayout(buttonLayout)

    def populate_tabs_with_layers(self, layer_data):
        logger.info("Populating tabs with layers")
        self.tabWidget.clear()
        tab_names = ["Organismos Nacionales", "Organismos Provinciales", "Organismos Municipales", "Universidades", "Empresas"]

        for i, tab_name in enumerate(tab_names):
            logger.debug(f"Processing tab: {tab_name}")
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tree_widget = QtWidgets.QTreeWidget()

            if i in layer_data and layer_data[i] is not None:
                data = layer_data[i]
                logger.debug(f"Data for tab {tab_name}: {data.shape} rows, columns: {data.columns}")
                header_labels = data.columns.tolist()
                tree_widget.setHeaderLabels(header_labels)

                for _, row in data.iterrows():
                    values = [str(row[col]) if col in row and pd.notna(row[col]) else '' for col in data.columns]
                    item = QTreeWidgetItem(values)
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                    wms_link = row.get('WMS', '')
                    item.setData(0, QtCore.Qt.UserRole, wms_link)
                    tree_widget.addTopLevelItem(item)
                logger.debug(f"Added {tree_widget.topLevelItemCount()} items to tree widget for tab {tab_name}")
            else:
                logger.warning(f"No data available for tab: {tab_name}")
                tree_widget.setHeaderLabels(['Info'])
                item = QTreeWidgetItem([f"No data available for {tab_name}."])
                tree_widget.addTopLevelItem(item)

            tab_layout.addWidget(tree_widget)
            self.tabWidget.addTab(tab_widget, tab_name)
        
        logger.info(f"Populated {self.tabWidget.count()} tabs with layers")

    def check_selected_wms_status(self):
        logger.info("Checking selected WMS status")
        for i in range(self.tabWidget.count()):
            tree_widget = self.tabWidget.widget(i).findChild(QtWidgets.QTreeWidget)
            
            # Add Status column if it doesn't exist
            if 'Status' not in [tree_widget.headerItem().text(j) for j in range(tree_widget.columnCount())]:
                tree_widget.headerItem().setText(tree_widget.columnCount(), 'Status')
                for j in range(tree_widget.topLevelItemCount()):
                    tree_widget.topLevelItem(j).setText(tree_widget.columnCount() - 1, '')

            status_column = tree_widget.columnCount() - 1

            for j in range(tree_widget.topLevelItemCount()):
                item = tree_widget.topLevelItem(j)
                if item.checkState(0) == QtCore.Qt.Checked:
                    wms_link = item.data(0, QtCore.Qt.UserRole)
                    if wms_link:
                        logger.debug(f"Checking WMS status for: {wms_link}")
                        status = check_wms_availability(wms_link)
                        item.setText(status_column, status)
                    else:
                        logger.warning(f"No WMS link found for selected item {j} in tab {i}")
                else:
                    item.setText(status_column, '')  # Clear status for unchecked items

    def get_selected_items(self):
        logger.info("Getting selected items")
        selected_items = []
        for i in range(self.tabWidget.count()):
            tree_widget = self.tabWidget.widget(i).findChild(QtWidgets.QTreeWidget)
            for j in range(tree_widget.topLevelItemCount()):
                item = tree_widget.topLevelItem(j)
                if item.checkState(0) == QtCore.Qt.Checked:
                    selected_items.append(item)
        logger.debug(f"Found {len(selected_items)} selected items")
        return selected_items

class QGISWebScraperLayerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select WMS Layers")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        self.layerTreeWidget = QtWidgets.QTreeWidget()
        self.layerTreeWidget.setHeaderLabels(["Layer Name", "Title"])
        layout.addWidget(self.layerTreeWidget)

        self.addLayerButton = QtWidgets.QPushButton("Add Selected Layers")
        layout.addWidget(self.addLayerButton)

    def get_selected_items(self):
        selected_items = []
        for i in range(self.layerTreeWidget.topLevelItemCount()):
            item = self.layerTreeWidget.topLevelItem(i)
            if item.checkState(0) == QtCore.Qt.Checked:
                selected_items.append(item)
        return selected_items