# F1 Historical Product & Performance Data

This folder contains historical product data for the top F1 teams mapped across multiple years (2021-2025), alongside scripts to fetch this data.

## Contents
- **CSV Data:** `Master_F1_Products_2021.csv` through `Master_F1_Products_2025.csv`
- **Scripts:** `f1_team_scraper.py`, `generate_team_results.py`

## How to Run
To scrape top products from Amazon:
```bash
python f1_team_scraper.py
```
To map the scraped products to the race schedule and generate performance data:
```bash
python generate_team_results.py
```
