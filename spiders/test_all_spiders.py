"""全量爬虫验证 — Scrapling 引擎兼容性测试 v2"""
import sys, os
if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, r"C:\Users\FOUR\Desktop\爬虫工具\ai-dev-hub\spiders")
import asyncio, time, traceback

SPIDER_TIMEOUT = 90  # 每个爬虫超时秒数
RESULTS = {}

def fmt(status, name, items, elapsed, err=""):
    icons = {"PASS":"[PASS]", "WARN":"[WARN]", "FAIL":"[FAIL]"}
    return f"  {icons[status]} {name}: items={items} time={elapsed:.1f}s{err}"

async def test_spider(name, module_path, spider_class_name):
    print(f"\n===== [{name}] =====\n", flush=True)
    start = time.time()
    try:
        import importlib
        mod = importlib.import_module(module_path)
        SpiderClass = getattr(mod, spider_class_name)
        spider = SpiderClass()

        result = await asyncio.wait_for(spider.run(), timeout=SPIDER_TIMEOUT)
        elapsed = time.time() - start

        items = getattr(result, 'items_count', 0)
        saved = getattr(result, 'saved_count', 0)
        errors = getattr(result, 'error_count', 0)

        if items > 0:
            RESULTS[name] = {"status":"PASS", "items":items, "time":f"{elapsed:.1f}s", "saved":saved, "error":None}
            print(fmt("PASS", name, items, elapsed))
        elif errors == 0:
            RESULTS[name] = {"status":"WARN", "items":0, "time":f"{elapsed:.1f}s", "saved":0, "error":"空结果"}
            print(fmt("WARN", name, 0, elapsed, " - 空结果"))
        else:
            RESULTS[name] = {"status":"FAIL", "items":0, "time":f"{elapsed:.1f}s", "saved":0, "error":f"{errors} errors"}
            print(fmt("FAIL", name, 0, elapsed, f" - {errors} errors"))
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        RESULTS[name] = {"status":"FAIL", "items":0, "time":f"{elapsed:.1f}s", "saved":0, "error":"超时"}
        print(fmt("FAIL", name, 0, elapsed, " - 超时"))
    except Exception as e:
        elapsed = time.time() - start
        RESULTS[name] = {"status":"FAIL", "items":0, "time":f"{elapsed:.1f}s", "saved":0, "error":str(e)[:150]}
        print(fmt("FAIL", name, 0, elapsed, f" - {str(e)[:80]}"))

async def main():
    spiders = [
        ("github_trending", "spiders.github.trending",  "GitHubTrendingSpider"),
        ("v2ex",            "spiders.forums.v2ex",       "V2EXSpider"),
        ("kaggle",          "spiders.competitions.kaggle","KaggleSpider"),
        ("juejin",          "spiders.forums.juejin",     "JuejinSpider"),
        ("hackernews",      "spiders.hackernews.hot",    "HackerNewsSpider"),
        ("openai",          "spiders.developer_programs.openai","OpenAISpider"),
    ]
    SKIP = ["tianchi"]  # 含Playwright, 待替换后测试

    for name, mod, cls in spiders:
        await test_spider(name, mod, cls)
        await asyncio.sleep(1)

    # 汇总
    print("\n\n" + "="*50)
    print("  全量爬虫验证报告 (Scrapling)")
    print("="*50)
    passed = sum(1 for r in RESULTS.values() if r["status"] == "PASS")
    warned = sum(1 for r in RESULTS.values() if r["status"] == "WARN")
    failed = sum(1 for r in RESULTS.values() if r["status"] == "FAIL")
    print(f"  总计: {len(RESULTS)} | PASS: {passed} | WARN: {warned} | FAIL: {failed}")
    print()
    for name, r in RESULTS.items():
        icon = {"PASS":"[OK]", "WARN":"[~]", "FAIL":"[X]"}[r["status"]]
        err = f" - {r['error']}" if r["error"] else ""
        print(f"  {icon} {name}: {r['items']}条, {r['time']}{err}")
    for s in SKIP:
        print(f"  [-] {s}: 跳过")
    print("="*50)

asyncio.run(main())
