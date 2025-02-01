#!/usr/bin/env python3
from bin_manager.db.database import BinDatabase
from bin_manager.scraper.scraper import BinScraper, ScraperConfig
from tqdm import tqdm
from datetime import datetime
import sys
from urllib.parse import urljoin

def collect_bank_urls():
    start_time = datetime.now()
    print(f"\nStarting bank URL collection at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize database and scraper with optimized configuration
    db = BinDatabase()
    config = ScraperConfig(
        retry_attempts=5,
        retry_backoff=1,
        timeout=15,
        delay=0.8  # Balanced delay for reliability
    )
    scraper = BinScraper(config)
    
    try:
        print("\nFetching country list...")
        country_hrefs = scraper.get_countries_list()
        total_countries = len(country_hrefs)
        
        if not country_hrefs:
            print("Error: No countries found. Please check the connection or source website.")
            return
        
        print(f"Found {total_countries:,} countries to process")
        
        # Track collection statistics
        stats = {
            'total_banks': 0,
            'successful_countries': 0,
            'failed_countries': []
        }
        
        with tqdm(total=total_countries, 
                 desc="Collecting bank URLs", 
                 unit="country",
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} countries "
                           "[{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            
            for href in country_hrefs:
                try:
                    country_name = href.split('/')[-1]
                    pbar.set_postfix_str(f"Processing: {country_name}")
                    
                    country_url = urljoin(config.base_url, href)
                    country_banks_hrefs = scraper.get_country_banks(country_url)
                    
                    if country_banks_hrefs:
                        db.insert_bank_urls(country_banks_hrefs)
                        stats['total_banks'] += len(country_banks_hrefs)
                        stats['successful_countries'] += 1
                    else:
                        stats['failed_countries'].append(country_name)
                    
                    pbar.update(1)
                    
                except KeyboardInterrupt:
                    print("\nCollection interrupted by user. Saving progress...")
                    break
                    
                except Exception as e:
                    print(f"\nError processing {country_name}: {str(e)}")
                    stats['failed_countries'].append(country_name)
                    continue
        
        # Display collection summary
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        
        print("\nCollection Summary:")
        print(f"Time elapsed: {elapsed_time}")
        print(f"Successfully processed countries: {stats['successful_countries']:,}/{total_countries:,}")
        print(f"Total bank URLs collected: {stats['total_banks']:,}")
        
        if stats['failed_countries']:
            print("\nFailed countries:")
            for country in stats['failed_countries']:
                print(f"- {country}")
        
        # Verify final database state
        total_urls = db.get_total_urls_count()
        print(f"\nFinal database state: {total_urls:,} bank URLs stored")
        
    except KeyboardInterrupt:
        print("\nCollection terminated by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    collect_bank_urls()