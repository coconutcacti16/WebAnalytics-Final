import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Add user agent to look less like a bot
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("Navigating to Reddit...")
        response = await page.goto("https://www.reddit.com/r/RedBullRacing/top/?t=week")
        print(f"Status code: {response.status}")
        
        await asyncio.sleep(5)
        
        content = await page.content()
        with open("reddit_page.html", "w") as f:
            f.write(content)
            
        print(f"Saved HTML. Length: {len(content)}")
        
        posts = await page.locator("shreddit-post").all()
        print(f"Found {len(posts)} shreddit-post elements")
        
        # If no shreddit-post, look for other post elements
        if len(posts) == 0:
            posts2 = await page.locator(".Post").all()
            print(f"Found {len(posts2)} .Post elements")
            posts3 = await page.locator("article").all()
            print(f"Found {len(posts3)} article elements")
            
        await browser.close()

asyncio.run(main())
