# written by sounic behera
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Any
from storage.audit_vault import archive_quote_batch
from datetime import datetime, timezone
import uuid
import os

DB_URL = os.getenv("DB_URL", "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi")

class StorageOrchestrator:
    @staticmethod
    def persist_quotes(quotes: List[Dict[str, Any]]) -> str:
        if not quotes:
            return "No quotes to persist."
            
        batch_id = str(uuid.uuid4())
        
        # 1. Archive to MinIO WORM Vault
        proof_hash, s3_key = archive_quote_batch(batch_id, quotes)
        
        # 2. Insert into TimescaleDB
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cur:
                insert_sql = """
                    INSERT INTO raw_flight_quotes 
                    (
                        recorded_at, crawl_id, source_platform, carrier, flight_number, 
                        corridor_code, route_id, advance_window, departure_date, departure_time, 
                        base_fare, fuel_surcharge, statutory_taxes, total_fare, 
                        proof_hash, proof_object_key
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (route_id, flight_number, recorded_at) DO NOTHING
                """
                
                rows = [
                    (
                        q.get("extraction_timestamp") or datetime.now(timezone.utc),
                        batch_id,
                        q.get("source"),
                        q.get("airline"),
                        q.get("flight_number"),
                        f"{q['src']}-{q['dest']}",
                        f"{q['src']}-{q['dest']}",
                        q.get("advance_window"),
                        q.get("departure_date"),
                        q.get("departure_time", "06:00"),
                        q.get("base_fare"),
                        q.get("fuel_surcharge"),
                        q.get("taxes"),
                        q.get("fare"),
                        proof_hash,
                        s3_key
                    )
                    for q in quotes
                ]
                
                execute_batch(cur, insert_sql, rows)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        
        return f"Persisted {len(quotes)} quotes. Hash: {proof_hash}"
