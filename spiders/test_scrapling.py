"""端到端验证: Scrapling 引擎替换 + 回退机制"""
import sys
sys.path.insert(0, '.')
import asyncio

from spiders.config import settings
from spiders.base import _SCRAPLING_AVAILABLE, _SCRAPLING_STEALTHY_FETCHER
from spiders.github.trending import GitHubTrendingSpider

async def test_scrapling_engine():
    spider = GitHubTrendingSpider()
    
    # === Test 1: Scrapling fetch basic ===
    print("=== Test 1: Scrapling fetch basic ===")
    response = await spider.fetch("https://httpbin.org/html")
    assert response is not None, "fetch returned None"
    assert response.status_code == 200, f"status: {response.status_code}"
    assert len(response.text) > 100, f"content too short: {len(response.text)}"
    print(f"  Status: {response.status_code}")
    print(f"  Content: {len(response.text)} bytes")
    print(f"  Has _scrapling_raw: {hasattr(response, '_scrapling_raw')}")
    print("  PASS")
    
    # === Test 2: parse_html (BS4 backward compat) ===
    print("\n=== Test 2: BS4 parse_html ===")
    soup = spider.parse_html(response.text)
    html = soup.select_one("html")
    assert html is not None, "BS4 couldn't find html"
    body_text = soup.get_text(strip=True)
    assert len(body_text) > 0, "BS4 extracted empty text"
    print(f"  Got HTML via BS4: {len(body_text)} chars")
    print("  PASS")
    
    # === Test 3: parse_scrapling (Selectors) ===
    print("\n=== Test 3: Scrapling parse_scrapling ===")
    ss = spider.parse_scrapling(response.text)
    body_el = ss.css("body")
    assert len(body_el) > 0, "Selector couldn't find body"
    text = ss.get_all_text(separator="\n", strip=True)
    assert len(text) > 0, "Selector extracted empty text"
    print(f"  Got HTML via Scrapling: {len(text)} chars")
    print("  PASS")
    
    # === Test 4: get_text compatibility ===
    print("\n=== Test 4: get_text compatibility ===")
    bs4_text = spider.get_text(soup)
    sel_text = spider.get_text(ss)
    assert len(bs4_text) > 0, "get_text BS4 failed"
    assert len(sel_text) > 0, "get_text Selector failed"
    print(f"  BS4 text: {len(bs4_text)} chars")
    print(f"  Selector text: {len(sel_text)} chars")
    print("  PASS")
    
    # === Test 5: httpx fallback ===
    print("\n=== Test 5: httpx fallback ===")
    # Force httpx by using use_scrapling=False
    resp_httpx = await spider.fetch("https://httpbin.org/html", use_scrapling=False)
    assert resp_httpx is not None, "httpx fetch returned None"
    assert resp_httpx.status_code == 200
    assert not hasattr(resp_httpx, '_scrapling_raw'), "httpx response should not have _scrapling_raw"
    print(f"  Status: {resp_httpx.status_code}, Content: {len(resp_httpx.text)} bytes")
    print("  PASS")
    
    # === Test 6: Scrapling list_available ===
    print("\n=== Test 6: Scrapling status ===")
    print(f"  Scrapling available: {_SCRAPLING_AVAILABLE}")
    print(f"  ENHANCE_SCRAPLING: {settings.ENABLE_SCRAPLING}")
    print("  PASS")
    
    print("\n" + "=" * 40)
    print("ALL TESTS PASSED")
    return True

asyncio.run(test_scrapling_engine())
