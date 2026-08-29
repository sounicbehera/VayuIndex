# written by sounic behera
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """
    Abstract base class for all flight quote scrapers.
    Defines a strict interface returning a standardized JSON schema.
    """

    def __init__(self, provider_id: str):
        self.provider_id = provider_id

    @abstractmethod
    async def extract_quotes(self, src: str, dest: str, depart_date: str, lead_tag: str) -> List[Dict[str, Any]]:
        """
        Executes the extraction logic for the specific provider.
        
        Args:
            src (str): Origin IATA code
            dest (str): Destination IATA code
            depart_date (str): Departure date (YYYY-MM-DD)
            lead_tag (str): Advance window identifier (e.g., 'T+7')
            
        Returns:
            List[Dict[str, Any]]: A list of validated flight quote dictionaries.
        """
        pass

    def validate_quote(self, quote: Dict[str, Any]) -> bool:
        """
        Validates the extracted quote against the strict schema.
        """
        required_keys = {
            "source", "airline", "carrier_code", "flight_number",
            "src", "dest", "departure_date", "advance_window",
            "base_fare", "fuel_surcharge", "taxes", "fare"
        }
        return required_keys.issubset(quote.keys())
