import asyncio
import json
import csv
import os
import pandas as pd
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def get_actual_2026_products():
    teams = [
        {"name": "Mercedes", "search": "Mercedes F1 team products 2026"},
        {"name": "Red Bull", "search": "Red Bull F1 team products 2026"},
        {"name": "Ferrari", "search": "Ferrari F1 team products 2026"},
        {"name": "McLaren", "search": "McLaren F1 team products 2026"},
        {"name": "Aston Martin", "search": "Aston Martin F1 team products 2026"},
        {"name": "Alpine", "search": "Alpine F1 team products 2026"},
        {"name": "Williams", "search": "Williams F1 team products 2026"},
        {"name": "Sauber", "search": "Sauber F1 team products 2026"},
        {"name": "Haas", "search": "Haas F1 team products 2026"},
        {"name": "RB", "search": "Visa Cash App RB F1 team products 2026"}
    ]
    
    schema = {
        "name": "Amazon Products",
        "baseSelector": "div[data-component-type='s-search-result']",
        "fields": [
            {
                "name": "name", 
                "selector": "h2 span.a-text-normal, span.a-size-medium.a-color-base.a-text-normal", 
                "type": "text"
            },
            {
                "name": "link", 
                "selector": "h2 a.a-link-normal", 
                "type": "attribute", 
                "attribute": "href"
            }
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema)
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy, 
        cache_mode=CacheMode.BYPASS,
        wait_for="div[data-component-type='s-search-result']" # Critical wait
    )
    
    races_so_far = [
        {"Date": "Mar 13 - 15", "Name": "Qatar Airways Australian GP"},
        {"Date": "Mar 20 - 23", "Name": "Heineken Chinese GP"},
        {"Date": "Apr 3 - 6", "Name": "Aramco Japanese GP"},
        {"Date": "Apr 11 - 13", "Name": "Gulf Air Bahrain GP"}
    ]
    
    all_actual_rows = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for team in teams:
            print(f"Scraping actual data for {team['name']}...")
            url = f"https://www.amazon.com/s?k={team['search'].replace(' ', '+')}"
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success and result.extracted_content:
                try:
                    products = json.loads(result.extracted_content)
                    print(f"  Found {len(products)} products for {team['name']}")
                    # Take top 3
                    valid_products = [p for p in products if p.get('name') and p.get('link')]
                    for i, p in enumerate(valid_products[:3]):
                        full_link = p['link']
                        if full_link.startswith('/'):
                            full_link = f"https://www.amazon.com{full_link}"
                            
                        for race in races_so_far:
                            all_actual_rows.append({
                                "Team": team['name'],
                                "Race Date": race['Date'],
                                "Race Name": race['Name'],
                                "Product Rank": i + 1,
                                "Product Name": p['name'],
                                "Product Link": full_link
                            })
                except Exception as e:
                    print(f"  Error parsing: {e}")
            else:
                print(f"  Failed to scrape {team['name']}: {result.error_message if not result.success else 'No content'}")
                    
    if all_actual_rows:
        df = pd.DataFrame(all_actual_rows)
        output_path = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper/Analysis/ACTUAL_best_selling_2026.csv"
        df.to_csv(output_path, index=False)
        print(f"Actual best sellers saved to {output_path}")
    else:
        print("No actual data collected. Check selectors.")

if __name__ == "__main__":
    asyncio.run(get_actual_2026_products())
