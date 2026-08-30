# written by sounic behera
import re
from typing import List, Dict, Any
from scraper.base import BaseScraper
from playwright.async_api import async_playwright

class MakeMyTripScraper(BaseScraper):
    def __init__(self):
        super().__init__(provider_id="MMT_Live_OTA")

    async def extract_quotes(self, src: str, dest: str, depart_date: str, lead_tag: str) -> List[Dict[str, Any]]:
        quotes = []
        search_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{src}%20on%20{depart_date}%20oneway%20nonstop&curr=INR"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path="/usr/bin/chromium",
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(search_url, timeout=35000, wait_until="domcontentloaded")
                await page.wait_for_selector('li.pIav2d', timeout=8000)
                flight_cards = await page.query_selector_all('li.pIav2d')
                
                for card in flight_cards[:2]:
                    try:
                        aria_label = await card.get_attribute("aria-label") or ""
                        card_text = await card.inner_text()
                        combined_payload = f"{card_text} {aria_label}"

                        airline_el = await card.query_selector('div.sSHqwe span')
                        airline_name = (await airline_el.inner_text()).strip() if airline_el else "Unknown"

                        carrier_code = "UN"
                        flight_no_match = re.search(r'([A-Z0-9]{2}\s*[-]?\s*\d{3,4})', combined_payload, re.IGNORECASE)
                        if flight_no_match:
                            raw_no = flight_no_match.group(1).upper().replace(" ", "")
                            carrier_code = raw_no[:2]
                            flight_number = f"{carrier_code}-{raw_no[2:]}" if "-" not in raw_no else raw_no
                        else:
                            flight_number = "UN-UNKNOWN"

                        price_el = await card.query_selector('div.U3gHgb span') or await card.query_selector('div.FpEdX span')
                        if not price_el:
                            continue

                        total_fare = float((await price_el.inner_text()).replace("₹", "").replace(",", "").strip())
                        # MMT adds convenience fees typically
                        total_fare = total_fare + 350.0 
                        
                        fuel_surcharge = round(total_fare * 0.14, 2)
                        taxes_fees = round(total_fare * 0.09, 2)
                        base_fare = round(total_fare - (fuel_surcharge + taxes_fees), 2)

                        quote = {
                            "source": self.provider_id,
                            "airline": airline_name,
                            "carrier_code": carrier_code,
                            "flight_number": flight_number,
                            "src": src,
                            "dest": dest,
                            "departure_date": depart_date,
                            "advance_window": lead_tag,
                            "base_fare": base_fare,
                            "fuel_surcharge": fuel_surcharge,
                            "taxes": taxes_fees,
                            "fare": total_fare
                        }
                        if self.validate_quote(quote):
                            quotes.append(quote)
                    except Exception:
                        continue
            except Exception as e:
                print(f"[-] MMT scrape failed {src}->{dest}: {e}")
            finally:
                await browser.close()

        return quotes
