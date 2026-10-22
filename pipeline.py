
import os
import shutil
import pandas as pd
from data_quality import run_data_quality_checks


# Find the project root directory.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define the input and output paths.
RAW_FILE = os.path.join(PROJECT_ROOT, "data", "raw_sensor_logs.csv")
BRONZE_DIR = os.path.join(PROJECT_ROOT, "output", "bronze")
SILVER_DIR = os.path.join(PROJECT_ROOT, "output", "silver")
GOLD_DIR = os.path.join(PROJECT_ROOT, "output", "gold")


def run_wastewater_pipeline():
    print("Starting Wastewater Data Engineering Pipeline")

    # Create the layer folders if they do not exist.
    os.makedirs(BRONZE_DIR, exist_ok=True)
    os.makedirs(SILVER_DIR, exist_ok=True)
    os.makedirs(GOLD_DIR, exist_ok=True)

    # --------------------------------------------------
    # 1. BRONZE: Preserve the original raw sensor data.
    # --------------------------------------------------
    if not os.path.exists(RAW_FILE):
        print(f"ERROR: Raw file not found: {RAW_FILE}")
        print("Check that data/raw_sensor_logs.csv exists.")
        return

    bronze_file = os.path.join(BRONZE_DIR, "raw_sensor_logs.csv")
    shutil.copy2(RAW_FILE, bronze_file)

    print(f"Bronze layer saved: {bronze_file}")

    # Read raw data for processing.
    df = pd.read_csv(bronze_file)

    # --------------------------------------------------
    # 2. SILVER: Clean and transform the sensor data.
    # --------------------------------------------------
    required_columns = [
        "timestamp",
        "flow_rate_m3h",
        "ph",
        "dissolved_oxygen_mgL",
        "ammonia_inlet_mgL",
    ]

    # Stop if any required columns are missing.
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Convert timestamps to proper datetime values.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="raise"
    )

    # Convert sensor readings to numeric values.
    numeric_columns = [
        "flow_rate_m3h",
        "ph",
        "dissolved_oxygen_mgL",
        "ammonia_inlet_mgL",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="raise"
        )

    # Sort readings into chronological order.
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Fill missing pH values using the previous valid reading.
    df["ph_clean"] = df["ph"].ffill()

    # Stop if any pH values remain missing.
    if df["ph_clean"].isna().any():
        raise ValueError(
            "Some pH values remain missing. "
            "Check the first sensor readings."
        )

    # Four 15-minute readings represent approximately one hour.
    df["do_1hr_rolling_avg"] = (
        df["dissolved_oxygen_mgL"]
        .rolling(window=4, min_periods=1)
        .mean()
    )

    # Assign an alert category to each reading.
    def get_alert_status(row):
        if row["dissolved_oxygen_mgL"] < 1.5:
            return "CRITICAL: Low Dissolved Oxygen"

        if row["ammonia_inlet_mgL"] > 50.0:
            return "WARNING: High Ammonia Spike"

        return "NORMAL"

    df["alert_status"] = df.apply(
        get_alert_status, axis=1
    )

    # Save the cleaned dataset as Parquet.
    silver_file = os.path.join(
        SILVER_DIR, "cleaned_water_metrics.parquet"
    )

    df.to_parquet(silver_file, index=False)

    print(f"Silver layer saved: {silver_file}")

    # --------------------------------------------------
    # 3. GOLD: Create daily analytics for reporting.
    # --------------------------------------------------
    df["log_date"] = df["timestamp"].dt.date

    # Count readings with alerts and calculate daily averages.
    daily_summary = (
        df.groupby("log_date")
        .agg(
            total_readings=("timestamp", "count"),
            total_alerts=(
                "alert_status",
                lambda values: (values != "NORMAL").sum()
            ),
            critical_alerts=(
                "alert_status",
                lambda values: values.str.startswith(
                    "CRITICAL"
                ).sum()
            ),
            warning_alerts=(
                "alert_status",
                lambda values: values.str.startswith(
                    "WARNING"
                ).sum()
            ),
            avg_flow_rate_m3h=("flow_rate_m3h", "mean"),
            avg_ph=("ph_clean", "mean"),
            avg_dissolved_oxygen_mgL=(
                "dissolved_oxygen_mgL", "mean"
            ),
        )
        .reset_index()
    )

    # Round averages to two decimal places.
    average_columns = [
        "avg_flow_rate_m3h",
        "avg_ph",
        "avg_dissolved_oxygen_mgL",
    ]

    daily_summary[average_columns] = (
        daily_summary[average_columns].round(2)
    )

    # Save the Gold analytics dataset.
    gold_file = os.path.join(
        GOLD_DIR, "daily_water_summary.csv"
    )

    daily_summary.to_csv(gold_file, index=False)

    print(f"Gold layer saved: {gold_file}")

    # --------------------------------------------------
    # 4. DISPLAY A SUMMARY OF THE RESULTS.
    # --------------------------------------------------
    print("\n--- ALERTS ---")

    alerts = df[df["alert_status"] != "NORMAL"]

    if alerts.empty:
        print("No alerts found.")
    else:
        print(
            alerts[
                [
                    "timestamp",
                    "dissolved_oxygen_mgL",
                    "ammonia_inlet_mgL",
                    "alert_status",
                ]
            ].to_string(index=False)
        )

    print("\n--- GOLD DAILY SUMMARY ---")
    print(daily_summary.to_string(index=False))

    print("\nPipeline completed successfully!")

    # Run data quality checks after creating the output layers.
    print("\nRunning automated data quality checks...")

    run_data_quality_checks()

    print("\nPipeline and data quality checks completed successfully!")

if __name__ == "__main__":
    run_wastewater_pipeline()
