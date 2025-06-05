import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Define the base URLs and their corresponding language codes
urls = [
    ("https://myaccount.greenmountainenergy.com/en_US/PriceHistoryPages/pricehistoryindex.html", "EN", "GME"),
    ("https://myaccount.greenmountainenergy.com/es_US/PriceHistoryPages/pricehistoryindex.html", "ES", "GME")
]

all_plans = []

for base_url, language, brand in urls:
    # Send request
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    for base_url, language, brand in urls:
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Accept any non-empty text and valid href
                if href.startswith('http') or href.startswith('/'):
                    full_url = urljoin(base_url, href)
                    plan_name = a_tag.get_text(strip=True)
                    if plan_name:
                        all_plans.append({
                            'Plan Name': plan_name,
                            'URL': full_url,
                            'Language': language,
                            'Brand': brand
                        })
        except Exception as e:
            print(f"Failed to scrape {base_url}: {e}")

# Remove duplicate URLs
df = pd.DataFrame({entry['URL']: entry for entry in all_plans}.values())

# Save to Excel
df.to_excel('gme_plans.xlsx', index=False)

print("Scraping complete. Results saved to 'gme_plans.xlsx'.")
