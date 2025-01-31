from BinDatabase import BinDatabase
from BinScraper import scrap_countries_pages_hrefs, scrape_country_page, base_url
import time

db = BinDatabase()

# First pass: collect all bank URLs
hrefs = scrap_countries_pages_hrefs()
for href in hrefs:
    country_url = f"{base_url}{href}"
    print(f"Collecting URLs from: {country_url}")
    country_banks_hrefs = scrape_country_page(country_url)
    db.insert_bank_urls(country_banks_hrefs)
    time.sleep(0.5)