import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://tv.kyivstar.ua/en/live-channels/55efdb72e4b0781039bc0340-pershyi-hd"
        print(f"Loading {url}")
        
        api_urls = []
        
        # Intercept network requests
        page.on("request", lambda request: api_urls.append(request.url) if "epg" in request.url or "programs" in request.url or "schedule" in request.url else None)
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Navigation error: {e}")
            
        print("Captured matching EPG API requests:")
        for u in set(api_urls):
            print(" ->", u)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
