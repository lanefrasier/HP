import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Define the base URLs and their corresponding language and brand
urls = [
    ("https://www.directenergy.com/en/historical-pricing/", "EN", "Direct Energy"),
    ("https://www.directenergy.com/es/historical-pricing/", "ES", "Direct Energy")
]

all_plans = []

for base_url, language, brand in urls:

    # Make the request and parse HTML
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Path filters for brands that use link-based plans
    if brand == "Direct Energy":
        path_filter = "/historical-pricing/texas"
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

