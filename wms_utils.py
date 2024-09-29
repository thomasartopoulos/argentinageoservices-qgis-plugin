import re
import requests
from xml.etree import ElementTree as ET
from qgis.core import QgsRasterLayer, QgsProject
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import pandas as pd
from .wms_checker import clean_url

def load_wms_layers(wms_link, tree_widget):
    wms_link = clean_url(wms_link)
    get_capabilities_url = f"{wms_link}?SERVICE=WMS&REQUEST=GetCapabilities"
    try:
        response = requests.get(get_capabilities_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Error", f"Failed to get WMS capabilities from {wms_link}: {str(e)}")
        return

    try:
        tree = ET.fromstring(response.content)
        layers = tree.findall(".//{http://www.opengis.net/wms}Layer")

        for layer in layers:
            name_element = layer.find("{http://www.opengis.net/wms}Name")
            title_element = layer.find("{http://www.opengis.net/wms}Title")
            if name_element is not None and title_element is not None:
                name = name_element.text
                title = title_element.text
                item = QTreeWidgetItem([name, title])
                item.setCheckState(0, Qt.Unchecked)
                item.setData(0, Qt.UserRole, wms_link)
                tree_widget.addTopLevelItem(item)
    except ET.ParseError as e:
        QMessageBox.critical(None, "Error", f"Failed to parse WMS capabilities from {wms_link}: {str(e)}")

def add_wms_layer(layer_name, wms_link):
    wms_link = clean_url(wms_link)
    uri = f"contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers={layer_name}&styles=&url={wms_link}"
    layer = QgsRasterLayer(uri, layer_name, "wms")
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)
    else:
        QMessageBox.critical(None, "Error", f"Failed to add WMS layer {layer_name} from {wms_link}")