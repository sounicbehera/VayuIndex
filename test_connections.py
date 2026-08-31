import urllib.request
import json
import sys

def test_health():
    url = "http://localhost:8000/api/v1/health"
    print(f"Pinging health endpoint: {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print("\n[SUCCESS] System is HEALTHY:")
            print(json.dumps(data, indent=2))
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"\n[ERROR] HTTP {e.code}: {e.reason}")
        try:
            error_data = json.loads(e.read().decode())
            print(json.dumps(error_data, indent=2))
        except Exception:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n[ERROR] Failed to reach API: {e.reason}")
        print("Make sure the FastAPI server is running and accessible at http://localhost:8000.")
        sys.exit(1)

if __name__ == "__main__":
    test_health()
