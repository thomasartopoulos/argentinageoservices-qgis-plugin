import requests
import pandas as pd
import io
import logging
from .wms_utils import clean_url
from .wms_checker import check_wms_availability

logger = logging.getLogger(__name__)

def parse_csv(content, url):
    try:
        logger.debug(f"Parsing CSV from URL: {url}")
        logger.debug(f"CSV content preview: {content[:200]}...")  # Log the first 200 characters of the CSV

        if "JJpjQ" in url:  # Special handling for Organismos Provinciales
            df = pd.read_csv(io.StringIO(content), sep='\t', encoding='utf-8', dtype=str)
            df = df.iloc[:, :3]
            df.columns = ['Provincia', 'Organismo', 'WMS']
        else:
            df = pd.read_csv(io.StringIO(content), sep='\t', encoding='utf-8', dtype=str)
        
        df = df.iloc[:, :3]
        logger.debug(f"Parsed DataFrame shape: {df.shape}")
        logger.debug(f"Parsed DataFrame columns: {df.columns}")
        logger.debug(f"First few rows of parsed DataFrame:\n{df.head()}")
        return df
    except Exception as e:
        logger.exception(f"Error parsing CSV from {url}: {str(e)}")
        return None

def scrape_web_page():
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
            logger.info(f"Fetching data from URL: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')
            
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response content preview: {csv_content[:200]}...")  # Log the first 200 characters
            
            df = parse_csv(csv_content, url)
            if df is not None and not df.empty:
                if 'WMS' in df.columns:
                    df['WMS'] = df['WMS'].apply(clean_url)
                    df['Status'] = 'Unchecked'  # Initialize status as unchecked
                data[i] = df
                
                logger.info(f"Successfully processed {url}")
                logger.info(f"DataFrame shape: {df.shape}")
                logger.info(f"DataFrame columns: {df.columns}")
            else:
                logger.warning(f"Failed to process {url} or DataFrame is empty")
        except Exception as e:
            logger.exception(f"Error processing {url}: {str(e)}")
            data[i] = None

    logger.info(f"Total datasets processed: {len(data)}")
    return data