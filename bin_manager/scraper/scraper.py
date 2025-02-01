import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from logging.handlers import RotatingFileHandler
import os
from dataclasses import dataclass
from time import sleep
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

@dataclass
class ScraperConfig:
    base_url: str = "https://bincheck.io/fr"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    retry_attempts: int = 3
    retry_backoff: int = 2
    timeout: int = 10
    delay: float = 0.5

class BinScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.logger = self._setup_logger()
        self.session = self._setup_session()
        self.selectors = {
            'country_container': (
                "section.bg-white.dark\\:text-white.dark\\:bg-gray-900 > "
                "section.py-20.antialiased.bg-white.dark\\:text-white.dark\\:bg-gray-900 > "
                "div > div.grid"
            ),
            'bank_table': (
                "section.bg-white.dark\\:text-white.dark\\:bg-gray-900 > "
                "section.py-5.antialiased.bg-white.dark\\:text-white.dark\\:bg-gray-900 > "
                "div > div > table"
            )
        }

    def _setup_logger(self) -> logging.Logger:
        """Configure rotating file logger with proper formatting."""
        os.makedirs('logs', exist_ok=True)
        logger = logging.getLogger('bin_scraper')
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(
            os.path.join('logs', 'scraper.log'),
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

    def _setup_session(self) -> requests.Session:
        """Configure session with retry logic and headers."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            "User-Agent": self.config.user_agent
        })
        
        return session

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page, handling errors gracefully."""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {str(e)}")
            return None
        finally:
            sleep(self.config.delay)

    def get_countries_list(self) -> List[str]:
        """Fetch list of country URLs."""
        url = urljoin(self.config.base_url, "bin-list")
        soup = self._fetch_page(url)
        if not soup:
            return []

        container = soup.select_one(self.selectors['country_container'])
        if not container:
            self.logger.error("Country container not found")
            return []

        return [link.get('href') for link in container.find_all('a') if link.get('href')]

    def get_country_banks(self, country_url: str) -> List[str]:
        """Fetch list of bank URLs for a specific country."""
        soup = self._fetch_page(country_url)
        if not soup:
            return []

        container = soup.select_one(self.selectors['country_container'])
        if not container:
            self.logger.error(f"Bank container not found for {country_url}")
            return []

        return [link.get('href') for link in container.find_all('a') if link.get('href')]

    def get_bank_bins(self, bank_url: str) -> List[Dict]:
        """Fetch BIN information for a specific bank."""
        soup = self._fetch_page(bank_url)
        if not soup:
            return []

        table = soup.select_one(self.selectors['bank_table'])
        if not table:
            self.logger.error(f"Bank table not found for {bank_url}")
            return []

        return self._parse_bank_table(table)

    def _parse_bank_table(self, table: BeautifulSoup) -> List[Dict]:
        """Parse bank table into structured data."""
        headers = [th.text.strip() for th in table.select("thead th")]
        rows_data = []

        for row in table.select("tbody tr"):
            cells = row.find_all('td')
            row_dict = {
                header: cell.text.strip().replace('↗', '').strip()
                for header, cell in zip(headers, cells)
            }
            rows_data.append(row_dict)

        return rows_data
