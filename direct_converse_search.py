#!/usr/bin/env python3
"""
Direct Playwright script - searches Chuck 70 in ~10 seconds
NO AI agent - direct script for guaranteed fast execution
"""
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

async def search_converse_direct():
    """Direct search on converse.in - completes in ~10-15 seconds"""

    print("🚀 Starting DIRECT Playwright search (no AI agent)...")
    print("   This will search 'Chuck 70' within 10-15 seconds\n")

    async with async_playwright() as p:
        # Launch browser with video recording
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        # Create context with video
        context = await browser.new_context(
            record_video_dir="video-analysis-agent/converse_direct_test",
            viewport={'width': 1920, 'height': 1080},
            record_video_size={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        start_time = time.time()

        print("⏱️  0s: Navigating to https://www.converse.in/...")
        try:
            # Navigate - don't wait for networkidle
            await page.goto("https://www.converse.in/", wait_until="domcontentloaded", timeout=10000)
            print(f"⏱️  {time.time()-start_time:.1f}s: Page loaded")
        except Exception as e:
            print(f"⚠️  Navigation timeout (continuing anyway): {e}")

        # Wait a moment for page to stabilize
        await asyncio.sleep(2)
        print(f"⏱️  {time.time()-start_time:.1f}s: Waiting for page to stabilize...")

        # Try to close any popups
        try:
            # Common popup selectors
            popup_selectors = [
                "button[aria-label='Close']",
                "button.close",
                "[class*='close']",
                "[class*='dismiss']"
            ]
            for selector in popup_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click(timeout=1000)
                        print(f"⏱️  {time.time()-start_time:.1f}s: Closed popup")
                        break
                except:
                    pass
        except:
            pass

        print(f"⏱️  {time.time()-start_time:.1f}s: Looking for search icon...")

        # Find and click search icon - try multiple strategies
        search_clicked = False
        search_selectors = [
            "button[aria-label*='Search']",
            "button[aria-label*='search']",
            "a[aria-label*='Search']",
            "a[aria-label*='search']",
            "[data-test='search']",
            ".search-icon",
            "#search-icon",
            "button:has-text('Search')",
            "svg[class*='search']",
        ]

        for selector in search_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.locator(selector).first.click(timeout=3000)
                    print(f"⏱️  {time.time()-start_time:.1f}s: ✅ Clicked search icon")
                    search_clicked = True
                    break
            except Exception as e:
                continue

        if not search_clicked:
            print(f"⏱️  {time.time()-start_time:.1f}s: ⚠️  Could not find search icon, trying input field directly")

        await asyncio.sleep(1)

        # Find search input and enter text
        input_selectors = [
            "input[type='search']",
            "input[placeholder*='Search']",
            "input[placeholder*='search']",
            "input[name='search']",
            "input[aria-label*='Search']",
            "#search",
            ".search-input"
        ]

        text_entered = False
        for selector in input_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.locator(selector).first.fill("Chuck 70", timeout=3000)
                    print(f"⏱️  {time.time()-start_time:.1f}s: ✅ Entered 'Chuck 70'")
                    text_entered = True
                    await asyncio.sleep(1)

                    # Press Enter to search
                    await page.locator(selector).first.press("Enter")
                    print(f"⏱️  {time.time()-start_time:.1f}s: ✅ Pressed Enter to search")
                    break
            except Exception as e:
                continue

        if not text_entered:
            print(f"⏱️  {time.time()-start_time:.1f}s: ❌ Could not find search input")
        else:
            # Wait for results
            print(f"⏱️  {time.time()-start_time:.1f}s: Waiting for search results...")
            await asyncio.sleep(3)

            # Check if we have results
            current_url = page.url
            print(f"⏱️  {time.time()-start_time:.1f}s: Current URL: {current_url}")

            if "search" in current_url.lower() or "chuck" in current_url.lower():
                print(f"⏱️  {time.time()-start_time:.1f}s: ✅ Search results page loaded!")
            else:
                print(f"⏱️  {time.time()-start_time:.1f}s: ⚠️  May still be on home page")

        # Final wait
        await asyncio.sleep(2)

        total_time = time.time() - start_time
        print(f"\n⏱️  Total time: {total_time:.1f} seconds")
        print(f"✅ Test complete!")

        # Close and save video
        await context.close()
        await browser.close()

        # Get video path
        video_dir = Path("video-analysis-agent/converse_direct_test")
        if video_dir.exists():
            video_files = list(video_dir.glob("*.webm"))
            if video_files:
                video_path = video_files[0]
                final_path = video_dir.parent / "converse_direct_search.webm"
                video_path.rename(final_path)
                size_mb = final_path.stat().st_size / (1024 * 1024)
                print(f"\n📹 Video saved: {final_path}")
                print(f"📊 Video size: {size_mb:.2f} MB")
                print(f"⏱️  Video duration: ~{total_time:.0f} seconds")
                return str(final_path)

        return None

async def main():
    print("="*60)
    print("DIRECT CONVERSE SEARCH - NO AI AGENT")
    print("="*60)
    print()

    video_path = await search_converse_direct()

    print("\n" + "="*60)
    if video_path:
        print("SUCCESS! Video shows actual search execution")
        print(f"Video: {video_path}")
    else:
        print("Video may not have been saved properly")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
