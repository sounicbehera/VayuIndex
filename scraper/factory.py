# written by sounic behera
from scraper.base import BaseScraper
from scraper.providers.indigo import IndiGoScraper
from scraper.providers.airindia import AirIndiaScraper
from scraper.providers.mmt import MakeMyTripScraper
from scraper.providers.emt import EaseMyTripScraper

class ScraperFactory:
    """
    Dynamically instantiates the requested scraper provider.
    """
    @staticmethod
    def get_scraper(provider: str) -> BaseScraper:
        provider_map = {
            "indigo": IndiGoScraper,
            "airindia": AirIndiaScraper,
            "mmt": MakeMyTripScraper,
            "emt": EaseMyTripScraper
        }
        
        provider_key = provider.lower()
        if provider_key not in provider_map:
            raise ValueError(f"Unknown scraper provider: {provider}")
            
        return provider_map[provider_key]()
