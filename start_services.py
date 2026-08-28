# written by smruti sourav sahoo
import subprocess
import sys
import time

def start_vayu_stack():
    print("==================================================")
    print("?? Bootstrapping vayuIndex (APIx Engine) Stack...")
    print("==================================================")

    processes = []

    try:
        # 1. FastAPI Gateway (Port 8000)
        print("[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
        api_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd="./backend"
        )
        processes.append(("FastAPI", api_proc))
        time.sleep(2)

        # 2. Redis ETL Stream Consumer
        print("[2/3] Starting Redis ETL Stream Consumer ...")
        etl_proc = subprocess.Popen(
            [sys.executable, "pipeline/stream_consumer.py"],
            cwd="."
        )
        processes.append(("ETL Consumer", etl_proc))
        time.sleep(1)

        # 3. Next.js Frontend Dashboard (Port 3000)
        print("[3/3] Starting Next.js Dashboard on http://localhost:3000 ...")
        dash_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="./dashboard",
            shell=True
        )
        processes.append(("Next.js Dashboard", dash_proc))

        print("\n? All services running! Press Ctrl+C in this terminal to terminate all processes cleanly.\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n?? Shutting down all vayuIndex microservices...")
        for name, proc in processes:
            print(f"Terminating {name}...")
            proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    start_vayu_stack()
