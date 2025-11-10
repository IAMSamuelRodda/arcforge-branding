#!/usr/bin/env python3
"""
Capture screenshots of reference websites for ArchForge design inspiration
"""

from playwright.sync_api import sync_playwright
import time

sites = [
    {
        "name": "Guillaume Nicollet",
        "url": "https://www.guillaumenicollet.com/",
        "focus": "Journey-based scrolling, skills section side-scroll"
    },
    {
        "name": "Replit Agent3",
        "url": "https://replit.com/agent3",
        "focus": "Animations, graphics flow"
    },
    {
        "name": "Astralab",
        "url": "https://astralab.framer.website/",
        "focus": "Cosmic theme, brand design"
    }
]

def capture_site(page, site, index):
    """Capture screenshots of a website"""
    print(f"\n{'='*60}")
    print(f"Capturing: {site['name']}")
    print(f"URL: {site['url']}")
    print(f"Focus: {site['focus']}")
    print(f"{'='*60}")

    try:
        # Navigate with proper wait strategy
        page.goto(site['url'], wait_until="load", timeout=60000)

        # Wait for content to load
        time.sleep(3)

        # Capture full page screenshot
        screenshot_path = f"/home/samuel/repos/arcforge-branding/referances/images/captured_{index}_full.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"✓ Full page screenshot saved: {screenshot_path}")

        # Capture viewport screenshot (hero section)
        viewport_path = f"/home/samuel/repos/arcforge-branding/referances/images/captured_{index}_hero.png"
        page.screenshot(path=viewport_path)
        print(f"✓ Hero screenshot saved: {viewport_path}")

        # Scroll down to see more content
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)

        mid_path = f"/home/samuel/repos/arcforge-branding/referances/images/captured_{index}_mid.png"
        page.screenshot(path=mid_path)
        print(f"✓ Mid-section screenshot saved: {mid_path}")

        return True

    except Exception as e:
        print(f"✗ Error capturing {site['name']}: {e}")
        return False

def main():
    with sync_playwright() as p:
        # Launch browser (headed to see what's happening)
        browser = p.chromium.launch(headless=False)

        # Create context with realistic viewport
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        # Capture each site
        for i, site in enumerate(sites, 1):
            success = capture_site(page, site, i)
            if success:
                print(f"✓ Successfully captured {site['name']}")
            time.sleep(2)  # Pause between sites

        print(f"\n{'='*60}")
        print("All screenshots captured!")
        print(f"{'='*60}\n")

        browser.close()

if __name__ == "__main__":
    main()
