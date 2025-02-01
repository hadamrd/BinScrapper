# bin_manager/app/state.py
from datetime import datetime
from typing import Dict, Any
from bin_manager.db.database import BinDatabase
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Manages application state across different modules."""
    
    def __init__(self):
        logger.info("Initializing StateManager")
        self._url_collection_status = {
            'is_running': False,
            'start_time': None,
            'total_countries': 0,
            'processed_countries': 0,
            'current_country': '',
            'collected_urls': 0,
            'failed_countries': [],
            'last_update': None
        }
        
        self._scraping_status = {
            'is_running': False,
            'resumable': False,
            'start_time': None,
            'processed_banks': 0,
            'total_banks': 0,
            'current_bank': '',
            'processed_bins': 0,
            'failed_urls': [],
            'last_update': None
        }
        logger.info("Initial scraping status: %s", self._scraping_status)

    def sync_with_db(self) -> None:
        """Synchronize state with database current state."""
        db = BinDatabase()
        try:
            total_urls = db.get_total_urls_count()
            processed_urls = db.get_processed_urls_count()
            
            logger.info(f"DB state - Total URLs: {total_urls}, Processed URLs: {processed_urls}")
            
            # First, reset status if database is empty
            if total_urls == 0:
                logger.info("Database is empty, resetting all status")
                self._scraping_status.update({
                    'total_banks': 0,
                    'processed_banks': 0,
                    'processed_bins': 0,
                    'resumable': False,
                    'last_update': datetime.now()
                })
            else:
                logger.info("Updating status with DB values")
                self._scraping_status.update({
                    'total_banks': total_urls,
                    'processed_banks': processed_urls,
                    'resumable': total_urls > processed_urls,
                    'last_update': datetime.now()
                })
                
            logger.info(f"Updated scraping status: {self._scraping_status}")
        finally:
            db.close()
    
    def reset(self) -> None:
        """Reset all statuses to their initial state."""
        self._url_collection_status = {
            'is_running': False,
            'start_time': None,
            'total_countries': 0,
            'processed_countries': 0,
            'current_country': '',
            'collected_urls': 0,
            'failed_countries': [],
            'last_update': None
        }
        
        self._scraping_status = {
            'is_running': False,
            'resumable': False,
            'start_time': None,
            'processed_banks': 0,
            'total_banks': 0,
            'current_bank': '',
            'processed_bins': 0,
            'failed_urls': [],
            'last_update': None
        }
        
        # Sync with current database state
        self.sync_with_db()
    
    def update_url_status(self, **kwargs) -> None:
        """Update URL collection status with new information."""
        for key, value in kwargs.items():
            if key in self._url_collection_status:
                self._url_collection_status[key] = value
        self._url_collection_status['last_update'] = datetime.now()
    
    def update_scraping_status(self, **kwargs) -> None:
        """Update scraping status with new information."""
        for key, value in kwargs.items():
            if key in self._scraping_status:
                self._scraping_status[key] = value
        self._scraping_status['last_update'] = datetime.now()
        
        # If we're updating status, sync resumable state
        if 'is_running' in kwargs or 'total_banks' in kwargs or 'processed_banks' in kwargs:
            self.sync_with_db()
    
    @property
    def url_collection_status(self) -> Dict[str, Any]:
        """Get current URL collection status."""
        return self._url_collection_status
    
    @property
    def scraping_status(self) -> Dict[str, Any]:
        return self._scraping_status

# Create a singleton instance
state_manager = StateManager()