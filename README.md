# Web Analytics Final Project  

**Team:** Women in STEM  

## Project Idea  

We are building an event-driven e-commerce pricing intelligence dashboard using Formula 1 merchandise as our case study.

### Why F1 for E-Commerce?

Formula 1 is a globally followed, event-based sport where demand fluctuates dramatically around race weekends and team performance. Podium finishes, championship momentum, and media coverage trigger short-term spikes in fan engagement and online purchasing behavior.

This makes F1 merchandise retail an ideal environment to study:

- Event-driven demand volatility  
- Dynamic pricing behavior  
- Competitor promotion timing  
- Stockout risk after performance surges  

Unlike general retail, F1 e-commerce provides clear, timestamped external events (race calendar and results) that allow us to directly measure how online pricing and promotional strategies respond to real-world triggers.

### Our Focus

We will:

- Scrape competitor F1 merchandise websites daily  
- Track pricing, discounts, and stock availability  
- Integrate public F1 race data via API  
- Analyze how pricing behavior shifts before and after race weekends  

Our goal is to demonstrate how event-aware web analytics can improve pricing strategy in high-volatility e-commerce environments.

## Data Collection Automation

This repository contains two main data collection pipelines that gather both F1 merchandise data and fan sentiment to fuel our pricing intelligence dashboard.

### 1. F1 Schedule, Placement, and Products Scraper Pipeline

This pipeline explains how to execute the data collection pipeline for the F1 E-Commerce Pricing Intelligence Dashboard. The core pipeline consists of two main Python scripts located in the `F1 Schedule:Placement:Products scraper` subdirectory. It is specifically designed to collect F1 race schedules, team race results, and Amazon data for top merchandise products.

**Prerequisites**
- Python 3.8 or newer.
- Dependencies such as `requests`, `bs4`, `crawl4ai`, etc., defined in the project's requirements.
- Appropriate browser configuration for asynchronous scraping with `crawl4ai`.

#### Step 1: Scrape Schedule and Products Data
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
Generates intermediate CSV files named `<team>_f1_products_2025.csv` (e.g., `mercedes_f1_products_2025.csv`) containing the extracted Amazon data for top products, including current pricing, rank, and corresponding upcoming race details.

#### Step 2: Combine Team Race Results and Price Analysis
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

**Automated Execution (Workflow)**
This process can be scheduled to run autonomously using the provided GitHub Actions workflow (e.g., the YAML configuration located in this `workflow/` directory). Ensure your repository settings allow Actions to read and write to the repository if you are committing the updated dataset CSVs directly back to the project.

---

### 2. F1 Reddit Scraper

These scripts gather fan sentiment and engagement data from various F1-related subreddits, allowing us to correlate community excitement with merchandise pricing and race events.

**Prerequisites**
- Python 3.8 or newer.
- Dependencies include `playwright`, `beautifulsoup4`, and `asyncio`.
- Since these scripts use Playwright for headless browser automation, you must install the required browser binaries before your first run:
  ```bash
  pip install playwright beautifulsoup4
  playwright install chromium
  ```

#### Historical 2025 Race Scraper (Comprehensive)
**Script:** `historical_f1_scraper.py`

This is the primary data collection script. It is designed to extract the top 100 Reddit posts for each of the 24 F1 race weekends in 2025 across 11 specific subreddits (the main `r/formula1` community and 10 specific team subreddits, including Red Bull, Mercedes, Ferrari, McLaren, and upcoming teams like Audi and Cadillac).

**How it Works**
1. **Targeted Searching:** Automatically generates search queries for each race (e.g., `(Bahrain GP OR Bahrain Grand Prix) 2025`) and applies them to each target subreddit.
2. **Engagement Focus:** Sorts search results by "Top" to capture the most engaging and highly-voted discussions.
3. **Anti-Bot Mitigation:** Reddit enforces strict rate limits. This script is built to seamlessly handle `429 Too Many Requests` errors by automatically pausing for 15 seconds and retrying before continuing.

**How to Execute**
```bash
cd "F1 Reddit scraper"
python historical_f1_scraper.py
```

**Expected Output**
Generates a master dataset named `F1_2025_Reddit_Data.csv` containing:
- **Subreddit:** The community where the post was made.
- **Race:** The specific Grand Prix the post relates to.
- **Title:** The headline of the post.
- **URL:** Direct link to the Reddit thread.
- **Upvotes:** The post's score (engagement metric).
- **Date:** The relative time the post was published.

#### Weekly Team Scraper (Targeted)
**Script:** `reddit_scraper.py`

This is a lightweight, targeted script designed for quick pulls. By default, it navigates directly to `r/RedBullRacing` and collects the top 20 posts from the past week. It serves as a great template if you only need a quick snapshot of a single team's recent performance.

**How to Execute**
```bash
cd "F1 Reddit scraper"
python reddit_scraper.py
```

**Expected Output**
Generates a focused CSV file named `RedBullRacing_Headlines.csv` containing the `Title`, `URL`, and `Upvotes` for the scraped posts.
