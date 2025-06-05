import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Define the base URLs and their corresponding language and brand
urls = [
    ("https://www.reliant.com/en/historical-pricing", "EN", "Reliant"),
    ("https://www.reliant.com/es/historical-pricing", "ES", "Reliant"),
    ("https://myaccount.greenmountainenergy.com/en_US/PriceHistoryPages/pricehistoryindex.html", "EN", "GME"),
    ("https://myaccount.greenmountainenergy.com/es_US/PriceHistoryPages/pricehistoryindex.html", "ES", "GME"),
    ("https://www.directenergy.com/en/historical-pricing/", "EN", "Direct Energy"),
    ("https://www.directenergy.com/es/historical-pricing/", "ES", "Direct Energy"),
    ("https://www.cirroenergy.com/lp/smartflex", "EN", "Cirro"),
    ("https://www.cirroenergy.com/en_US/lp/SmartFlex_ES", "ES", "Cirro"),
    ("https://www.discountpowertx.com/en/about/historical-pricing/price-history-index", "EN", "Discount Power"),
    ("https://www.discountpowertx.com/es/about/historical-pricing/price-history-index", "ES", "Discount Power")
]

all_plans = []

for base_url, language, brand in urls:
    # Cirro plans are hardcoded — no scraping needed
    if brand == "Cirro":
        all_plans.append({
            'Plan Name': "Smart Flex Plan",
            'URL': base_url,
            'Language': language,
            'Brand': brand
        })
        continue

    # Make the request and parse HTML
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Discount Power dropdown scraping
    if brand == "Discount Power":
        select_tag = soup.find("select")  # no need for ID since there's only one on the page
        if select_tag:
            for option in select_tag.find_all("option"):
                href = option.get("value")
                plan_name = option.get_text(strip=True)
                if href and plan_name and href != "#":
                    full_url = urljoin(base_url, href)
                    all_plans.append({
                        'Plan Name': plan_name,
                        'URL': full_url,
                        'Language': language,
                        'Brand': brand
                    })
        continue

    # Path filters for brands that use link-based plans
    if brand == "Reliant":
        path_filter = "/historical-pricing/"
    elif brand == "Direct Energy":
        path_filter = "/historical-pricing/texas"
    elif brand == "GME":
        path_filter = "/PriceHistoryPages/"
    else:
        continue  # skip unknowns

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
