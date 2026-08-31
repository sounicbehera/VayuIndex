import datetime
import random
import psycopg2

DB_URL = "postgresql://vayu_admin:vayu_secure_password@localhost:5433/vayu_cpi"

def seed_history():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    today = datetime.date.today()
    base_value = 100.0
    
    # Check if today exists, if not, generate for today as well
    cur.execute("SELECT COUNT(*) FROM apix_daily_indices;")
    count = cur.fetchone()[0]
    
    start_offset = 0
    current_val = 109.88 # Start near today's actual value
    
    for i in range(start_offset, 31):
        date = today - datetime.timedelta(days=i)
        fluctuation = random.uniform(-0.5, 0.5)
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
    cur.close()
    conn.close()
    print("Seeded 30 days of historical data.")

if __name__ == "__main__":
    seed_history()
