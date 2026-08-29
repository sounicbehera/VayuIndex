# written by sounic behera
import time
from datetime import datetime, timedelta, timezone
from scraper.worker import scrape_flight_corridor

ROUTES = [
    {"src": "DEL", "dest": "BOM"},
    {"src": "DEL", "dest": "BLR"},
    {"src": "BOM", "dest": "BLR"},
    {"src": "DEL", "dest": "CCU"},
    {"src": "DEL", "dest": "MAA"},
]

ADVANCE_DAYS = {
    "T+1": 1,
    "T+7": 7,
    "T+15": 15,
    "T+30": 30
}

PROVIDERS = ["indigo", "airindia", "mmt", "emt"]

def dispatch_scrape_jobs():
    """
    Generates and dispatches distributed scrape tasks to the Celery/Redis queue.
    """
    print("[*] Starting vayuIndex Distributed Scraper Producer...")
    today = datetime.now(timezone.utc)
    
    total_tasks = 0
    for provider in PROVIDERS:
        for route in ROUTES:
            for lead_tag, days_out in ADVANCE_DAYS.items():
                target_date = (today + timedelta(days=days_out)).strftime("%Y-%m-%d")
                
                # Push task to Redis queue via Celery
                scrape_flight_corridor.delay(
                    provider=provider,
                    src=route["src"],
                    dest=route["dest"],
                    depart_date=target_date,
                    lead_tag=lead_tag
                )
                total_tasks += 1
                
    print(f"[+] Dispatched {total_tasks} tasks to Celery queue.")

if __name__ == "__main__":
    dispatch_scrape_jobs()
