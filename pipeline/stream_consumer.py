import json
import time
import psycopg2
import redis

# Connections
r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
conn = psycopg2.connect("postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi")
cursor = conn.cursor()

STREAM_KEY = "raw.airfare.quotes"
GROUP_NAME = "vayu_etl_group"
CONSUMER_NAME = "worker_node_1"

try:
    r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
except redis.exceptions.ResponseError:
    pass

print(f"[*] ETL Stream Worker active. Listening on stream: {STREAM_KEY}...")

while True:
    try:
        messages = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=20, block=2000)
        
        for stream, batch in messages:
            for message_id, raw_data in batch:
                data = json.loads(raw_data["data"])

                insert_query = """
                INSERT INTO raw_flight_quotes (
                    crawl_id, source_platform, carrier, flight_number,
                    route_id, advance_window, departure_date,
                    base_fare, fuel_surcharge, statutory_taxes, convenience_fee, total_fare,
                    is_sold_out, is_outlier
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                
                cursor.execute(insert_query, (
                    data["crawl_id"],
                    data["source_platform"],
                    data["carrier"],
                    data["flight_number"],
                    data["route_id"],
                    data["advance_window"],
                    data["departure_date"],
                    data["base_fare"],
                    data["fuel_surcharge"],
                    data["statutory_taxes"],
                    data["convenience_fee"],
                    data["total_fare"],
                    data.get("is_sold_out", False),
                    data.get("is_outlier", False)
                ))
                conn.commit()
                
                r.xack(STREAM_KEY, GROUP_NAME, message_id)
                print(f"[✓] Persisted: {data['route_id']} ({data['advance_window']}) | {data['carrier']} -> Total: ₹{data['total_fare']} (Base: ₹{data['base_fare']})")
                
    except Exception as e:
        print(f"[!] Worker Error: {e}")
        time.sleep(2)