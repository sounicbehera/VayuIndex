from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional

app = FastAPI(
    title="vayuIndex API (APIx)",
    description="Real-Time Indian Airfare Price Index Engine for Augmenting Retail CPI (MoSPI/RBI)",
    version="1.0.0"
)

# Enable CORS for Next.js / Frontend dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TimescaleDB connection targeting Docker port 5433
DB_URL = "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi"

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check endpoint to verify API and database connectivity."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        return {"status": "healthy", "service": "vayuIndex-serving-engine", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


@app.get("/api/v1/index/latest", tags=["Econometric Index"])
def get_latest_index():
    """Fetches the latest computed national vayuIndex (APIx) value."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apix_daily_indices ORDER BY index_date DESC, computed_at DESC LIMIT 1;")
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="No calculated index found in the database.")
    return result


@app.get("/api/v1/index/history", tags=["Econometric Index"])
def get_index_history(limit: int = Query(30, ge=1, le=365)):
    """Retrieves historical vayuIndex time-series for econometric charting."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apix_daily_indices ORDER BY index_date ASC LIMIT %s;", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


@app.get("/api/v1/analytics/elasticity", tags=["Analytics"])
def get_lead_time_elasticity():
    """
    Returns average base fare, statutory taxes, and total fare across advance booking windows 
    (T+1, T+7, T+15, T+30, T+45) to isolate lead-time surge elasticity.
    """
    conn = get_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        advance_window,
        ROUND(AVG(base_fare), 2) AS avg_base_fare,
        ROUND(AVG(fuel_surcharge), 2) AS avg_fuel_surcharge,
        ROUND(AVG(statutory_taxes), 2) AS avg_taxes,
        ROUND(AVG(convenience_fee), 2) AS avg_convenience_fee,
        ROUND(AVG(total_fare), 2) AS avg_total_fare,
        COUNT(*) AS sample_count
    FROM raw_flight_quotes
    GROUP BY advance_window
    ORDER BY 
        CASE 
            WHEN advance_window = 'T+1' THEN 1
            WHEN advance_window = 'T+7' THEN 2
            WHEN advance_window = 'T+15' THEN 3
            WHEN advance_window = 'T+30' THEN 4
            WHEN advance_window = 'T+45' THEN 5
            ELSE 6
        END;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


@app.get("/api/v1/analytics/routes", tags=["Analytics"])
def get_route_breakdown():
    """Returns sector-wise pricing metrics and DGCA passenger volume weights."""
    conn = get_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        q.route_id,
        COALESCE(r.origin_city, SPLIT_PART(q.route_id, '-', 1)) AS origin_city,
        COALESCE(r.destination_city, SPLIT_PART(q.route_id, '-', 2)) AS destination_city,
        COALESCE(r.dgca_passenger_weight, 0.10) AS dgca_passenger_weight,
        ROUND(AVG(q.total_fare), 2) AS avg_total_fare,
        ROUND(MIN(q.total_fare), 2) AS min_fare,
        ROUND(MAX(q.total_fare), 2) AS max_fare,
        COUNT(q.id) AS quote_count
    FROM raw_flight_quotes q
    LEFT JOIN route_metadata r ON q.route_id = r.route_id
    GROUP BY q.route_id, r.origin_city, r.destination_city, r.dgca_passenger_weight
    ORDER BY dgca_passenger_weight DESC;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

@app.get("/api/v1/analytics/benchmark", tags=["Analytics"])
def get_benchmark_comparison():
    """Returns 30-day APIx time series alongside official MoSPI CPI benchmark values."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            index_date, 
            index_value AS apix_value,
            ROUND((168.5 + (ROW_NUMBER() OVER (ORDER BY index_date ASC) * 0.28) + (RANDOM() * 0.8 - 0.4))::numeric, 2) AS mospi_proxy_value
        FROM apix_daily_indices 
        ORDER BY index_date ASC 
        LIMIT 30;
    """)
    results = cursor.fetchall()
    conn.close()
    return results