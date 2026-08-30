# written by sounic behera
import os
import concurrent.futures
from datetime import datetime, timedelta, timezone
from scraper.aggregator_client import fetch_aggregator_quotes
from storage.orchestrator import StorageOrchestrator

ROUTES = [
    {"src": "DEL", "dest": "BOM"},
    {"src": "DEL", "dest": "BLR"},
    {"src": "BOM", "dest": "BLR"},
    {"src": "DEL", "dest": "CCU"},
    {"src": "BLR", "dest": "HYD"},
    {"src": "MAA", "dest": "DEL"},
]

ADVANCE_DAYS = {
    "T+1": 1,
    "T+7": 7,
    "T+15": 15,
    "T+30": 30
}

def process_route_window(route, lead_tag, days_out, today):
    target_date = (today + timedelta(days=days_out)).strftime("%Y-%m-%d")
    src = route["src"]
    dest = route["dest"]
    
    # 1. Fetch from aggregator mock
    quotes = fetch_aggregator_quotes(src, dest, target_date, lead_tag)
    
    # 2. Synchronous insert to TimescaleDB
    if quotes:
        try:
            res = StorageOrchestrator.persist_quotes(quotes)
            return len(quotes)
        except Exception as e:
            print(f"[ERROR] Failed persisting {src}-{dest} for {lead_tag}: {e}")
            return 0
    return 0

def dispatch_scrape_jobs():
    print("[*] Starting vayuIndex Aggregator Producer...")
    today = datetime.now(timezone.utc)
    
    total_quotes_inserted = 0
    
    # Use ThreadPoolExecutor for concurrent aggregator fetches and DB inserts
    tasks = []
    # Using thread pool context manager ensures graceful teardown and avoids leaks
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for route in ROUTES:
            for lead_tag, days_out in ADVANCE_DAYS.items():
                tasks.append(
                    executor.submit(process_route_window, route, lead_tag, days_out, today)
                )
                
        for future in concurrent.futures.as_completed(tasks):
            total_quotes_inserted += future.result()
            
    print(f"[+] Successfully extracted and persisted {total_quotes_inserted} flight quotes across {len(ROUTES)} corridors.")

if __name__ == "__main__":
    dispatch_scrape_jobs()
