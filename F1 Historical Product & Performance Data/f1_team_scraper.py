import requests
from bs4 import BeautifulSoup
import asyncio
import json
import csv
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

def get_f1_schedule():
    """Fetches the 2025 F1 Schedule from ESPN."""
    url = "https://www.espn.com/f1/schedule/_/year/2025"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule = []
    
    table = soup.find('table')
    if not table:
        print("No schedule table found on ESPN.")
        return schedule
        
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            date_text = cols[0].text.strip()
            race_text = cols[1].text.strip()
            
            # Skip header row or irrelevant rows
            if date_text.lower() == 'dates' or not date_text:
                continue
                
            schedule.append({
                "Race Date": date_text,
                "Race Name": race_text
            })
            
    print(f"Extracted {len(schedule)} races from the schedule.")
    return schedule

async def get_amazon_top_products(search_term):
    """Fetches the top 20 racing team products from Amazon using Crawl4AI."""
    import urllib.parse
    encoded_search = urllib.parse.quote_plus(search_term)
    base_url = f"https://www.amazon.com/s?k={encoded_search}"
    top_products = []
    
    schema = {
        "name": "Amazon Products",
        "baseSelector": "div[data-component-type='s-search-result']",
        "fields": [
            {
                "name": "product_name",
                "selector": ".a-size-medium.a-color-base.a-text-normal, .a-size-base-plus.a-color-base.a-text-normal",
                "type": "text"
            },
            {
                "name": "price",
                "selector": ".a-price .a-offscreen",
                "type": "text"
            }
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        wait_for="div[data-component-type='s-search-result']"
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print(f"Scraping Amazon products at {base_url}")
        result = await crawler.arun(url=base_url, config=run_config)
        
        if not result.success:
            print(f"Failed to scrape Amazon: {result.error_message}")
            return top_products
            
        try:
            products = json.loads(result.extracted_content)
            print(f"Found {len(products)} products on Amazon page.")
            for i, p in enumerate(products[:20]):
                name = p.get('product_name', 'N/A')
                price = p.get('price', 'N/A')
                top_products.append({
                    "Product Rank": i + 1,
                    "Product Name": name,
                    "Price": price
                })
        except Exception as e:
            print(f"Error parsing JSON from Crawl4AI: {e}")
            
    return top_products

def generate_csv(schedule, top_products, output_file):
    """Generates the combined CSV with the schedule and product data."""
    if not schedule or not top_products:
        print("Missing schedule or product data. CSV will not be generated.")
        return
        
    print(f"Generating {output_file}...")
    headers = ["Race Date", "Race Name", "Product Rank", "Product Name", "Price"]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for race in schedule:
                for product in top_products:
                    row = {
                        "Race Date": race["Race Date"],
                        "Race Name": race["Race Name"],
                        "Product Rank": product["Product Rank"],
                        "Product Name": product["Product Name"],
                        "Price": product["Price"]
                    }
                    writer.writerow(row)
                    
        print(f"Successfully wrote data for {len(schedule)} races to {output_file}.")
    except Exception as e:
        print(f"Failed to write CSV: {e}")

async def main():
    print("Starting F1 Team Products Scraper...")
    
    # Define teams to scrape
    teams = [
        {"name": "redbull", "search_term": "Red Bull F1 racing team"},
        {"name": "mclaren", "search_term": "McLaren F1 racing team"},
        {"name": "ferrari", "search_term": "Ferrari F1 racing team"},
        {"name": "mercedes", "search_term": "Mercedes F1 racing team"},
        {"name": "williams", "search_term": "Williams F1 racing team"},
        {"name": "astonmartin", "search_term": "Aston Martin F1 racing team"},
        {"name": "sauber", "search_term": "Sauber F1 racing team"},
        {"name": "alpine", "search_term": "Alpine F1 racing team"},
        {"name": "haas", "search_term": "Haas F1 racing team"}
    ]
    
    # 1. Get the Schedule (only need to do this once)
    schedule = get_f1_schedule()
    
    for team in teams:
        team_name = team["name"]
        search_term = team["search_term"]
        output_csv = f"{team_name}_f1_products_2025.csv"
        
        print(f"\n--- Processing {team_name.upper()} ---")
        
        # 2. Get the Products for this team
        top_products = await get_amazon_top_products(search_term)
        
        # 3. Generate the CSV for this team
        generate_csv(schedule, top_products, output_csv)
        
    print("\nAll scraping processes complete.")

if __name__ == "__main__":
    asyncio.run(main())
