from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, max_pages: int = 1) -> List[Dict]:
        """Return list of internship dicts."""
        raise NotImplementedError
