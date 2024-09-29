import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def classFactory(iface):
    logger.debug("classFactory called")
    try:
        from .main import QGISWebScraper
        logger.debug("QGISWebScraper imported successfully")
        return QGISWebScraper(iface)
    except Exception as e:
        logger.exception("Error in classFactory")
        raise