#!/usr/bin/env python3
"""Quick test to see what URL levi.in actually loads"""
import asyncio
from playwright.async_api import async_playwright

async def test_levi_url():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Navigating to https://levi.in/...")
        await page.goto("https://levi.in/", wait_until="networkidle", timeout=15000)

        final_url = page.url
        title = await page.title()

        print(f"\nFinal URL: {final_url}")
        print(f"Page Title: {title}")

        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_levi_url())
