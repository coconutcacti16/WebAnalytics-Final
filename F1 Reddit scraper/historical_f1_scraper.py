import asyncio
import csv
import logging
import urllib.parse
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

RACES = [
    "Australian GP", "Chinese GP", "Japanese GP", "Bahrain GP", 
    "Saudi Arabian GP", "Miami GP", "Emilia Romagna GP", "Monaco GP", 
    "Spanish GP", "Canadian GP", "Austrian GP", "British GP", 
    "Belgian GP", "Hungarian GP", "Dutch GP", "Italian GP", 
    "Azerbaijan GP", "Singapore GP", "United States GP", "Mexican GP", 
    "São Paulo GP", "Las Vegas GP", "Qatar GP", "Abu Dhabi GP"
]

def generate_queries(race):
    base = race.replace("GP", "").strip()
    return f'({base} GP OR {base} Grand Prix) 2025'

SUBREDDITS = [
    "formula1",
    "AlpineF1Team",
    "AstonMartinFormula1",
    "AudiF1",
    "CadillacF1",
    "scuderiaferrari",
    "haasf1team",
    "McLarenFormula1",
    "mercedesamgf1",
    "RedBullRacing",
    "WilliamsF1"
]

async def scrape_reddit():
    # Initialize CSV
    with open("F1_2025_Reddit_Data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Subreddit", "Race", "Title", "URL", "Upvotes", "Date"])
        writer.writeheader()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        for sub in SUBREDDITS:
            for race in RACES:
                query = generate_queries(race)
                q_encoded = urllib.parse.quote(query)
                url = f"https://www.reddit.com/r/{sub}/search/?q={q_encoded}&restrict_sr=1&sort=top"
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await page.goto(url, wait_until="domcontentloaded")
                        if response.status == 200:
                            await asyncio.sleep(2)
                            
                            # Scroll twice to load more posts if available
                            for _ in range(2):
                                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                                await asyncio.sleep(1)

                            content = await page.content()
                            soup = BeautifulSoup(content, "html.parser")
                            
                            posts_extracted = []
                            for a in soup.find_all("a"):
                                href = a.get("href", "")
                                if "/comments/" in href:
                                    title = a.get_text(strip=True)
                                    if not title: continue
                                    
                                    container = a.find_parent("div")
                                    if container:
                                        parent2 = container.find_parent("div")
                                        if parent2:
                                            text = parent2.get_text(separator='|', strip=True)
                                            if "Show results from" in text:
                                                continue
                                            
                                            date_match = re.search(r'·\|([^|]+ago)', text)
                                            votes_match = re.search(r'\|([^|]+)\|votes', text)
                                            date = date_match.group(1).strip() if date_match else "Unknown"
                                            votes = votes_match.group(1).strip() if votes_match else "0"
                                            
                                            url_full = f"https://www.reddit.com{href}" if href.startswith('/') else href
                                            if not any(p['URL'] == url_full for p in posts_extracted):
                                                posts_extracted.append({
                                                    "Title": title,
                                                    "URL": url_full,
                                                    "Upvotes": votes,
                                                    "Date": date
                                                })

                            logging.info(f"r/{sub} - {race}: Found {len(posts_extracted)} posts")
                            
                            if posts_extracted:
                                posts_extracted = posts_extracted[:100]
                                with open("F1_2025_Reddit_Data.csv", "a", newline="", encoding="utf-8") as f:
                                    writer = csv.DictWriter(f, fieldnames=["Subreddit", "Race", "Title", "URL", "Upvotes", "Date"])
                                    for p in posts_extracted:
                                        p["Subreddit"] = sub
                                        p["Race"] = race
                                        writer.writerow(p)

                            break # Success
                        elif response.status == 429:
                            logging.warning(f"Rate limit hit for r/{sub} - {race}, sleeping for 15 seconds...")
                            await asyncio.sleep(15)
                        else:
                            logging.error(f"Error {response.status} for r/{sub} - {race}")
                            break # Unrecoverable error
                    except Exception as e:
                        logging.error(f"Exception for r/{sub} - {race}: {e}")
                        if attempt == max_retries - 1:
                            break
                        await asyncio.sleep(5)
                    
                await asyncio.sleep(1) # respect rate limit between races
                
        await browser.close()
        logging.info("Scraping completed!")

if __name__ == "__main__":
    asyncio.run(scrape_reddit())
