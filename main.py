import os
import requests
import pandas as pd
import io
import re
import urllib.parse
from xml.etree import ElementTree as ET
from qgis.core import QgsRasterLayer, QgsProject, QgsDataSourceUri
from qgis.PyQt.QtCore import QCoreApplication, QVariant, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QTreeWidgetItem, QDialog
from .QGISWebScraper_dialog import Ui_QGISWebScraperDialogBase
from .QGISWebScraperLayerDialog import Ui_QGISWebScraperLayerDialog

class QGISWebScraper:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)  # Correctly define plugin_dir
        self.dialog = None
        self.layer_dialog = None
        self.layer_data = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'resources/sol_de_mayo.png')
        self.action = QAction(QIcon(icon_path), "ArgentinaGeoServices", self.iface.mainWindow())
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
            self.ui.importButton.clicked.connect(self.show_wms_layers)

        self.layer_data = self.scrape_web_page()
        if self.layer_data is not None:
            self.ui.wmsTreeWidget.clear()
            for _, row in self.layer_data.iterrows():
                organismo = row['Organismo']
                wms_link = row['WMS']
                item = QTreeWidgetItem([organismo, wms_link])
                item.setCheckState(0, Qt.Unchecked)
                # Store the WMS link in the item's data
                item.setData(0, Qt.UserRole, wms_link)
                self.ui.wmsTreeWidget.addTopLevelItem(item)

        self.dialog.show()

    def scrape_web_page(self):
        url = "https://datawrapper.dwcdn.net/nH8e7/45/dataset.csv"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://datawrapper.dwcdn.net/nH8e7/45/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            csv_content = response.content.decode('utf-8')
            csv_buffer = io.StringIO(csv_content)
            try:
                data = pd.read_csv(csv_buffer, delimiter='\t')
                def clean_url(url):
                    if pd.isna(url):
                        return url
                    url = re.sub(r'\[WMS\]|\[WFS\]|\[WCS\]', '', url)
                    url = url.replace('(', '').replace(')', '')
                    return url.strip()

                for col in ['WMS', 'WFS', 'WCS']:
                    data[col] = data[col].apply(clean_url)

                return data
            except pd.errors.EmptyDataError:
                print("No data found in the CSV file.")
                return None
            except pd.errors.ParserError:
                print("Error parsing the CSV file.")
                return None
        else:
            print(f"Failed to download the file: Status code {response.status_code}")
            return None

    def show_wms_layers(self):
        if self.layer_data is None:
            QMessageBox.warning(None, "Error", "No data available.")
            return

        selected_items = [item for item in [self.ui.wmsTreeWidget.topLevelItem(i)
                                            for i in range(self.ui.wmsTreeWidget.topLevelItemCount())]
                        if item.checkState(0) == Qt.Checked]

        if not selected_items:
            QMessageBox.warning(None, "No Selection", "No WMS endpoints selected.")
            return

        # Ensure only one WMS can be selected
        if len(selected_items) > 1:
            QMessageBox.warning(None, "Selection Error", "You can only select one WMS endpoint.")
            # Uncheck all items except the first one
            for item in self.ui.wmsTreeWidget.topLevelItems():
                item.setCheckState(0, Qt.Unchecked)
            selected_items[0].setCheckState(0, Qt.Checked)
            selected_items = [selected_items[0]]

        if self.layer_dialog is None:
            self.layer_dialog = QDialog()
            self.layer_ui = Ui_QGISWebScraperLayerDialog()
            self.layer_ui.setupUi(self.layer_dialog)
            self.layer_ui.addLayerButton.clicked.connect(self.add_selected_layers)

        self.layer_ui.layerTreeWidget.clear()
        for item in selected_items:
            wms_link = item.data(0, Qt.UserRole)  # Retrieve the WMS link from the item's data
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
                item.setCheckState(0, Qt.Unchecked)
                # Store the WMS link in the item's data
                item.setData(0, Qt.UserRole, wms_link)
                self.layer_ui.layerTreeWidget.addTopLevelItem(item)

    def add_selected_layers(self):
        selected_items = [item for item in [self.layer_ui.layerTreeWidget.topLevelItem(i)
                                            for i in range(self.layer_ui.layerTreeWidget.topLevelItemCount())]
                          if item.checkState(0) == Qt.Checked]

        for item in selected_items:
            layer_name = item.text(0)
            wms_link = item.data(0, Qt.UserRole)
            if not wms_link:
                QMessageBox.critical(None, "Error", f"No WMS link found for layer {layer_name}.")
                continue

            uri = f"contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers={layer_name}&styles=&url={wms_link}"
            layer = QgsRasterLayer(uri, layer_name, "wms")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
            else:
                QMessageBox.critical(None, "Error", f"Failed to add WMS layer {layer_name} from {wms_link}")