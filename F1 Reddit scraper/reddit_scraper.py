import asyncio
from playwright.async_api import async_playwright
import csv

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("Navigating to Reddit...")
        response = await page.goto("https://www.reddit.com/r/RedBullRacing/top/?t=week")
        
        # We need to collect top 20 headlines
        target_count = 20
        posts_data = []
        collected_urls = set()
        
        # Scroll and collect
        retries = 0
        max_retries = 20
        
        while len(posts_data) < target_count and retries < max_retries:
            # Wait a bit for posts to render
            await asyncio.sleep(2)
            
            # Find all currently loaded posts
            posts = await page.locator("shreddit-post").all()
            
            for post in posts:
                try:
                    title = await post.get_attribute("post-title")
                    url = await post.get_attribute("content-href")
                    score = await post.get_attribute("score")
                    
                    if url and url not in collected_urls and title:
                        collected_urls.add(url)
                        posts_data.append({
                            "Title": title.strip(),
                            "URL": f"https://www.reddit.com{url}" if url.startswith('/') else url,
                            "Upvotes": score
                        })
                except Exception as e:
                    pass
                
                if len(posts_data) >= target_count:
                    break
                    
            print(f"Collected {len(posts_data)}/{target_count} posts...")
            
            if len(posts_data) < target_count:
                # Scroll down
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                retries += 1
                
        await browser.close()
        
        if posts_data:
            # Replaced '/' with '_' in the filename as macOS doesn't allow slashes in filenames
            with open("RedBullRacing_Headlines.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Title", "URL", "Upvotes"])
                writer.writeheader()
                writer.writerows(posts_data)
            print("Successfully saved 20 posts to RedBullRacing_Headlines.csv")
        else:
            print("Failed to find any posts.")

asyncio.run(main())
