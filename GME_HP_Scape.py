import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from io import StringIO
import os

HEADERS = {'User-Agent': 'Mozilla/5.0'}

urls = [
    ("https://myaccount.greenmountainenergy.com/en_US/PriceHistoryPages/pricehistoryindex.html", "EN"),
    ("https://myaccount.greenmountainenergy.com/es_US/PriceHistoryPages/pricehistoryindex.html", "ES")
]

brand = "GME"
path_filter = "/PriceHistoryPages/"
all_data = []

output_path = r"C:\Users\LFrasier\NRG Energy, Inc\Digital Operations-NRG365 - General\Historical Pricing\PowerBi\gme_combined_historical_prices.xlsx"

for base_url, language in urls:
    try:
        response = requests.get(base_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if path_filter in href:
                full_url = urljoin(base_url, href)
                plan_name = a_tag.get_text(strip=True)
                if full_url and plan_name:
                    plan_resp = requests.get(full_url, headers=HEADERS)
                    plan_resp.raise_for_status()
                    plan_soup = BeautifulSoup(plan_resp.text, 'html.parser')
                    tables = plan_soup.find_all('table')

                    for table in tables:
                        html_table = str(table)
                        df = pd.read_html(StringIO(html_table))[0]
                        df.insert(0, 'Plan Name', plan_name)
                        df.insert(1, 'Language', language)
                        df.insert(2, 'Brand', brand)
                        all_data.append(df)
    except Exception as e:
        print(f"Failed to process {base_url}: {e}")

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_excel(output_path, index=False)
    print(f"Saved to: {output_path}")
else:
    print("No data extracted.")
