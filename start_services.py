# written by sounic behera
import subprocess
import time
import sys

def run_command(command, description):
    print(f"\n[EXEC] {description}")
    print(f"       > {command}")
    
    # We use subprocess.run to block execution until the command finishes
    result = subprocess.run(command, shell=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}. Halting pipeline.")
        sys.exit(1)



def main():
    print("=== INITIALIZING VAYU_INDEX DISTRIBUTED PIPELINE ===")
    
    # Step 1: Ensure all Docker containers are up and running
    run_command("docker-compose up -d", "Booting infrastructure (API, DB, Redis, Celery, Frontend)")
    
    # Step 2: Push critical backend updates to container and restart FastAPI (since volumes aren't mounted)
    subprocess.run("docker cp api/app/main.py vayu_api:/app/api/app/main.py", shell=True)
    subprocess.run("docker restart vayu_api", shell=True)
    print("\n[WAIT] Pausing 10 seconds for database and message broker connections to stabilize...")
    time.sleep(10)
    
    # Step 3: Ingestion via Google Aggregator Adapter
    subprocess.run("docker cp scraper/aggregator_client.py vayu_api:/app/scraper/aggregator_client.py", shell=True)
    subprocess.run("docker cp scraper/producer.py vayu_api:/app/scraper/producer.py", shell=True)
    run_command("docker exec -i vayu_api python -m scraper.producer", "Ingesting aggregated flight intelligence (Google Aggregator pattern)")
    
    # Step 5: Execute the econometric aggregation 
    run_command("docker exec -i vayu_api python -m analytics.calculator", "Computing Jevons CPI and writing to TimescaleDB")
    
    # Step 6: Ensure 30-day historical data is populated for presentation dashboard
    # We dynamically copy the module into the container in case the image wasn't rebuilt
    subprocess.run("docker cp analytics/seed_history.py vayu_api:/app/analytics/seed_history.py", shell=True)
    run_command("docker exec -i vayu_api python -m analytics.seed_history", "Seeding 30-day historical Jevons index trend")
    
    print("\n=== PIPELINE COMPLETE ===")
    print("Dashboard live at: http://localhost:3000")

if __name__ == "__main__":
    main()