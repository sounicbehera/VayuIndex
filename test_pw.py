from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re
import time

def scrape_indigo(src, dest, date_str):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        stealth_sync(page)
        
        # Example URL (MakeMyTrip used here for better success rate during hackathon, as goindigo.in has strict Akamai)
        # However, to meet the strict requirement, we will try goindigo first.
        
        url = f"https://www.goindigo.in/"
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(5)
            print("Title:", page.title())
        except Exception as e:
            print("Failed to load:", e)
        finally:
            browser.close()

if __name__ == '__main__':
    scrape_indigo("DEL", "BOM", "2026-09-28")
