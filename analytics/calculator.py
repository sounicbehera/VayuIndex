# written by sounic behera
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import os

DB_URL = os.getenv("DB_URL", "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi")

def calculate_and_store_index(target_date: str = None):
    """Computes the Jevons-Laspeyres hybrid index for a given date and persists to apix_daily_indices."""
    import time
    max_retries = 10
    conn = None
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
            break
        except psycopg2.OperationalError as e:
            if i < max_retries - 1:
                print(f"[!] Database not ready, retrying in 3 seconds... ({i+1}/{max_retries})")
                time.sleep(3)
            else:
                raise e

    try:
        cursor = conn.cursor()

        if target_date is None:
            target_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Fetch today's quotes joined with DGCA passenger corridor weights
        cursor.execute("""
            SELECT 
                r.route_id,
                r.total_fare,
                COALESCE(m.dgca_passenger_weight, 
                    CASE r.route_id
                        WHEN 'DEL-BOM' THEN 0.220
                        WHEN 'DEL-BLR' THEN 0.145
                        WHEN 'BOM-BLR' THEN 0.100
                        WHEN 'DEL-CCU' THEN 0.090
                        WHEN 'DEL-MAA' THEN 0.085
                        ELSE 0.050
                    END
                ) AS weight
            FROM raw_flight_quotes r
            LEFT JOIN route_metadata m ON r.route_id = m.route_id
            WHERE DATE(r.recorded_at) = %s AND r.is_outlier = FALSE;
        """, (target_date,))
        
        rows = cursor.fetchall()
        if not rows:
            print(f"[!] No valid quotes found for calculation on {target_date}.")
            return None

        # Group fares by corridor
        route_fares = {}
        route_weights = {}
        for row in rows:
            rid = row["route_id"]
            if not rid:
                continue
            fare = float(row["total_fare"])
            weight = float(row["weight"])
            
            if rid not in route_fares:
                route_fares[rid] = []
                route_weights[rid] = weight
            route_fares[rid].append(fare)

        # 1. Elementary Level: Jevons Geometric Mean per corridor
        # 2. Upper Level: Laspeyres Weighted Sum across corridors
        route_geom_means = {}
        weighted_fare_sum = 0.0
        total_weight = 0.0

        print("\n---------------- ROUTE-LEVEL JEVONS SUMMARY ----------------")
        for rid, fares in route_fares.items():
            # Geometric mean: exp(mean(log(P)))
            geom_mean = float(np.exp(np.mean(np.log(fares))))
            route_geom_means[rid] = geom_mean
            w = route_weights[rid]
            weighted_fare_sum += geom_mean * w
            total_weight += w
            print(f"Route: {rid:<8} | Quotes: {len(fares):<3} | Geom Mean: Rs. {geom_mean:8.2f} | DGCA Weight: {(w or 0.0):.4f}")
        print("------------------------------------------------------------")

        # Normalized Laspeyres Basket Aggregate
        current_basket_price = weighted_fare_sum / total_weight if total_weight > 0 else weighted_fare_sum
        
        # Baseline period constant (Base price = ₹5,000 => Index = 100.0)
        BASE_BASKET_PRICE = 5000.0
        apix_value = round((current_basket_price / BASE_BASKET_PRICE) * 100.0, 4)

        # Persist daily index into apix_daily_indices
        upsert_sql = """
        INSERT INTO apix_daily_indices (index_date, base_period, index_value)
        VALUES (%s, '2026-08-01', %s)
        ON CONFLICT (index_date) 
        DO UPDATE SET 
            index_value = EXCLUDED.index_value;
        """
        cursor.execute(upsert_sql, (target_date, apix_value))
        conn.commit()

        print(f"[OK] NATIONAL vayuIndex (APIx): {apix_value} (Base = 100.0)")
        print(f"[OK] Successfully stored index in table `apix_daily_indices` for {target_date}.\n")
        return apix_value
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    calculate_and_store_index()