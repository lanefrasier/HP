import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Define the base URLs and their corresponding language and brand
urls = [
    ("https://www.reliant.com/en/historical-pricing", "EN", "Reliant"),
    ("https://www.reliant.com/es/historical-pricing", "ES", "Reliant"),
    ("https://myaccount.greenmountainenergy.com/en_US/PriceHistoryPages/pricehistoryindex.html", "EN", "GME"),
    ("https://myaccount.greenmountainenergy.com/es_US/PriceHistoryPages/pricehistoryindex.html", "ES", "GME")
]

all_plans = []

for base_url, language, brand in urls:
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Choose correct path filter
    if brand == "Reliant":
        path_filter = "/historical-pricing/"
    elif brand == "GME":
        path_filter = "/PriceHistoryPages/"
    else:
        continue  # In case of unexpected brand

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if path_filter in href:
            full_url = urljoin(base_url, href)
            plan_name = a_tag.get_text(strip=True)
            if plan_name:
                all_plans.append({
                    'Plan Name': plan_name,
                    'URL': full_url,
                    'Language': language,
                    'Brand': brand
                })

# Remove duplicates based on URL
df = pd.DataFrame({entry['URL']: entry for entry in all_plans}.values())

# Save to Excel
df.to_excel('pricing_plans.xlsx', index=False)

print("Scraping complete. Results saved to 'pricing_plans.xlsx'.")
