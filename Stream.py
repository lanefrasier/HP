import requests
from bs4 import BeautifulSoup
import pandas as pd

# Set URL and metadata
url = "https://www.mystream.com/en/historical-rates/texas.html"
brand = "Stream"
language = "EN"

# Use headers to avoid bot-block
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Fetch and parse page
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

all_data = []

# Find each plan's h3 and follow-up table
for h3 in soup.find_all("h3"):
    plan_name = h3.get_text(strip=True)

    # The pricing table is within the next div with class "historical-rates"
    historical_rates_div = h3.find_next("div", class_="historical-rates")
    if not historical_rates_div:
        continue

    table = historical_rates_div.find("table")
    if not table:
        continue

    # Extract header
    headers_row = table.find("tr")
    if not headers_row:
        continue

    headers = [th.get_text(strip=True) for th in headers_row.find_all("th")]

    # Extract data rows
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) != len(headers):
            continue

        row_data = {
            "Plan Name": plan_name,
            "Brand": brand,
            "Language": language
        }
        for header_text, cell in zip(headers, cells):
            row_data[header_text] = cell.get_text(strip=True)
        all_data.append(row_data)

# Write to Excel
df = pd.DataFrame(all_data)
df.to_excel("stream_energy_historical_rates.xlsx", index=False)

print("✅ Stream pricing scraped and saved to 'stream_energy_historical_rates.xlsx'")
