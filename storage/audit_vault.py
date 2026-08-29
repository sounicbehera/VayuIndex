# written by smruti sourav sahoo
import io
import json
import hashlib
import os
from datetime import datetime
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadminpassword")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "vayu-cpi-audit")

def get_minio_client() -> Minio:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    return client

def archive_quote_batch(crawl_batch_id: str, flat_quotes: list) -> tuple[str, str]:
    """
    Serializes quotes, calculates SHA-256 digest, and archives payload to MinIO WORM vault.
    Returns: (proof_hash, proof_obj_key)
    """
    client = get_minio_client()
    
    payload_dict = {
        "crawl_batch_id": crawl_batch_id,
        "recorded_at": datetime.now().isoformat(),
        "quote_count": len(flat_quotes),
        "quotes": flat_quotes
    }
    payload_bytes = json.dumps(payload_dict, sort_keys=True).encode("utf-8")
    
    proof_hash = hashlib.sha256(payload_bytes).hexdigest()
    
    today_prefix = datetime.now().strftime("%Y/%m/%d")
    proof_obj_key = f"{today_prefix}/batch_{crawl_batch_id[:8]}_{proof_hash[:16]}.json"
    
    client.put_object(
        MINIO_BUCKET,
        proof_obj_key,
        io.BytesIO(payload_bytes),
        len(payload_bytes),
        content_type="application/json"
    )
    
    return proof_hash, proof_obj_key