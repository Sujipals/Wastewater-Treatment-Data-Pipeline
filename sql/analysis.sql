-- =====================================================================
-- Azure Synapse T-SQL: Wastewater Treatment Gold Layer Analytics
-- =====================================================================

-- 1. Query the Parquet file directly (Serverless SQL Pool style)
-- This reads your local 'output/cleaned_water_metrics.parquet' file using SQL
SELECT 
    CAST(timestamp AS DATE) AS LogDate,
    COUNT(CASE WHEN alert_status <> 'NORMAL' THEN 1 END) AS TotalAlerts,
    AVG(flow_rate_m3h) AS AvgFlowRate,
    AVG(do_1hr_rolling_avg) AS AvgDissolvedOxygen
FROM 
    OPENROWSET(
        BULK 'output/cleaned_water_metrics.parquet',
        FORMAT = 'PARQUET'
    ) AS [r]
GROUP BY CAST(timestamp AS DATE);

-- 2. Find all critical operational anomaly incidents
SELECT 
    timestamp,
    ph_clean,
    dissolved_oxygen_mgL,
    ammonia_inlet_mgL,
    alert_status
FROM 
    OPENROWSET(
        BULK 'output/cleaned_water_metrics.parquet',
        FORMAT = 'PARQUET'
    ) AS [r]
WHERE alert_status <> 'NORMAL'
ORDER BY timestamp DESC;

-- Query daily aggregate metrics and alert counts from the Gold Parquet layer
SELECT 
    CAST(timestamp AS DATE) AS LogDate,
    COUNT(CASE WHEN alert_status <> 'NORMAL' THEN 1 END) AS TotalAlerts,
    AVG(flow_rate_m3h) AS AvgFlowRate,
    AVG(do_1hr_rolling_avg) AS AvgDissolvedOxygen
FROM 
    OPENROWSET(
        BULK 'output/cleaned_water_metrics.parquet',
        FORMAT = 'PARQUET'
    ) AS [r]
GROUP BY CAST(timestamp AS DATE);