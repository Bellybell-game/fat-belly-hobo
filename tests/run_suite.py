#!/usr/bin/env python3
"""
Fat Belly Hobo - Deterministic External Test Suite
====================================================
Tests run OUTSIDE the product. No game code is modified for testing.

Design principles (per user):
- Product is never modified to accommodate tests
- All tests are deterministic: same setup -> same expected outcome
- Interactions are tested, not just screenshots
- Uses the existing ?test=1 API for deterministic control (no RNG dependence)

Usage:
    python3 run_suite.py [--filter <name>] [--report]
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

SUITE_DIR = Path(__file__).parent
RESULTS_DIR = SUITE_DIR / "results"
BASE_URL = "http://127.0.0.1:8901/index.html"

class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.details = []
        self.screenshots = []
        self.error = None
        self.duration_ms = 0

    def log(self, msg):
        self.details.append(msg)
        print(f"    {msg}")

    def to_dict(self):
        return {
            "name": self.name,
            "passed": self.passed,
            "details": self.details,
            "screenshots": self.screenshots,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }

class GameDriver:
    """Deterministic driver for the game via ?test=1 API and UI interactions."""
    
    def __init__(self, page, result):
        self.page = page
        self.result = result
    
    async def load_test_mode(self):
        """Load game in test mode for deterministic control."""
        await self.page.goto(f"{BASE_URL}?test=1", wait_until="networkidle")
        await self.page.wait_for_timeout(2500)
    
    async def load_normal(self):
        """Load game in normal mode."""
        await self.page.goto(BASE_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(2500)
    
    async def screenshot(self, name):
        path = str(RESULTS_DIR / f"{self.result.name}-{name}.png")
        await self.page.screenshot(path=path)
        self.result.screenshots.append(path)
        return path
    
    async def test_api(self, expr):
        """Evaluate expression against the test API. Returns the result."""
        return await self.page.evaluate(f"""() => {{
            if (typeof window.FatBellyTest === 'undefined') return {{error: 'no test API'}};
            try {{ return window.FatBellyTest.{expr}; }}
            catch(e) {{ return {{error: e.message}}; }}
        }}""")
    
    async def click_brawl(self):
        """Click LET'S BRAWL button deterministically."""
        # Button is centered around (640, 554) at 1280x720
        await self.page.mouse.click(640, 554)
        await self.page.wait_for_timeout(3000)
    
    async def press_key(self, key):
        """Press a keyboard key."""
        await self.page.keyboard.press(key)
        await self.page.wait_for_timeout(500)
    
    async def get_game_state(self):
        """Get deterministic game state via test API."""
        return await self.test_api("getState()")

# Import test cases
from test_cases import TEST_CASES

async def run_one(pw, test_fn, name):
    result = TestResult(name)
    start = time.time()
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    try:
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        driver = GameDriver(page, result)
        await test_fn(driver, result)
        result.passed = True
    except AssertionError as e:
        result.error = f"ASSERT: {e}"
        result.log(f"FAILED: {e}")
    except Exception as e:
        result.error = f"ERROR: {e}"
        result.log(f"ERROR: {e}")
    finally:
        result.duration_ms = int((time.time() - start) * 1000)
        await browser.close()
    return result

async def main():
    filter_name = None
    if "--filter" in sys.argv:
        filter_name = sys.argv[sys.argv.index("--filter") + 1]
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    selected = [(n, f) for n, f in TEST_CASES if not filter_name or filter_name in n]
    print(f"Running {len(selected)} test(s)...")
    
    results = []
    async with async_playwright() as pw:
        for name, fn in selected:
            print(f"\n[TEST] {name}")
            r = await run_one(pw, fn, name)
            results.append(r)
            status = "PASS" if r.passed else "FAIL"
            print(f"  -> {status} ({r.duration_ms}ms)")
    
    # Write report
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "tests": [r.to_dict() for r in results],
    }
    report_path = RESULTS_DIR / "report.json"
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {report['passed']}/{report['total']} passed")
    print(f"Report: {report_path}")
    for r in results:
        if not r.passed:
            print(f"  FAILED: {r.name} - {r.error}")
    
    sys.exit(0 if report["failed"] == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
