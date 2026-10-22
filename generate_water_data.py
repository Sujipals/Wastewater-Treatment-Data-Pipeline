import os
import random
import pandas as pd
from datetime import datetime, timedelta

# Create data directory
os.makedirs("data", exist_ok=True)

# Generate 24 hours of 15-minute interval sensor logs
start_time = datetime(2026, 10, 22, 0, 0, 0)
records = []

for i in range(96): # 96 intervals of 15 mins = 24 hours
    current_time = start_time + timedelta(minutes=15 * i)
    
    # Simulate normal biological water metrics with occasional spikes
    flow_rate = round(random.uniform(450.0, 600.0), 2)
    ph = round(random.uniform(6.8, 7.8), 2)
    dissolved_oxygen = round(random.uniform(1.8, 3.5), 2) # Normal DO level: 2.0 - 3.0 mg/L
    ammonia_inlet = round(random.uniform(22.0, 35.0), 2) # mg/L
    
    # Inject simulated sensor faults (nulls) and pollution spikes
    if i in [10, 11]: 
        ph = None  # Sensor offline fault
    if i in [45, 46, 47]: 
        dissolved_oxygen = 0.8  # Critical drop in Oxygen (Aeration fault)
    if i in [70, 71]: 
        ammonia_inlet = 65.0  # High organic load spike

    records.append({
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "flow_rate_m3h": flow_rate,
        "ph": ph,
        "dissolved_oxygen_mgL": dissolved_oxygen,
        "ammonia_inlet_mgL": ammonia_inlet
    })

df = pd.DataFrame(records)
df.to_csv("data/raw_sensor_logs.csv", index=False)
print("✅ Created 'data/raw_sensor_logs.csv' with simulated IoT sensor readings!")