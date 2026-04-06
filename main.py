import asyncio
import random
import csv
import math
import os
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

async def human_mouse_move(page: Page, start_x: int, start_y: int, dest_x: int, dest_y: int):
    """Simulate human-like mouse movement with random noise using Bézier curve"""
    steps = random.randint(15, 30)
    for i in range(steps):
        t = i / steps
        current_x = start_x + (dest_x - start_x) * t + random.uniform(-3, 3)
        current_y = start_y + (dest_y - start_y) * t + random.uniform(-3, 3)
        await page.mouse.move(current_x, current_y)
        await asyncio.sleep(random.uniform(0.01, 0.03))
    await page.mouse.move(dest_x, dest_y)

async def scrape_job_board(browser: Browser, account_id: int, max_pages: int = 10):
    """Scrape job listings from V2EX jobs board"""
    print(f"🤖 [Agent {account_id}] Initializing stealth environment...")
    
    context: BrowserContext = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        locale="zh-CN",
        timezone_id="Asia/Shanghai"
    )
    page: Page = await context.new_page()

    # Inject stealth script to bypass detection
    await page.add_init_script("""
        (() => {
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel(R) Iris(R) Xe Graphics';
                return getParameter.apply(this, arguments);
            };
            window.chrome = {
                app: { isInstalled: false },
                runtime: { OnInstalledReason: { INSTALL: 'install' } },
                loadTimes: () => ({})
            };
            if (navigator.webdriver) {
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            }
        })();
    """)

    scraped_data = []

    try:
        for page_num in range(1, max_pages + 1):
            target_url = f"https://www.v2ex.com/go/jobs?p={page_num}"
            print(f"\n🌐 [Agent {account_id}] Entering page {page_num}: {target_url}")
            
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector('.topic-link', timeout=30000)
            
            print(f"🖱️ [Agent {account_id}] Simulating human browsing on page {page_num}...")
            await human_mouse_move(page, start_x=200, start_y=150, dest_x=500, dest_y=600)
            await page.mouse.wheel(0, random.randint(500, 1000))
            await asyncio.sleep(random.uniform(1.0, 2.0))

            jobs_locator = page.locator('.topic-link')
            count = await jobs_locator.count()
            print(f"🔍 Found {count} jobs, starting keyword filtering...")

            # Filter jobs by target keywords
            target_keywords = ["Python", "实习", "后端", "爬虫", "AI", "大模型", "LLM", "Agent"]

            filtered_count = 0
            for i in range(count):
                title = await jobs_locator.nth(i).inner_text()
                title_lower = title.lower()

                if any(keyword.lower() in title_lower for keyword in target_keywords):
                    href = await jobs_locator.nth(i).get_attribute('href')
                    full_url = f"https://www.v2ex.com{href}"
                    scraped_data.append({'title': title, 'url': full_url})
                    filtered_count += 1
                    print(f"🎯 Target acquired: {title[:25]}...")

            print(f"✅ Page {page_num} extraction complete! Kept {filtered_count} matching jobs.")

            # Cooldown between pages to avoid detection
            if page_num < max_pages:
                cooldown = random.uniform(3.5, 7.5)
                print(f"⏳ Cooldown... Simulating human reading, waiting {cooldown:.1f} seconds")
                await asyncio.sleep(cooldown)

        # Save all collected data to CSV
        filename = f'v2ex_jobs_multi_pages.csv'
        absolute_path = os.path.abspath(filename)

        with open(absolute_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'url'])
            writer.writeheader()
            writer.writerows(scraped_data)

        print(f"\n🎉 Task completed successfully! Scraped {len(scraped_data)} job postings.")
        print(f"📂 Your internship job database is here: {absolute_path}")

    except Exception as e:
        print(f"❌ [Agent {account_id}] Task failed, error: {e}")
    finally:
        await context.close()

async def run():
    """Main entry point with proxy configuration"""
    async with async_playwright() as p:
        try:
            print("🚀 Attempting to launch browser with proxy...")
            browser: Browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                proxy={
                    # Make sure this matches your actual proxy port
                    "server": "http://127.0.0.1:7897",
                    "bypass": "localhost,127.0.0.1"
                },
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--ignore-certificate-errors",
                    "--use-gl=desktop",
                ]
            )
        except Exception as e:
            print(f"❌ Browser launch failed! Check if your proxy is running and port is correct. Error: {e}")
            return

        # Start with 1 agent to avoid overwhelming the target server
        tasks = [
            scrape_job_board(browser, account_id=1),
        ]

        await asyncio.gather(*tasks)

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
