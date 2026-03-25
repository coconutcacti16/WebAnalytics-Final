# F1 Schedule & Amazon Product Scraper

## Overview
We've built a suite of python scrapers to gather and connect F1 2025 schedule data, live Amazon product data for Red Bull Racing, and real-time ESPN race results.

## What was completed
1. **ESPN Schedule Parsing**: Fetched the ESPN 2025 schedule, finding `24` distinct race weekends.
2. **Amazon Parsing Validation**: Genericized the Headless browsing with `Crawl4AI` to run against searches for all 10 active "F1 racing team" brands.
3. **Data Combination**: Merged the two inputs mapping each race weekend to current top 20 items per team.
4. **Driver Results, Repeated Products, & File Consolidation**: Built `generate_team_results.py` to cross-reference our Amazon scraping with race IDs mapped from ESPN. It dynamically scrapes each race's results page for the top drivers per team. 
   - **Red Bull:** 4 drivers across two sub-brands (`VER/LAW` for Red Bull, `TSU/HAD` for Racing Bulls). 
   - **Remaining Teams:** `NOR/PIA` (McLaren), `LEC/HAM` (Ferrari), `RUS/ANT` (Mercedes), `ALB/SAI` (Williams), `ALO/STR` (Aston Martin), `HUL/BOR` (Sauber), `GAS/DOO` (Alpine), `OCO/BEA` (Haas).
   
   It calculates price changes on repeated items and calculates `Team Cumulative Placement` and `Team Placement Change`. This script outputs everything to a single, consolidated `{team}_combined_f1_data.csv` and deletes any intermediate files.

## Validation Results
- Running `python3 f1_team_scraper.py` successfully generates 10 intermediate CSVs mapping schedule to team products.
- Running `python3 generate_team_results.py` successfully produces 10 final consolidated CSV files that merge Amazon products to ESPN Race parameters and specific Driver placements. It handles parsing Driver names cleanly and accurately calculates price shifts between recurring item appearances.
- A total of 10 master CSV files (`{team}_combined_f1_data.csv`) are ultimately generated, cleanly avoiding file clutter. New calculated columns were also added:
  - `Product Rank`: Tracked across iterations.
  - `Team Cumulative Placement`: The sum of all active drivers' numerical positions per race.
  - `Team Placement Change`: The delta between the current race's cumulative total and the chronologically previous race's total.

## Files Modified/Created
- `f1_team_scraper.py`
- `generate_team_results.py`
- `10 {team}_combined_f1_data.csv` files
- `test_espn.py`, `test_amazon.py`, `test_espn_race.py`, `test_espn_rb.py` (Investigation Scripts)
