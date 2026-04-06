# StealthWalker (潜行者)

> **A high-concurrency, anti-detect browser automation framework based on Playwright and Asyncio.**
>
> 基于 Playwright 和 Asyncio 构建的高并发、抗检测浏览器自动化特工框架。专为绕过复杂网络风控（如 Cloudflare）、提供高质量 LLM/Agent 外部数据源而设计。

---

## 目录 (Table of Contents)
- [核心特性 (Features)](#核心特性-features)
- [技术栈 (Tech Stack)](#技术栈-tech-stack)
- [快速开始 (Quick Start)](#快速开始-quick-start)
- [使用示例 (Usage)](#使用示例-usage)
- [免责声明 (Disclaimer)](#免责声明-disclaimer)

---

## 核心特性 (Features)

* **深度指纹隐匿 (Deep Stealth):** 底层重写 WebGL 渲染器信息、硬件并发数及 Navigator 属性，抹除 WebDriver 痕迹，轻松绕过高阶机器人检测。
* **拟人化交互 (Human-like Interaction):** 内置基于贝塞尔曲线的随机鼠标移动轨迹算法与自然滚动停顿，完美模拟真实人类操作。
* **异步高并发 (Async Concurrency):** 抛弃传统阻塞式爬虫，采用 `asyncio` 驱动多账号/多上下文同时并行任务，单节点稳定并发处理 `[填写你的真实并发数]` 个任务流。
* **插件化架构 (Pluggable):** 业务逻辑与底层反侦察环境高度解耦，易于扩展为各种垂直场景（如招聘数据嗅探、电商竞品监控等）的定制化 Agent。

## 技术栈 (Tech Stack)

* **核心语言:** Python 3.9+
* **自动化引擎:** Playwright (Async API)
* **并发框架:** Asyncio
* **数据持久化:** CSV / SQLite

## 快速开始 (Quick Start)

### 1. 克隆仓库
```bash
git clone https://github.com/Aleaues/StealthWalker.git
cd StealthWalker
```

### 2. 配置虚拟环境与依赖
推荐使用虚拟环境以保持系统纯净：

```bash
python -m venv venv
# Windows 激活
.\venv\Scripts\activate
# Mac/Linux 激活
source venv/bin/activate

# 安装核心依赖
pip install playwright
# 安装 Chromium 内核及系统依赖
playwright install chromium
```

## 使用示例 (Usage)

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # 挂载代理并加载防检测参数启动浏览器
        browser = await p.chromium.launch(
            headless=False,
            proxy={"server": "http://127.0.0.1:7890", "bypass": "localhost,127.0.0.1"},
            args=["--disable-blink-features=AutomationControlled"]
        )

        # 并发执行特工任务
        await asyncio.gather(
            scrape_job_board(browser, account_id=1, max_pages=3)
        )
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

提示: 运行结束后，结构化数据将自动保存在项目根目录的 CSV 文件中。

## 免责声明 (Disclaimer)

本项目仅供 Python 自动化技术学习与研究使用。请严格遵守目标网站的 robots.txt 协议与相关法律法规。开发者对使用该工具造成的任何滥用行为或业务损失不承担任何责任。请合理控制请求频率，做一名有道德底线的爬虫工程师。
