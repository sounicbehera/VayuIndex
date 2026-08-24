import asyncio
from datetime import datetime, timedelta
import json
import httpx
from playwright.async_api import async_playwright

async def get_indigo_session():
    """Extracts valid session tokens and Akamai cookies via Playwright."""
    print("[*] Initiating IndiGo API session handshake...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Intercept token from network requests
        api_headers = {}
        async def capture_request(request):
            if "api" in request.url and "flight" in request.url:
                for k, v in request.headers.items():
                    if k.lower() in ["authorization", "x-session-id", "x-api-key", "signature"]:
                        api_headers[k] = v

        page.on("request", capture_request)
        
        try:
            await page.goto("https://www.goindigo.in", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            cookies = await context.cookies()
            cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            return cookie_header, api_headers
        finally:
            await browser.close()

async def fetch_indigo_direct(origin: str, dest: str, days_ahead: int):
    cookie_str, extra_headers = await get_indigo_session()
    travel_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    # IndiGo Search Endpoint
    api_url = "https://www.goindigo.in/api/booking/availability"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://www.goindigo.in/",
        "Origin": "https://www.goindigo.in",
        "Cookie": cookie_str,
        **extra_headers
    }
    
    payload = {
        "origin": origin,
        "destination": dest,
        "travelDate": travel_date,
        "pax": {"adults": 1, "children": 0, "infants": 0},
        "fareFamily": "REGULAR"
    }

    print(f"[*] Calling IndiGo REST API directly for {origin} -> {dest} on {travel_date}...")
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(api_url, json=payload, headers=headers)
            print(f"[+] API Status Code: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                print(f"[✓] Received Clean JSON Response: {len(data.get('flights', []))} flights found.")
                return data
            else:
                print(f"[!] API Block/Failure: {res.text[:200]}")
        except Exception as e:
            print(f"[!] HTTP Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_indigo_direct("DEL", "BOM", 7))