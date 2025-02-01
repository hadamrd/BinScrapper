from tqdm import tqdm
from BinDatabase import BinDatabase
from BinScraper import scrape_bank_page
import time

db = BinDatabase()
total_urls = db.get_total_urls_count()
processed_urls = db.get_processed_urls_count()

with tqdm(total=total_urls, initial=processed_urls) as pbar:
    unprocessed_urls = db.get_unprocessed_urls()
    for url_data in unprocessed_urls:
        bank_table = scrape_bank_page(url_data['url'])
        if bank_table:
            db.insert_bank_data(bank_table, url_data['id'])
        db.mark_url_processed(url_data['id'])
        pbar.update(1)
        time.sleep(0.5)

db.close()