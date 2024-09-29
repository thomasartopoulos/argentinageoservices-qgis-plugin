import os
import logging
from qgis.core import QgsProject
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from .ui import QGISWebScraperDialog, QGISWebScraperLayerDialog
from .scraper import scrape_web_page
from .wms_utils import load_wms_layers, add_wms_layer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class QGISWebScraper:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None
        self.layer_dialog = None
        self.layer_data = None

    def initGui(self):
        icon_path = 'resources/sol_de_mayo.png'
        self.action = QAction(QIcon(icon_path), "ArgentinaGeoServices", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&ArgentinaGeoServices", self.action)

    def unload(self):
        self.iface.removePluginMenu("&ArgentinaGeoServices", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        logger.info("Plugin run method called")
        if self.dialog is None:
            logger.debug("Creating new QGISWebScraperDialog")
            self.dialog = QGISWebScraperDialog()
            self.dialog.importButton.clicked.connect(self.import_selected_wms_layers)
            self.dialog.checkStatusButton.clicked.connect(self.check_selected_wms_status)

        logger.info("Scraping web page for layer data")
        self.layer_data = scrape_web_page()
        if self.layer_data is not None:
            logger.info(f"Layer data retrieved. Number of datasets: {len(self.layer_data)}")
            self.dialog.populate_tabs_with_layers(self.layer_data)
        else:
            logger.error("Failed to retrieve layer data")
            QMessageBox.warning(None, "Data Retrieval Error", "Failed to retrieve data from some or all sources.")

        logger.info("Showing dialog")
        self.dialog.show()

    def check_selected_wms_status(self):
        logger.info("Checking selected WMS status")
        self.dialog.check_selected_wms_status()

    def import_selected_wms_layers(self):
        logger.info("Importing selected WMS layers")
        selected_items = self.dialog.get_selected_items()

        if not selected_items:
            logger.warning("No WMS layers selected")
            QMessageBox.warning(None, "No Selection", "No WMS layers selected.")
            return

        if self.layer_dialog is None:
            logger.debug("Creating new QGISWebScraperLayerDialog")
            self.layer_dialog = QGISWebScraperLayerDialog()
            self.layer_dialog.addLayerButton.clicked.connect(self.add_selected_layers)

        self.layer_dialog.layerTreeWidget.clear()
        for item in selected_items:
            wms_link = item.data(0, Qt.UserRole)
            logger.debug(f"Loading WMS layers for link: {wms_link}")
            load_wms_layers(wms_link, self.layer_dialog.layerTreeWidget)

        logger.info("Showing layer dialog")
        self.layer_dialog.show()

    def add_selected_layers(self):
        logger.info("Adding selected layers")
        selected_items = self.layer_dialog.get_selected_items()

        for item in selected_items:
            layer_name = item.text(0)
            wms_link = item.data(0, Qt.UserRole)
            if not wms_link:
                logger.warning(f"No WMS link found for layer {layer_name}")
                QMessageBox.critical(None, "Error", f"No WMS link found for layer {layer_name}.")
                continue

            logger.debug(f"Adding WMS layer: {layer_name} from {wms_link}")
            add_wms_layer(layer_name, wms_link)

        logger.info("Finished adding selected layers")