import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name='bin_scraper', log_file='scraper.log'):
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    log_path = os.path.join('logs', log_file)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Rotating file handler - 5MB per file, keep 3 backup files
    handler = RotatingFileHandler(
        log_path, 
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logger()

base_url = "https://bincheck.io/fr"

def scrap_countries_pages_hrefs():
    url = f"{base_url}/bin-list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        selector = "body > section.bg-white.dark\:text-white.dark\:bg-gray-900 > section.py-20.antialiased.bg-white.dark\:text-white.dark\:bg-gray-900 > div > div.grid.grid-cols-1.sm\:grid-cols-2.md\:grid-cols-3.gap-x-10.lg\:gap-x-10.gap-y-10"
        
        container = soup.select_one(selector)
        if not container:
            print("Container not found")
            return []
            
        links = container.find_all('a')
        hrefs = [link.get('href') for link in links]
        
        return hrefs
        
    except requests.RequestException as e:
        logger.error(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing the page: {e}")
        return []

def scrape_country_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        selector = "body > section.bg-white.dark\:text-white.dark\:bg-gray-900 > section.py-20.antialiased.bg-white.dark\:text-white.dark\:bg-gray-900 > div > div.grid.grid-cols-1.sm\:grid-cols-2.md\:grid-cols-3.gap-x-10.lg\:gap-x-10.gap-y-10"
        
        container = soup.select_one(selector)
        if not container:
            logger.error("Container not found")
            return []
            
        links = container.find_all('a')
        hrefs = [link.get('href') for link in links]
        
        return hrefs
        
    except requests.RequestException as e:
        logger.error(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing the page: {e}")
        return []

def scrape_bank_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table_selector = "body > section.bg-white.dark\:text-white.dark\:bg-gray-900 > section.py-5.antialiased.bg-white.dark\:text-white.dark\:bg-gray-900 > div > div > table"
        
        table_element_soup = soup.select_one(table_selector)
        if not table_element_soup:
            logger.error("bank table element not found")
            return []
        
        bank_table = parse_bank_table(table_element_soup)
        return bank_table
        
    except requests.RequestException as e:
        logger.error(f"Request error for {url}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"General error for {url}: {str(e)}")
        return []

def parse_bank_table(soup):    
    # Get headers
    headers = [th.text.strip() for th in soup.select("thead th")]
    
    # Initialize list for rows
    rows_data = []
    
    # Parse each row
    for row in soup.select("tbody tr"):
        row_dict = {}
        cells = row.find_all('td')
        
        # Map cells to headers
        for header, cell in zip(headers, cells):
            # Get text content, removing the '↗' symbol
            value = cell.text.strip().replace('↗', '').strip()
            row_dict[header] = value
            
        rows_data.append(row_dict)
    
    # # Create PrettyTable
    # pt = PrettyTable()
    # pt.field_names = headers
    
    # # Add rows to table
    # for row in rows_data:
    #     pt.add_row([row[header] for header in headers])
    
    # # Set alignment
    # for header in headers:
    #     pt.align[header] = 'l'
    
    # # Print formatted table
    # print(pt)
    
    # Return data dictionary
    return rows_data
