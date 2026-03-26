# F1 Reddit Scraper Documentation

This document explains the Reddit data collection tools developed for the F1 E-Commerce Pricing Intelligence project. These scripts gather fan sentiment and engagement data from various F1-related subreddits, allowing us to correlate community excitement with merchandise pricing and race events.

The `F1 Reddit scraper` directory contains two scraping tools.

## Prerequisites
- Python 3.8 or newer.
- Dependencies include `playwright`, `beautifulsoup4`, and `asyncio`.
- Since these scripts use Playwright for headless browser automation, you must install the required browser binaries before your first run:
  ```bash
  pip install playwright beautifulsoup4
  playwright install chromium
  ```

## 1. Historical 2025 Race Scraper (Comprehensive)
**Script:** `historical_f1_scraper.py`

This is the primary data collection script. It is designed to extract the top 100 Reddit posts for each of the 24 F1 race weekends in 2025 across 11 specific subreddits (the main `r/formula1` community and 10 specific team subreddits, including Red Bull, Mercedes, Ferrari, McLaren, and upcoming teams like Audi and Cadillac).

### How it Works
1. **Targeted Searching:** Automatically generates search queries for each race (e.g., `(Bahrain GP OR Bahrain Grand Prix) 2025`) and applies them to each target subreddit.
2. **Engagement Focus:** Sorts search results by "Top" to capture the most engaging and highly-voted discussions.
3. **Anti-Bot Mitigation:** Reddit enforces strict rate limits. This script is built to seamlessly handle `429 Too Many Requests` errors by automatically pausing for 15 seconds and retrying before continuing.

### How to Execute
```bash
cd "F1 Reddit scraper"
python historical_f1_scraper.py
```

### Expected Output
Generates a master dataset named `F1_2025_Reddit_Data.csv` containing:
- **Subreddit:** The community where the post was made.
- **Race:** The specific Grand Prix the post relates to.
- **Title:** The headline of the post.
- **URL:** Direct link to the Reddit thread.
- **Upvotes:** The post's score (engagement metric).
- **Date:** The relative time the post was published.

## 2. Weekly Team Scraper (Targeted)
**Script:** `reddit_scraper.py`

This is a lightweight, targeted script designed for quick pulls. By default, it navigates directly to `r/RedBullRacing` and collects the top 20 posts from the past week. It serves as a great template if you only need a quick snapshot of a single team's recent performance.

### How to Execute
```bash
cd "F1 Reddit scraper"
python reddit_scraper.py
```

### Expected Output
Generates a focused CSV file named `RedBullRacing_Headlines.csv` containing the `Title`, `URL`, and `Upvotes` for the scraped posts.
