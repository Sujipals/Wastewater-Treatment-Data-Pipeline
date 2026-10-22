import os
import pandas as pd

def run_wastewater_pipeline():
    print("🚀 Starting Wastewater Treatment Local Pipeline (Pandas Engine)...\n")

    # 1. Ingest Raw Sensor Data (Bronze Layer)
    csv_path = "data/raw_sensor_logs.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found. Run generate_water_data.py first!")
        return

    df = pd.read_csv(csv_path)

    # 2. Type Casting & Timestamp Parsing
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["flow_rate_m3h"] = df["flow_rate_m3h"].astype(float)
    df["ph"] = df["ph"].astype(float)
    df["dissolved_oxygen_mgL"] = df["dissolved_oxygen_mgL"].astype(float)
    df["ammonia_inlet_mgL"] = df["ammonia_inlet_mgL"].astype(float)

    # 3. Handle Sensor Faults: Forward Fill Missing pH Readings
    df["ph_clean"] = df["ph"].ffill()

    # 4. Feature Engineering: 1-Hour Rolling Average for Dissolved Oxygen
    df["do_1hr_rolling_avg"] = df["dissolved_oxygen_mgL"].rolling(window=4, min_periods=1).mean()

    # 5. Flag Operational Anomaly Alerts
    def get_alert_status(row):
        if row["dissolved_oxygen_mgL"] < 1.5:
            return "CRITICAL: Low Dissolved Oxygen"
        elif row["ammonia_inlet_mgL"] > 50.0:
            return "WARNING: High Ammonia Spike"
        else:
            return "NORMAL"

    df["alert_status"] = df.apply(get_alert_status, axis=1)

    # 6. Display Results in Terminal
    print("--- 🚨 DETECTED ANOMALIES & SENSOR ALERTS ---")
    alerts_df = df[df["alert_status"] != "NORMAL"]
    if not alerts_df.empty:
        print(alerts_df[["timestamp", "ph_clean", "dissolved_oxygen_mgL", "ammonia_inlet_mgL", "alert_status"]].to_string(index=False))
    else:
        print("No critical alerts found.")

    print("\n--- 📊 CLEANED & FEATURE-ENGINEERED DATA SAMPLE (First 10 Rows) ---")
    print(df[["timestamp", "flow_rate_m3h", "ph_clean", "do_1hr_rolling_avg", "alert_status"]].head(10).to_string(index=False))

    # 7. Write Curated Output to Parquet (Gold Layer)
    os.makedirs("output", exist_ok=True)
    output_path = "output/cleaned_water_metrics.parquet"
    df.to_parquet(output_path, index=False)
    print(f"\n✅ Wastewater Pipeline Complete! Curated dataset saved to '{output_path}'")

if __name__ == "__main__":
    run_wastewater_pipeline()