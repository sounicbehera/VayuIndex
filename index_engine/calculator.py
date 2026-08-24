import sys
from datetime import datetime, timezone
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect via Port 5433 to Docker
DB_URL = "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi"

def calculate_daily_apix(target_date: str = None):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("[*] Connected to TimescaleDB successfully on port 5433.")
    except Exception as e:
        print(f"[!] Database connection error: {e}")
        return None

    # Default to latest recorded date if none specified
    if not target_date:
        cursor.execute("SELECT MAX(recorded_at)::DATE as latest_date FROM raw_flight_quotes;")
        row = cursor.fetchone()
        if not row or not row["latest_date"]:
            print("[!] No quotes found in table raw_flight_quotes.")
            conn.close()
            return None
        target_date = row["latest_date"].isoformat()

    print(f"[*] Calculating vayuIndex (APIx) for date: {target_date}")

    # Fetch quotes and DGCA corridor weights
    query = """
    SELECT 
        q.route_id,
        q.total_fare,
        COALESCE(r.dgca_passenger_weight, 0.10) AS dgca_passenger_weight
    FROM raw_flight_quotes q
    LEFT JOIN route_metadata r ON q.route_id = r.route_id
    WHERE q.recorded_at::DATE = %s AND (q.is_outlier IS FALSE OR q.is_outlier IS NULL);
    """
    cursor.execute(query, (target_date,))
    rows = cursor.fetchall()

    if not rows:
        print(f"[!] No quotes matched query criteria for date: {target_date}")
        conn.close()
        return None

    print(f"[+] Retrieved {len(rows)} flight quotes for computation.")

    # Group fares by route
    route_prices = {}
    route_weights = {}
    for r in rows:
        route_id = r["route_id"]
        if route_id not in route_prices:
            route_prices[route_id] = []
            route_weights[route_id] = float(r["dgca_passenger_weight"])
        route_prices[route_id].append(float(r["total_fare"]))

    # Baseline reference fare (₹5000) for standard price-relative indexing
    base_price_p0 = 5000.0
    weighted_relative_sum = 0.0
    total_weight_norm = 0.0

    print("\n---------------- ROUTE-LEVEL JEVONS SUMMARY ----------------")
    for route, prices in route_prices.items():
        # Jevons Index: Geometric Mean per route
        geom_mean = float(np.exp(np.mean(np.log(prices))))
        price_relative = geom_mean / base_price_p0
        w = route_weights[route]

        weighted_relative_sum += price_relative * w
        total_weight_norm += w
        print(f"Route: {route:<8} | Quotes: {len(prices):<3} | Geom Mean: ₹{geom_mean:8.2f} | DGCA Weight: {w:.4f}")

    # Macro Weighted Laspeyres aggregation (Base Index = 100.0)
    apix_value = round((weighted_relative_sum / total_weight_norm) * 100.0, 4)
    print("------------------------------------------------------------")
    print(f"[✓] NATIONAL vayuIndex (APIx): {apix_value} (Base = 100.0)\n")

    # Persist the computed daily index
    insert_query = """
    INSERT INTO apix_daily_indices (index_date, index_value, base_period, formula_used, computed_at)
    VALUES (%s, %s, %s, %s, NOW())
    ON CONFLICT (index_date)
    DO UPDATE SET index_value = EXCLUDED.index_value, computed_at = NOW();
    """
    cursor.execute(insert_query, (target_date, apix_value, "2026-08-01", "Jevons-Laspeyres Hybrid"))
    conn.commit()
    conn.close()
    print(f"[✓] Successfully stored index in table `apix_daily_indices` for {target_date}.")
    return apix_value

if __name__ == "__main__":
    calculate_daily_apix()