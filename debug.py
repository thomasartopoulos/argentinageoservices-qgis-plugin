import requests
import pandas as pd
import io
import re

def clean_url(url):
    if pd.isna(url):
        return url
    url = re.sub(r'\[WMS\]', '', url)
    url = url.replace('(', '').replace(')', '')
    return url.strip()

def parse_csv(content, url):
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
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')
            
            df = parse_csv(csv_content, url)
            if df is not None:
                if 'WMS' in df.columns:
                    df['WMS'] = df['WMS'].apply(clean_url)
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

# Test the function
data = scrape_web_page()
for i, df in data.items():
    if df is not None:
        print(f"Data for URL {i}:")
        print(df.head())
        print("\n")
    else:
        print(f"No data available for URL {i}\n")