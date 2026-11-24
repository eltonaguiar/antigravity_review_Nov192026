"""nodriver stealth scraper — real Chrome over CDP, no --enable-automation, no webdriver flag.

nodriver is the successor to undetected-chromedriver: it speaks CDP directly, so there is no
navigator.webdriver tell and no chromedriver binary for a WAF to fingerprint. Paced deliberately
(one page every few seconds) because the whole point is to stay invisible on a residential IP.

Usage: python nd_scrape.py <url> [wait_seconds]
"""
import asyncio
import json
import os
import re
import sys

import nodriver as uc

URL = sys.argv[1]
WAIT = int(sys.argv[2]) if len(sys.argv) > 2 else 18

JS = r"""
JSON.stringify((() => {
  const clean = s => (s || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  const out = {title: document.title, url: location.href, items: [], nextData: false,
               priceTexts: [], bodyLen: 0, head: ''};
  const body = clean(document.body.innerText);
  out.bodyLen = body.length;
  out.head = body.slice(0, 320);
  out.nextData = !!document.getElementById('__NEXT_DATA__');

  const seen = new Set();
  document.querySelectorAll('a[href]').forEach(a => {
    const t = clean(a.innerText);
    if (!t || t.length < 12 || t.length > 320) return;
    if (!/\$\s?\d/.test(t)) return;
    const k = t.slice(0, 80);
    if (seen.has(k)) return;
    seen.add(k);
    out.items.push({text: t.slice(0, 240), href: (a.href || '').slice(0, 200)});
  });
  out.priceTexts = (body.match(/\$\s?\d[\d,]*(\.\d{2})?/g) || []).slice(0, 30);
  return out;
})())
"""


async def main():
    browser = await uc.start(headless=False, browser_args=[
        "--disable-blink-features=AutomationControlled",
        "--window-size=1440,950",
    ])
    page = await browser.get(URL)

    # let any Cloudflare/PerimeterX interstitial resolve, then require stable real content
    deadline = asyncio.get_event_loop().time() + max(WAIT, 25)
    last, stable = 0, 0
    while asyncio.get_event_loop().time() < deadline:
        await page.sleep(2)
        try:
            probe = await page.evaluate(
                "JSON.stringify((() => ({t: document.title, n: document.body.innerText.length,"
                " x: document.body.innerText.slice(0,90).toLowerCase()}))())")
            probe = json.loads(probe) if isinstance(probe, str) else (probe or {})
            if not isinstance(probe, dict):
                probe = {"t": "", "n": 0, "x": ""}
        except Exception:
            continue
        t = (probe.get("t") or "").lower()
        x = probe.get("x") or ""
        challenging = ("just a moment" in t or "security verification" in x
                       or "performing security" in x or "verifying you are human" in x
                       or "attention required" in t)
        n = probe.get("n") or 0
        if not challenging and n > 2500:
            stable = stable + 1 if abs(n - last) < 60 else 0
            last = n
            if stable >= 2:
                break

    try:
        raw = await page.evaluate(JS)
        data = json.loads(raw) if isinstance(raw, str) else (raw or {"error": "evaluate returned None"})
    except Exception as e:
        data = {"error": f"{type(e).__name__}: {e}"[:200]}

    slug = re.sub(r"[^a-z0-9]+", "_", URL.lower())[:60]
    outpath = os.path.join(os.environ.get("TMPDIR", "."), f"nd_{slug}.json")
    json.dump({"url": URL, "data": data}, open(outpath, "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)

    d = data if isinstance(data, dict) else {}
    print(f"title={d.get('title')!r} body_len={d.get('bodyLen')} items={len(d.get('items') or [])} next={d.get('nextData')}")
    print("head:", (d.get("head") or "")[:170])
    for it in (d.get("items") or [])[:8]:
        print("  ITEM:", it["text"][:140])
    print("saved ->", outpath)
    browser.stop()


asyncio.run(main())
