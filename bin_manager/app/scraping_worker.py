# bin_manager/app/scraping_worker.py
import asyncio
from datetime import datetime
from bin_manager.db.database import BinDatabase
from bin_manager.scraper.scraper import BinScraper, ScraperConfig
from bin_manager.app.state import state_manager

def format_bank_name(name: str, max_length: int = 20) -> str:
    """Format bank name for consistent display."""
    if len(name) <= max_length:
        return name.ljust(max_length)
    return name[:max_length-3] + "..."

async def scraping_worker():
    """Background worker for scraping BIN data."""
    config = ScraperConfig(
        retry_attempts=5,
        retry_backoff=2,
        timeout=15,
        delay=0.8
    )
    
    scraper = BinScraper(config)
    db = BinDatabase()
    
    try:
        # Initialize session statistics
        total_urls = db.get_total_urls_count()
        processed_urls = db.get_processed_urls_count()
        
        state_manager.update_scraping_status(
            is_running=True,
            start_time=datetime.now(),
            total_banks=total_urls,
            processed_banks=processed_urls,
            processed_bins=0
        )
        
        scraper.logger.info(f"Starting scraping session - {total_urls - processed_urls:,} banks remaining")
        
        unprocessed_urls = db.get_unprocessed_urls()
        for url_data in unprocessed_urls:
            if not state_manager.scraping_status['is_running']:
                scraper.logger.warning("Scraping stopped by user")
                break
                
            try:
                bank_name = url_data['url'].split('/')[-1]
                formatted_name = format_bank_name(bank_name)
                
                state_manager.update_scraping_status(
                    current_bank=formatted_name
                )
                
                scraper.logger.info(f"Processing bank: {bank_name}")
                bank_table = scraper.get_bank_bins(url_data['url'])
                
                if bank_table:
                    db.insert_bank_data(bank_table, url_data['id'])
                    current_bins = state_manager.scraping_status['processed_bins']
                    state_manager.update_scraping_status(
                        processed_bins=current_bins + len(bank_table)
                    )
                    scraper.logger.info(f"Collected {len(bank_table)} BINs from {bank_name}")
                else:
                    failed_urls = state_manager.scraping_status['failed_urls']
                    failed_urls.append(url_data['url'])
                    state_manager.update_scraping_status(failed_urls=failed_urls)
                    scraper.logger.warning(f"No BINs found for {bank_name}")
                
                db.mark_url_processed(url_data['id'])
                current_processed = state_manager.scraping_status['processed_banks']
                state_manager.update_scraping_status(
                    processed_banks=current_processed + 1
                )
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                scraper.logger.error(f"Error processing {url_data['url']}: {str(e)}")
                failed_urls = state_manager.scraping_status['failed_urls']
                failed_urls.append(url_data['url'])
                state_manager.update_scraping_status(failed_urls=failed_urls)
                continue
                
    finally:
        state_manager.update_scraping_status(
            is_running=False,
            current_bank=''
        )
        db.close()
        scraper.logger.info("Scraping session completed")