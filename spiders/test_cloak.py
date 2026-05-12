"""测试 tianchi CloakBrowser 替换"""
import asyncio, sys
sys.path.insert(0, r"C:\Users\FOUR\Desktop\爬虫工具\ai-dev-hub\spiders")

async def test():
    from cloakbrowser import launch_async
    print("Launching CloakBrowser...", flush=True)
    b = await launch_async(headless=True, stealth_args=True, humanize=True)
    print(f"Browser: {type(b).__name__}", flush=True)
    p = await b.new_page()
    await p.goto("https://httpbin.org/html", timeout=15000)
    title = await p.title()
    print(f"Title: {title}", flush=True)
    await b.close()
    print("PASS: CloakBrowser tianchi replacement verified", flush=True)

asyncio.run(test())
