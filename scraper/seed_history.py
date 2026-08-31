# written by sounic behera
import os
import psycopg2
from datetime import datetime, timedelta, timezone
from scraper.aggregator_client import fetch_aggregator_quotes
from storage.orchestrator import StorageOrchestrator
from analytics.calculator import calculate_and_store_index

DB_URL = os.getenv("DB_URL", "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi")

ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL")
]

WINDOWS = ["T+1", "T+7", "T+15", "T+30"]

def seed_database():
    print("[*] Starting Backfill & Re-seed Operation for the last 30 days...")

    # 1. Wipe the existing database completely
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        with conn.cursor() as cur:
            print("[*] Wiping existing `raw_flight_quotes` and `apix_daily_indices`...")
            cur.execute("TRUNCATE raw_flight_quotes RESTART IDENTITY CASCADE;")
            cur.execute("TRUNCATE apix_daily_indices RESTART IDENTITY CASCADE;")
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to wipe database: {e}")
        if conn:
            conn.rollback()
        return
    finally:
        if conn:
            conn.close()

    # 2. Time-Shifting Logic (30 days ago to today)
    start_date = datetime.now(timezone.utc) - timedelta(days=30)
    all_quotes = []

    print("[*] Generating quotes for all days...")
    for i in range(31):
        current_date = start_date + timedelta(days=i)
        depart_date_str = current_date.strftime("%Y-%m-%d")

        for src, dest in ROUTES:
            for window in WINDOWS:
                # We fetch realistic Google Flights quotes via our updated adapter
                quotes = fetch_aggregator_quotes(
                    src=src,
                    dest=dest,
                    depart_date=depart_date_str,
                    lead_tag=window
                )
                
                # We need to shift the `extraction_timestamp` (recorded_at) back to that historical day 
                # instead of today, so the calculator picks it up for that specific day.
                for q in quotes:
                    # Slightly vary the times within that historical day for uniqueness
                    q["extraction_timestamp"] = current_date.isoformat()
                    all_quotes.append(q)

    # 3. Batch Insertion (O(1) database hit)
    print(f"[*] Aggregated {len(all_quotes)} total quotes in-memory.")
    print("[*] Performing bulk insert into TimescaleDB...")
    try:
        # Use existing Orchestrator which batches the array and writes to MinIO
        StorageOrchestrator.persist_quotes(all_quotes)
        print("[+] Bulk insert successful!")
    except Exception as e:
        print(f"[!] Bulk insert failed: {e}")
        return

    # 4. Calculator Trigger
    print("[*] Re-calculating vayuIndex (APIx) for all 30 days...")
    for i in range(31):
        current_date = start_date + timedelta(days=i)
        target_date_str = current_date.strftime("%Y-%m-%d")
        try:
            calculate_and_store_index(target_date_str)
        except Exception as e:
            print(f"[!] Failed to calculate index for {target_date_str}: {e}")

    print("[+] Backfill operation fully completed!")

if __name__ == "__main__":
    seed_database()
