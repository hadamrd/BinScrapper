#!/usr/bin/env python3
from bin_manager.scraper.scraper import BinScraper, ScraperConfig
from tqdm import tqdm
import time
from datetime import datetime, timedelta
import sys

from bin_manager.db.database import BinDatabase

def format_time(seconds: float) -> str:
    """Convert seconds to human-readable time format."""
    return str(timedelta(seconds=int(seconds)))

def format_bank_name(name: str, max_length: int = 20) -> str:
    """Format bank name for consistent progress bar display."""
    if len(name) <= max_length:
        return name.ljust(max_length)
    return name[:max_length-3] + "..."

def scrap_bins():
    # Initialize scraper with custom configuration
    config = ScraperConfig(
        retry_attempts=5,
        retry_backoff=2,
        timeout=15,
        delay=0.8
    )
    
    scraper = BinScraper(config)
    db = BinDatabase()
    
    try:
        total_urls = db.get_total_urls_count()
        processed_urls = db.get_processed_urls_count()
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"Starting BIN scraping session at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total URLs to process: {total_urls - processed_urls:,} of {total_urls:,}")
        print(f"{'='*60}\n")
        
        session_stats = {
            'processed_bins': 0,
            'failed_urls': [],
            'successful_banks': 0
        }
        
        with tqdm(total=total_urls, 
                 initial=processed_urls,
                 desc="Scraping BINs",
                 unit="bank",
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}") as pbar:
            
            unprocessed_urls = db.get_unprocessed_urls()
            for url_data in unprocessed_urls:
                try:
                    bank_name = url_data['url'].split('/')[-1]
                    formatted_name = format_bank_name(bank_name)
                    pbar.set_postfix_str(f"Bank: {formatted_name}")
                    
                    # Scrape bank data (this will also display the pretty table)
                    bank_table = scraper.get_bank_bins(url_data['url'])
                    
                    if bank_table:
                        db.insert_bank_data(bank_table, url_data['id'])
                        session_stats['processed_bins'] += len(bank_table)
                        session_stats['successful_banks'] += 1
                    else:
                        session_stats['failed_urls'].append(url_data['url'])
                    
                    db.mark_url_processed(url_data['id'])
                    pbar.update(1)
                    
                except KeyboardInterrupt:
                    print("\n\nScraping interrupted by user. Saving progress...")
                    break
                    
                except Exception as e:
                    print(f"\nError processing {url_data['url']}: {str(e)}")
                    session_stats['failed_urls'].append(url_data['url'])
                    continue
        
        # Display final statistics
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("Scraping Session Summary")
        print(f"{'='*60}")
        print(f"Time elapsed: {format_time(elapsed_time)}")
        print(f"Successfully processed banks: {session_stats['successful_banks']:,}")
        print(f"Total BINs collected: {session_stats['processed_bins']:,}")
        print(f"Failed URLs: {len(session_stats['failed_urls']):,}")
        
        if session_stats['failed_urls']:
            print("\nFailed URLs:")
            for url in session_stats['failed_urls']:
                print(f"- {url}")
        
        print(f"\nOverall progress: {db.get_processed_urls_count():,} / {total_urls:,} banks processed")
        
    except KeyboardInterrupt:
        print("\n\nScraping terminated by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    scrap_bins()