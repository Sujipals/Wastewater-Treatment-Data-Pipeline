          
import pandas as pd


# Read the Silver layer produced by the pipeline.
FILE_PATH = "output/silver/cleaned_water_metrics.parquet"


def run_data_quality_checks():
    print("Starting data quality checks...\n")

    # Load the cleaned data.
    df = pd.read_parquet(FILE_PATH)

    # Define the columns that must exist.
    required_columns = [
        "timestamp",
        "flow_rate_m3h",
        "ph_clean",
        "dissolved_oxygen_mgL",
        "ammonia_inlet_mgL",
        "alert_status",
    ]

    # Check 1: Dataset must contain records.
    assert len(df) > 0, "FAIL: Dataset is empty"
    print("PASS: Dataset contains records")

    # Check 2: All required columns must exist.
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    assert not missing_columns, (
        f"FAIL: Missing columns: {missing_columns}"
    )
    print("PASS: Required columns exist")

    # Check 3: Cleaned pH must have no missing values.
    assert df["ph_clean"].notna().all(), (
        "FAIL: Missing cleaned pH values"
    )
    print("PASS: Cleaned pH has no missing values")

    # Check 4: Timestamps must be valid.
    assert df["timestamp"].notna().all(), (
        "FAIL: Invalid timestamps found"
    )
    print("PASS: Timestamps are valid")

    # Check 5: Each timestamp should be unique.
    assert not df["timestamp"].duplicated().any(), (
        "FAIL: Duplicate timestamps found"
    )
    print("PASS: No duplicate timestamps")

    # Check 6: Alert categories must be recognized.
    valid_alerts = {
        "NORMAL",
        "CRITICAL: Low Dissolved Oxygen",
        "WARNING: High Ammonia Spike",
    }

    assert df["alert_status"].isin(valid_alerts).all(), (
        "FAIL: Unexpected alert category"
    )
    print("PASS: Alert categories are valid")

    # Check 7: Sensor readings must not be negative.
    non_negative_columns = [
        "flow_rate_m3h",
        "dissolved_oxygen_mgL",
        "ammonia_inlet_mgL",
    ]

    for col in non_negative_columns:
        assert (df[col] >= 0).all(), (
            f"FAIL: Negative values found in {col}"
        )

    print("PASS: Non-negative sensor readings")

    # Check 8: pH should be within its usual 0–14 scale.
    assert df["ph_clean"].between(0, 14).all(), (
        "FAIL: pH values outside the 0–14 scale"
    )
    print("PASS: pH values are within the 0–14 scale")

    print("\nAll data quality checks passed!")
    print(f"Total records checked: {len(df)}")


if __name__ == "__main__":
    run_data_quality_checks()
