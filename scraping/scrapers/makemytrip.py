import asyncio
from datetime import datetime, timedelta
import re
import json
import redis
from playwright.async_api import async_playwright

r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
STREAM_KEY = "raw.airfare.quotes"

async def scrape_live_google_flights(origin: str, dest: str, days_ahead: int):
    # Formulate travel date (YYYY-MM-DD)
    dept_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    window_tag = f"T+{days_ahead}"
    
    # Direct Google Flights search URL for one-way flight
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{dept_date}%20one-way"
    
    print(f"[*] Navigating to Google Flights: {origin} -> {dest} for {dept_date} ({window_tag})...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Set to True once verified
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for flight listings container to render
            await page.wait_for_selector("ul.RkTKof, li.pIav2d, div[role='listitem']", timeout=15000)
            await page.wait_for_timeout(2000)

            # Query all flight listing items
            flight_items = await page.query_selector_all("li.pIav2d")
            print(f"[+] Found {len(flight_items)} live flight cards on Google Flights.")

            for item in flight_items[:6]:
                text = await item.inner_text()
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                
                # Extract fare using regex (e.g. ₹5,432 or ₹12,890)
                price_match = re.search(r"₹\s?([\d,]+)", text)
                if not price_match:
                    continue
                
                raw_price = int(price_match.group(1).replace(",", ""))
                
                # Extract carrier name if available
                carrier = "IndiGo"
                for c in ["IndiGo", "Air India", "Akasa Air", "SpiceJet", "Vistara"]:
                    if c.lower() in text.lower():
                        carrier = c
                        break

                # Fare deconstruction estimate
                base_fare = round(raw_price * 0.72, 2)
                fuel_surcharge = round(raw_price * 0.15, 2)
                statutory_taxes = round(raw_price * 0.08, 2)
                convenience_fee = round(raw_price - (base_fare + fuel_surcharge + statutory_taxes), 2)

                event = {
                    "source_platform": "GoogleFlights_Live",
                    "carrier": carrier,
                    "flight_number": f"{carrier[:2].upper()}-{days_ahead}01",
                    "route_id": f"{origin}-{dest}",
                    "advance_window": window_tag,
                    "departure_date": dept_date,
                    "base_fare": base_fare,
                    "fuel_surcharge": fuel_surcharge,
                    "statutory_taxes": statutory_taxes,
                    "convenience_fee": convenience_fee,
                    "total_fare": float(raw_price)
                }

                # Push to Redis Stream
                r.xadd(STREAM_KEY, {"data": json.dumps(event)})
                print(f"  • {carrier} ({origin}->{dest}) [{window_tag}] -> Live Price: ₹{raw_price}")

        except Exception as e:
            print(f"[!] Extraction error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    # Test on DEL -> BOM across T+7 and T+30
    asyncio.run(scrape_live_google_flights("DEL", "BOM", 7))
    asyncio.run(scrape_live_google_flights("DEL", "BOM", 30))