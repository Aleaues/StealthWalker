import asyncio
import random
import csv
import math
import os
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# [保留上一版的拟人化插件]
async def human_mouse_move(page: Page, start_x: int, start_y: int, dest_x: int, dest_y: int):
    steps = random.randint(15, 30)
    for i in range(steps):
        t = i / steps
        current_x = start_x + (dest_x - start_x) * t + random.uniform(-3, 3)
        current_y = start_y + (dest_y - start_y) * t + random.uniform(-3, 3)
        await page.mouse.move(current_x, current_y)
        await asyncio.sleep(random.uniform(0.01, 0.03))
    await page.mouse.move(dest_x, dest_y)

# [核心升级：针对 V2EX 真实网站的岗位嗅探逻辑]
# [代码升级部分开始：增加 max_pages 参数控制爬取深度]
# ==========================================
# max_pages=3: [参数升级] 作用：设置默认爬取前 3 页。你可以随时在调用时修改这个数字。
async def scrape_job_board(browser: Browser, account_id: int, max_pages: int = 10):
    print(f"🤖 [特工 {account_id} 号] 正在初始化伪装环境...")
    
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

    # 把数据口袋放在外面，准备装载所有页面的战利品
    scraped_data = [] 

    try:
        # range(1, max_pages + 1): [新函数用法] 作用：生成从 1 开始，到 max_pages 结束的数字序列。
        # 如果 max_pages 是 3，它就会依次产出 1, 2, 3。
        for page_num in range(1, max_pages + 1):
            
            # f"...{page_num}": 动态拼接 URL，这叫“字符串格式化”。
            target_url = f"https://www.v2ex.com/go/jobs?p={page_num}"
            print(f"\\n🌐 [特工 {account_id} 号] 潜入第 {page_num} 页: {target_url}")
            
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector('.topic-link', timeout=30000)
            
            print(f"🖱️ [特工 {account_id} 号] 假装浏览第 {page_num} 页...")
            await human_mouse_move(page, start_x=200, start_y=150, dest_x=500, dest_y=600)
            await page.mouse.wheel(0, random.randint(500, 1000)) # 随机滚动距离，更像真人
            await asyncio.sleep(random.uniform(1.0, 2.0))

            jobs_locator = page.locator('.topic-link')
            count = await jobs_locator.count()
            print(f"🔍 发现 {count} 个岗位，开始执行关键词过滤...")
        
        # ==========================================
        # [代码升级部分开始：增加关键词筛选器]
        # ==========================================
        # 你可以在这里定义你感兴趣的关键词列表
            target_keywords = ["Python", "实习", "后端", "爬虫", "AI", "大模型", "LLM", "Agent"]
        
            filtered_count = 0 # 记录成功匹配了多少个
        
            for i in range(count):
                title = await jobs_locator.nth(i).inner_text()
            
            # 统一转成小写再比较，防止漏掉 "python" 或 "PYTHON" 这种大小写混写的情况
                title_lower = title.lower()
            
            # any(): [新函数] 作用：这是 Python 里非常高级且优雅的用法。
            # 只要后面的列表推导式中有一个为 True（即只要有一个关键词出现在标题里），any() 就会返回 True。
                if any(keyword.lower() in title_lower for keyword in target_keywords):
                
                    href = await jobs_locator.nth(i).get_attribute('href')
                    full_url = f"https://www.v2ex.com{href}"
                
                    scraped_data.append({'title': title, 'url': full_url})
                    filtered_count += 1
                    print(f"🎯 命中目标: {title[:25]}...") 
        
            print(f"✅ 第 {page_num} 页提取完成！经过筛选，保留了 {filtered_count} 个对口岗位。")

            # [核心防封锁逻辑] 如果当前不是最后一页，就强制休息一段时间再翻页
            if page_num < max_pages:
                cooldown = random.uniform(3.5, 7.5) # 随机休息 3.5 到 7.5 秒
                print(f"⏳ 翻页冷却中... 模拟人类阅读，停留 {cooldown:.1f} 秒")
                await asyncio.sleep(cooldown)

        # ==========================================
        # [代码升级部分结束]
        # ==========================================
        
        # 所有页面爬取完毕，一次性保存到文件
        filename = f'v2ex_jobs_multi_pages.csv'
        absolute_path = os.path.abspath(filename) 
        
        with open(absolute_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'url'])
            writer.writeheader()
            writer.writerows(scraped_data)
            
        print(f"\\n🎉 任务圆满完成！共抓取了 {len(scraped_data)} 条岗位信息！")
        print(f"📂 你的超级实习岗位库在这里：{absolute_path}")

    except Exception as e:
        print(f"❌ [特工 {account_id} 号] 任务失败，报错: {e}")
    finally:
        await context.close()
async def run():
    # ==========================================
        # [代码升级部分开始：挂载网络代理 (Proxy)]
        # ==========================================
        # proxy: [新参数] 作用：告诉 Playwright 启动的这个独立浏览器，所有网络请求都要走下面指定的代理通道。
        # 为什么必须加？因为 Playwright 启动的 Chrome 是一个纯净的沙盒环境，默认【不会】继承你电脑系统自带的 VPN 代理设置。
    async with async_playwright() as p:
        try:
            print("🚀 正在尝试挂载代理启动浏览器...")
            # ==========================================
            # [代码升级部分开始：更健壮的代理启动模块]
            # ==========================================
            browser: Browser = await p.chromium.launch(
                headless=False, 
                channel="chrome", 
                proxy={
                    # 请务必确保这里的端口是你真实的代理端口！
                    "server": "http://127.0.0.1:7897", 
                    
                    # bypass: [参数升级] 作用：告诉浏览器，如果是访问本机的地址，就不要走代理。
                    # 为什么要加？有时候代理软件的本地路由没配好，会导致 Chrome 刚启动连自己都找不到，直接闪退。加上它更稳！
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
            # ==========================================
            # [代码升级部分结束]
            # ==========================================
        except Exception as e:
            # 如果启动失败，不再抛出长串红字，而是给出人类能看懂的提示
            print(f"❌ 浏览器启动失败！请检查你的代理软件是否打开，且端口号是否正确。底层报错原因: {e}")
            return # 直接退出程序，不往下执行了
        
        # 为了不给真实网站服务器造成瞬间巨大压力（这也是做爬虫的道德修养），
        # 这次我们先派 1 个特工去探路。你可以把这里改成循环来测试多账号。
        tasks = [
            scrape_job_board(browser, account_id=1),
        ]

        await asyncio.gather(*tasks)

        await asyncio.sleep(2) 
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())