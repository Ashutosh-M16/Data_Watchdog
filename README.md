# Data_Watchdog

Automated Data Watchdog — initial project skeleton.

This repository contains the starting scaffold for the Automated Data Watchdog project: an analytics system that ingests business data, performs cleaning, KPI and trend analysis, detects anomalies, generates business insights, and sends alerts.

What's included in this commit:

- Project structure with core modules (ingestion, preprocessing, analytics, anomaly, insights, alerts, database, utils).
- Minimal Streamlit app entrypoint (app.py) to upload and preview data.
- Sample data generator and a small sample dataset (data/sample/sample_business_data.csv).
- Basic tests folder with a simple loader test.
- .env.example and requirements.txt.

Next steps (phase 1-3):
- Implement detailed preprocessing logic and data-quality reporting.
- Implement KPI calculations and trend analysis.
- Implement anomaly detection and severity classification.
- Expand tests and add CI configuration.

Run locally:
1. python -m venv .venv
2. source .venv/bin/activate (mac/linux) or .venv\Scripts\activate (Windows)
3. pip install -r requirements.txt
4. streamlit run app.py

License: MIT
