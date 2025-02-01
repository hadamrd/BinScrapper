# bin_manager/app/url_collection_worker.py
import asyncio
from datetime import datetime
from bin_manager.db.database import BinDatabase
from bin_manager.scraper.scraper import BinScraper, ScraperConfig
from bin_manager.app.state import state_manager

async def url_collection_worker():
    """Background worker for collecting bank URLs."""
    db = BinDatabase()
    scraper = BinScraper(ScraperConfig(delay=0.8))
    
    try:
        # Reset status at start
        state_manager.update_url_status(
            is_running=True,
            start_time=datetime.now(),
            total_countries=0,
            processed_countries=0,
            current_country='',
            collected_urls=0,
            failed_countries=[]
        )
        
        # Get country list
        scraper.logger.info("Fetching country list...")
        country_hrefs = scraper.get_countries_list()
        
        if not country_hrefs:
            scraper.logger.error("No countries found!")
            return
            
        state_manager.update_url_status(total_countries=len(country_hrefs))
        scraper.logger.info(f"Found {len(country_hrefs)} countries to process")
        
        for href in country_hrefs:
            if not state_manager.url_collection_status['is_running']:
                scraper.logger.warning("Collection stopped by user")
                break
                
            country_name = href.split('/')[-1]
            scraper.logger.info(f"Processing country: {country_name}")
            
            state_manager.update_url_status(current_country=country_name)
            
            try:
                country_url = scraper.config.base_url + href
                country_banks_hrefs = scraper.get_country_banks(country_url)
                
                if country_banks_hrefs:
                    db.insert_bank_urls(country_banks_hrefs)
                    current_urls = state_manager.url_collection_status['collected_urls']
                    state_manager.update_url_status(
                        collected_urls=current_urls + len(country_banks_hrefs)
                    )
                    scraper.logger.info(f"Collected {len(country_banks_hrefs)} URLs from {country_name}")
                else:
                    failed_countries = state_manager.url_collection_status['failed_countries']
                    failed_countries.append(country_name)
                    state_manager.update_url_status(failed_countries=failed_countries)
                    scraper.logger.info(f"No URLs found for {country_name}")
                
                current_processed = state_manager.url_collection_status['processed_countries']
                state_manager.update_url_status(processed_countries=current_processed + 1)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                scraper.logger.error(f"Error processing {country_name}: {str(e)}")
                failed_countries = state_manager.url_collection_status['failed_countries']
                failed_countries.append(country_name)
                state_manager.update_url_status(failed_countries=failed_countries)
                continue
                
    finally:
        state_manager.update_url_status(
            is_running=False,
            current_country=''
        )
        db.close()
        scraper.logger.info("URL collection completed")