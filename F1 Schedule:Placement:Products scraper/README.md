# F1 Schedule, Placement, and Products Scraper

This folder contains scraping scripts and combined datasets matching F1 team race placements with Amazon product metrics for individual teams.

## Contents
- **CSV Data:** Combined team-level datasets (e.g., `mercedes_combined_f1_data.csv`, `redbull_combined_f1_data.csv`)
- **Scripts:** `f1_team_scraper.py`, `generate_team_results.py`
- **Tests:** `test_amazon.py`, `test_espn.py`, `test_espn_race.py`, `test_espn_rb.py`

## How to Run
To run the primary scraper:
```bash
python f1_team_scraper.py
```
To map the products to team results:
```bash
python generate_team_results.py
```
To execute the tests, you can use `pytest`:
```bash
pytest test_amazon.py test_espn.py test_espn_race.py test_espn_rb.py
```
