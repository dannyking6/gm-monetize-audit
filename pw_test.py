import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                    args=['--no-sandbox', '--disable-dev-shm-usage'])
        pg = await b.new_page()
        await pg.goto('https://example.com', timeout=30000)
        print('title:', await pg.title())
        await b.close()

asyncio.run(main())
