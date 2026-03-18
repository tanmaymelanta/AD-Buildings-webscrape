import pandas as pd
import os
import re
import time
from playwright.sync_api import sync_playwright

# Load data
df = pd.read_excel("residential building joined.xlsx")
df = df.iloc[0:1000]

xpath = '//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div'

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", str(name))

os.makedirs("data", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for _, row in df.iterrows():
        try:
            lat = row['centroid_lat']
            lon = row['centroid_lon']
            name = clean_filename(row['name'])

            url = f'https://maps.urbi.ae/dubai/geo/{lon}%2C{lat}?m=54.571762%2C24.415654%2F18.72'
            print(f"Scraping: {url}")

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            element = page.locator(f"xpath={xpath}")
            element.wait_for(timeout=10000)

            text = element.inner_text()

            with open(f"data/{name}.txt", "w", encoding="utf-8") as f:
                f.write(text)

            time.sleep(2)  # avoid being flagged as bot

        except Exception as e:
            print(f"Failed for {row.get('name', 'unknown')}: {e}")

    browser.close()
