import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def scrape_amazon():
    # URL for searching "Red Bull F1 racing team"
    base_url = "https://www.amazon.com/s?k=Red+Bull+F1+racing+team"
    
    # CSS Strategy for Amazon product cards
    schema = {
        "name": "Amazon Products",
        "baseSelector": "div[data-component-type='s-search-result']",
        "fields": [
            {
                "name": "product_name",
                "selector": "h2 span, .a-size-medium.a-color-base.a-text-normal, .a-size-base-plus.a-color-base.a-text-normal",
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
        print(f"Scraping {base_url}")
        result = await crawler.arun(url=base_url, config=run_config)
        
        if not result.success:
            print(f"Failed to scrape: {result.error_message}")
            return
            
        try:
            products = json.loads(result.extracted_content)
            print(f"Found {len(products)} products.")
            for i, p in enumerate(products[:20]):
                name = p.get('product_name', 'N/A')
                # Some prices might be multiple strings if there are whole and fractional parts. The .a-offscreen should have the full string.
                price = p.get('price', 'N/A')
                print(f"{i+1}. {name} | {price}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_amazon())
