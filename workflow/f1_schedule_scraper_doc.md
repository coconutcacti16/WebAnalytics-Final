# F1 Schedule, Placement, and Products Scraper Pipeline

This document explains how to execute the data collection pipeline for the F1 E-Commerce Pricing Intelligence Dashboard.

The core pipeline consists of two main Python scripts located in the `F1 Schedule:Placement:Products scraper` subdirectory.

## Prerequisites
- Python 3.8 or newer.
- Dependencies such as `requests`, `bs4`, `crawl4ai`, etc., defined in the project's requirements.
- Appropriate browser configuration for asynchronous scraping with `crawl4ai`.

## Step 1: Scrape Schedule and Products Data
**Script:** `f1_team_scraper.py`

This script pulls the target race schedule and current merchandise metrics:
1. **F1 Calendar:** Retrieves the 2025 F1 Schedule from ESPN to align product pricing with upcoming race weekends.
2. **Product Details:** Scrapes Amazon for the top 20 merchandise products corresponding to each of the 9 active F1 teams.

**How to Execute:**
```bash
cd "F1 Schedule:Placement:Products scraper"
python f1_team_scraper.py
```

**Expected Output:**
Generates intermediate CSV files named `<team>_f1_products_2025.csv` (e.g., `mercedes_f1_products_2025.csv`) containing current pricing, rank, and upcoming race details.

## Step 2: Combine Team Race Results and Price Analysis
**Script:** `generate_team_results.py`

This script processes the previously gathered data alongside real-world race outcomes:
1. Translates the schedule into specific ESPN Race IDs.
2. Scrapes the results for each race, extracting individual driver positions for the specified teams.
3. Computes team cumulative placements and price fluctuations for tracked products across race dates.
4. Generates a comprehensive dataset.

**How to Execute:**
```bash
cd "F1 Schedule:Placement:Products scraper"
python generate_team_results.py
```

**Expected Output:**
Replaces the intermediate file with a comprehensive final CSV named `<team>_combined_f1_data.csv` (e.g., `mercedes_combined_f1_data.csv`).
*Note: The intermediate CSVs are automatically deleted after a successful run to keep the working environment clean.*

## Automated Execution (Workflow)
This process can be scheduled to run autonomously using the provided GitHub Actions workflow (e.g., the YAML configuration located in this `workflow/` directory). Ensure your repository settings allow Actions to read and write to the repository if you are committing the updated dataset CSVs directly back to the project.
