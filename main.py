import os
import requests
import pandas as pd
import io
import re
from xml.etree import ElementTree as ET
from qgis.core import QgsRasterLayer, QgsProject
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem, QDialog, QTabWidget, QWidget, QVBoxLayout, QMessageBox

class Ui_QGISWebScraperDialogBase(object):
    def setupUi(self, QGISWebScraperDialogBase):
        QGISWebScraperDialogBase.setObjectName("QGISWebScraperDialogBase")
        QGISWebScraperDialogBase.resize(600, 500)

        # Set window icon here
        QGISWebScraperDialogBase.setWindowIcon(QtGui.QIcon('resources/sol_de_mayo.png'))

        self.verticalLayout = QtWidgets.QVBoxLayout(QGISWebScraperDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QTabWidget(QGISWebScraperDialogBase)
        self.verticalLayout.addWidget(self.tabWidget)

        self.importButton = QtWidgets.QPushButton(QGISWebScraperDialogBase)
        self.importButton.setObjectName("importButton")
        self.verticalLayout.addWidget(self.importButton)

        self.retranslateUi(QGISWebScraperDialogBase)
        QtCore.QMetaObject.connectSlotsByName(QGISWebScraperDialogBase)

    def retranslateUi(self, QGISWebScraperDialogBase):
        _translate = QtCore.QCoreApplication.translate
        QGISWebScraperDialogBase.setWindowTitle(_translate("QGISWebScraperDialogBase", "ArgentinaGeoServices"))
        self.importButton.setText(_translate("QGISWebScraperDialogBase", "Import Selected WMS"))

class Ui_QGISWebScraperLayerDialog(object):
    def setupUi(self, QGISWebScraperLayerDialog):
        QGISWebScraperLayerDialog.setObjectName("QGISWebScraperLayerDialog")
        QGISWebScraperLayerDialog.resize(400, 300)

        self.verticalLayout = QtWidgets.QVBoxLayout(QGISWebScraperLayerDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.layerTreeWidget = QtWidgets.QTreeWidget(QGISWebScraperLayerDialog)
        self.layerTreeWidget.setObjectName("layerTreeWidget")
        self.layerTreeWidget.setColumnCount(2)
        self.layerTreeWidget.setHeaderLabels(["Layer Name", "Title"])
        self.verticalLayout.addWidget(self.layerTreeWidget)

        self.addLayerButton = QtWidgets.QPushButton(QGISWebScraperLayerDialog)
        self.addLayerButton.setObjectName("addLayerButton")
        self.verticalLayout.addWidget(self.addLayerButton)

        self.retranslateUi(QGISWebScraperLayerDialog)
        QtCore.QMetaObject.connectSlotsByName(QGISWebScraperLayerDialog)

    def retranslateUi(self, QGISWebScraperLayerDialog):
        _translate = QtCore.QCoreApplication.translate
        QGISWebScraperLayerDialog.setWindowTitle(_translate("QGISWebScraperLayerDialog", "Select WMS Layers"))
        self.addLayerButton.setText(_translate("QGISWebScraperLayerDialog", "Add Selected Layers"))

class QGISWebScraper:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None
        self.layer_dialog = None
        self.layer_data = None
        self.ui = None

    def initGui(self):
        icon_path = 'resources/sol_de_mayo.png'
        self.action = QtWidgets.QAction(QtGui.QIcon(icon_path), "ArgentinaGeoServices", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&ArgentinaGeoServices", self.action)

    def unload(self):
        self.iface.removePluginMenu("&ArgentinaGeoServices", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.dialog is None:
            self.dialog = QDialog()
            self.ui = Ui_QGISWebScraperDialogBase()
            self.ui.setupUi(self.dialog)
            self.ui.importButton.clicked.connect(self.import_selected_wms_layers)

        # Load WMS layers into the tabs
        self.layer_data = self.scrape_web_page()
        if self.layer_data is not None:
            self.populate_tabs_with_layers()
        else:
            QMessageBox.warning(None, "Data Retrieval Error", "Failed to retrieve data from some or all sources.")

        self.dialog.show()

    def clean_url(self, url):
        if pd.isna(url):
            return url
        url = re.sub(r'\[WMS\]', '', url)
        url = url.replace('(', '').replace(')', '')
        return url.strip()

    def parse_csv(self, content, url):
        try:
            if "JJpjQ" in url:  # Special handling for Organismos Provinciales
                df = pd.read_csv(io.StringIO(content), sep='\t', encoding='utf-8', dtype=str)
                # Keep only the first three columns
                df = df.iloc[:, :3]
                # Rename columns to match expected structure
                df.columns = ['Provincia', 'Organismo', 'WMS']
            else:
                df = pd.read_csv(io.StringIO(content), sep='\t', encoding='utf-8', dtype=str)
            
            # Ensure we only keep the first three columns for all datasets
            df = df.iloc[:, :3]
            
            return df
        except Exception as e:
            print(f"Error parsing CSV: {str(e)}")
            return None

    def scrape_web_page(self):
        urls = [
            "https://datawrapper.dwcdn.net/nH8e7/45/dataset.csv",  # Organismos Nacionales
            "https://datawrapper.dwcdn.net/JJpjQ/34/dataset.csv",  # Organismos Provinciales
            "https://datawrapper.dwcdn.net/bGS4P/29/dataset.csv",  # Organismos Municipales
            "https://datawrapper.dwcdn.net/Dp6Aq/14/dataset.csv",  # Universidades
            "https://datawrapper.dwcdn.net/wqjGw/5/dataset.csv"    # Empresas
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        data = {}

        for i, url in enumerate(urls):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                csv_content = response.content.decode('utf-8')
                
                df = self.parse_csv(csv_content, url)
                if df is not None:
                    if 'WMS' in df.columns:
                        df['WMS'] = df['WMS'].apply(self.clean_url)
                    data[i] = df
                    
                    print(f"Successfully processed {url}")
                    print(f"DataFrame shape: {df.shape}")
                    print(f"DataFrame columns: {df.columns}")
                else:
                    print(f"Failed to process {url}")
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
                data[i] = None

        return data

    def populate_tabs_with_layers(self):
        if self.ui is None or self.ui.tabWidget is None:
            print("UI or tabWidget is not initialized")
            return

        self.ui.tabWidget.clear()
        tab_names = ["Organismos Nacionales", "Organismos Provinciales", "Organismos Municipales", "Universidades", "Empresas"]

        for i, tab_name in enumerate(tab_names):
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tree_widget = QtWidgets.QTreeWidget()

            if i in self.layer_data and self.layer_data[i] is not None:
                data = self.layer_data[i]
                header_labels = data.columns.tolist()
                tree_widget.setHeaderLabels(header_labels)

                for _, row in data.iterrows():
                    values = [str(row[col]) if not pd.isna(row[col]) else '' for col in header_labels]
                    item = QTreeWidgetItem(values)
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                    item.setData(0, QtCore.Qt.UserRole, row['WMS'])
                    tree_widget.addTopLevelItem(item)
            else:
                tree_widget.setHeaderLabels(['Info'])
                item = QTreeWidgetItem([f"No data available for {tab_name}."])
                tree_widget.addTopLevelItem(item)

            tab_layout.addWidget(tree_widget)
            self.ui.tabWidget.addTab(tab_widget, tab_name)

    def import_selected_wms_layers(self):
        selected_items = []

        # Iterate through all the tabs to collect selected WMS layers
        for i in range(self.ui.tabWidget.count()):
            tree_widget = self.ui.tabWidget.widget(i).findChild(QtWidgets.QTreeWidget)
            for j in range(tree_widget.topLevelItemCount()):
                item = tree_widget.topLevelItem(j)
                if item.checkState(0) == QtCore.Qt.Checked:
                    selected_items.append(item)

        if not selected_items:
            QMessageBox.warning(None, "No Selection", "No WMS layers selected.")
            return

        if self.layer_dialog is None:
            self.layer_dialog = QDialog()
            self.layer_ui = Ui_QGISWebScraperLayerDialog()
            self.layer_ui.setupUi(self.layer_dialog)
            self.layer_ui.addLayerButton.clicked.connect(self.add_selected_layers)

        self.layer_ui.layerTreeWidget.clear()
        for item in selected_items:
            wms_link = item.data(0, QtCore.Qt.UserRole)  # Retrieve the WMS link from the item's data
            self.load_wms_layers(wms_link)

        self.layer_dialog.show()

    def load_wms_layers(self, wms_link):
        get_capabilities_url = f"{wms_link}?SERVICE=WMS&REQUEST=GetCapabilities"
        response = requests.get(get_capabilities_url)

        if response.status_code != 200:
            QMessageBox.critical(None, "Error", f"Failed to get WMS capabilities from {wms_link}")
            return

        tree = ET.fromstring(response.content)
        layers = tree.findall(".//{http://www.opengis.net/wms}Layer")

        self.layer_ui.layerTreeWidget.clear()
        for layer in layers:
            name_element = layer.find("{http://www.opengis.net/wms}Name")
            title_element = layer.find("{http://www.opengis.net/wms}Title")
            if name_element is not None and title_element is not None:
                name = name_element.text
                title = title_element.text
                item = QTreeWidgetItem([name, title])
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.setData(0, QtCore.Qt.UserRole, wms_link)
                self.layer_ui.layerTreeWidget.addTopLevelItem(item)

    def add_selected_layers(self):
        selected_items = [item for item in [self.layer_ui.layerTreeWidget.topLevelItem(i)
                                            for i in range(self.layer_ui.layerTreeWidget.topLevelItemCount())]
                          if item.checkState(0) == QtCore.Qt.Checked]

        for item in selected_items:
            layer_name = item.text(0)
            wms_link = item.data(0, QtCore.Qt.UserRole)
            if not wms_link:
                QMessageBox.critical(None, "Error", f"No WMS link found for layer {layer_name}.")
                continue

            uri = f"contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers={layer_name}&styles=&url={wms_link}"
            layer = QgsRasterLayer(uri, layer_name, "wms")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
            else:
                QMessageBox.critical(None, "Error", f"Failed to add WMS layer {layer_name} from {wms_link}")