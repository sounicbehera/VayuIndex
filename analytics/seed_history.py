# written by sounic behera
import os
import datetime
import random
import psycopg2

DB_URL = os.getenv("DB_URL", "postgresql://vayu_admin:vayu_secure_password@vayu_timescale:5432/vayu_cpi")

def seed_history():
    print("[*] Starting Historical Data Seeder for 30-Day Trend...")
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Check how many rows already exist
        cur.execute("SELECT COUNT(*) FROM apix_daily_indices;")
        count = cur.fetchone()[0]
        
        if count >= 30:
            print(f"[OK] Historical data already present ({count} rows). Skipping backfill.")
            return

        today = datetime.date.today()
        # Ensure we don't overwrite today's active calculated index if it exists
        cur.execute("SELECT index_value FROM apix_daily_indices WHERE index_date = %s;", (today,))
        today_record = cur.fetchone()
        
        current_val = float(today_record[0]) if today_record else 110.0
        
        days_to_fill = 30 - count
        print(f"[!] Found {count} rows. Backfilling {days_to_fill} days of historical Jevons indices backwards...")
        
        for i in range(1, days_to_fill + 1):
            date = today - datetime.timedelta(days=i)
            
            # We want an upward trend (inflation) moving forward in time.
            # Since we are iterating backwards, we MUST subtract a positive amount on average.
            fluctuation = random.uniform(-0.1, 0.6) 
            current_val -= fluctuation
            
            cur.execute("""
                INSERT INTO apix_daily_indices (index_date, index_value, base_period, daily_inflation_rate, formula_used)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (index_date) DO NOTHING;
            """, (
                date,
                round(current_val, 4),
                '2026-08-01',
                round(fluctuation, 4),
                'Weighted Laspeyres'
            ))
            
        conn.commit()
        print("[OK] Successfully backfilled 30-day historical trend.")
        
    except Exception as e:
        print(f"[ERROR] Failed to seed historical data: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_history()
