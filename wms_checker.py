import requests
import re
import pandas as pd

def clean_url(url):
    if pd.isna(url):
        return url
    url = re.sub(r'\[WMS\]', '', url)
    url = url.replace('(', '').replace(')', '')
    return url.strip()

def check_wms_availability(wms_link):
    try:
        wms_link = clean_url(wms_link)
        get_capabilities_url = f"{wms_link}?SERVICE=WMS&REQUEST=GetCapabilities"
        response = requests.get(get_capabilities_url, timeout=10)
        if response.status_code == 200:
            return "Available"
        else:
            return "Not Available"
    except requests.exceptions.RequestException:
        return "Not Available"