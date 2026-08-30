# written by sounic behera
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

DB_URL = os.getenv("DB_URL", "postgresql://vayu_admin:vayu_secure_password@127.0.0.1:5433/vayu_cpi")

# Official DGCA Monthly Published Sector Fares (Benchmark Dataset)
DGCA_MONTHLY_BENCHMARKS = {
    "DEL-BOM": 5650.0,
    "DEL-BLR": 6420.0,
    "BOM-BLR": 4180.0,
    "DEL-CCU": 5890.0,
    "DEL-MAA": 6120.0,
    "BLR-HYD": 3250.0,
    "BOM-GOI": 3800.0,
}

def run_dgca_backtest(days_history: int = 30):
    """
    Evaluates 30-day high-frequency Jevons route geometric means 
    against official DGCA published monthly average corridor benchmarks.
    """
    conn = psycopg2.connect(DB_URL)
    
    # Query daily route-level geometric means from raw quotes
    query = """
        SELECT 
            departure_date,
            route_id,
            EXP(AVG(LN(total_fare))) AS jevons_route_fare,
            AVG(total_fare) AS arithmetic_mean_fare,
            COUNT(*) as sample_count
        FROM raw_flight_quotes
        WHERE is_outlier = FALSE
        GROUP BY departure_date, route_id
        ORDER BY departure_date ASC, route_id ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("[!] No historical quote data available for back-testing.")
        return None

    # Map DGCA reference benchmarks to the dataset
    df["dgca_benchmark"] = df["route_id"].map(DGCA_MONTHLY_BENCHMARKS)
    df = df.dropna(subset=["dgca_benchmark"])

    # Econometric Error Metrics Calculation
    df["absolute_error"] = (df["jevons_route_fare"] - df["dgca_benchmark"]).abs()
    df["percentage_error"] = (df["absolute_error"] / df["dgca_benchmark"]) * 100

    results_summary = []
    for route, group in df.groupby("route_id"):
        mae = group["absolute_error"].mean()
        mape = group["percentage_error"].mean()
        rmse = np.sqrt((group["absolute_error"] ** 2).mean())
        corr = group["jevons_route_fare"].corr(group["dgca_benchmark"]) if len(group) > 1 else 1.0

        results_summary.append({
            "route_id": route,
            "samples_evaluated": int(group["sample_count"].sum()),
            "avg_jevons_fare": round(float(group["jevons_route_fare"].mean()), 2),
            "dgca_benchmark_fare": float(DGCA_MONTHLY_BENCHMARKS[route]),
            "mae_inr": round(float(mae), 2),
            "mape_percent": round(float(mape), 2),
            "rmse_inr": round(float(rmse), 2)
        })

    overall_mape = df["percentage_error"].mean()
    overall_mae = df["absolute_error"].mean()
    
    print("\n" + "=" * 78)
    print("           vayuIndex (APIx) - 30-DAY DGCA BACK-TESTING EVALUATION")
    print("=" * 78)
    print(f"Total Date-Corridor Pairs Analyzed : {len(df)}")
    print(f"Aggregate Mean Absolute Error (MAE) : Rs.{overall_mae:.2f}")
    print(f"Mean Absolute Percentage Error (MAPE): {overall_mape:.2f}%")
    print(f"Tracking Accuracy Confidence Score  : {100 - overall_mape:.2f}%\n")
    print(f"{'Route ID':<10} | {'Jevons Fare':<12} | {'DGCA Ref':<10} | {'MAE (Rs.)':<10} | {'MAPE (%)':<10}")
    print("-" * 78)

    for r in results_summary:
        print(f"{r['route_id']:<10} | Rs.{r['avg_jevons_fare']:<11.2f} | Rs.{r['dgca_benchmark_fare']:<9.2f} | Rs.{r['mae_inr']:<9.2f} | {r['mape_percent']:<9.2f}%")
    print("=" * 78 + "\n")

    return {
        "overall_mae": round(float(overall_mae), 2),
        "overall_mape": round(float(overall_mape), 2),
        "tracking_confidence": round(float(100 - overall_mape), 2),
        "corridor_breakdown": results_summary
    }

if __name__ == "__main__":
    run_dgca_backtest()