# 🌊 Azure Wastewater Treatment Data Pipeline & IoT Analytics

## 📋 Overview
An end-to-end cloud-native data engineering pipeline designed to ingest, clean, feature-engineer, and analyze high-frequency time-series IoT sensor data from a wastewater treatment plant. This project simulates a modern **Medallion Architecture** using Python and demonstrates analytical querying capabilities via **Azure Synapse Analytics T-SQL**.

---

## 🛠️ Tech Stack & Architecture
* **Language:** Python (Pandas, PyArrow)
* **Data Engineering Pattern:** Medallion Architecture (Bronze -> Silver -> Gold)
* **Storage Format:** Columnar Parquet
* **Cloud & Query Concepts:** Azure Synapse Analytics, Serverless SQL Pools, T-SQL

---

## 📂 Project Structure
```text
Water_Project/
│
├── data/
│   └── raw_sensor_logs.csv         # Bronze Layer: Raw IoT sensor inputs
│
├── output/
│   └── cleaned_water_metrics.parquet # Gold Layer: Curated, transformed dataset
│
├── sql/
│   └── analysis.sql                # T-SQL scripts for analytical querying
│
├── generate_water_data.py          # Script simulating IoT sensor telemetry
└── pipeline.py                     # Main ELT cleaning and feature engineering script