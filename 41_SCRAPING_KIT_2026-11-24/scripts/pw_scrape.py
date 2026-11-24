"""Headful real-Chrome scraper. Drives installed Chrome (channel='chrome') with a persistent
profile so Akamai/PerimeterX see a genuine browser fingerprint on this machine's own IP.

Usage: python pw_scrape.py <url> [--wait 9000]
Writes JSON to $TMPDIR/pw_<slug>.json and prints a compact summary.
"""
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1]
WAIT = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
PROFILE = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "cache", "scratch", "pw_profile")

EXTRACT_JS = r"""
() => {
  const out = {title: document.title, url: location.href, nextData: null, items: [], priceTexts: []};

  // 1) Next.js payload (Walmart CA, many retail sites)
  const nd = document.getElementById('__NEXT_DATA__');
  if (nd) {
    try {
      const j = JSON.parse(nd.textContent);
      out.nextData = j;
    } catch (e) { out.nextDataErr = String(e).slice(0, 120); }
  }

  // 2) JSON-LD products
  out.ld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
    try {
      const j = JSON.parse(s.textContent);
      const arr = Array.isArray(j) ? j : [j];
      arr.forEach(x => { if (x && (x['@type'] === 'Product' || x['@type'] === 'ItemList')) out.ld.push(x); });
    } catch (e) {}
  });

  // 3) Generic card harvest: any anchor with a $ price in its subtree
  const seen = new Set();
  document.querySelectorAll('a[href]').forEach(a => {
    const t = (a.innerText || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
    if (!t || t.length < 12 || t.length > 300) return;
    if (!/\$\s?\d/.test(t)) return;
    const key = t.slice(0, 90);
    if (seen.has(key)) return;
    seen.add(key);
    out.items.push({text: t.slice(0, 260), href: a.href.slice(0, 220)});
  });

  // 4) Every visible price token, for a sanity check
  const bodyText = document.body.innerText.replace(/\u00a0/g, ' ');
  out.priceTexts = (bodyText.match(/\$\s?\d[\d,]*(\.\d{2})?/g) || []).slice(0, 40);
  out.bodyLen = bodyText.length;
  out.head = bodyText.slice(0, 300);
  return out;
}
"""

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE,
        channel="chrome",
        headless=False,
        viewport={"width": 1440, "height": 950},
        args=["--disable-blink-features=AutomationControlled"],
        ignore_default_args=["--enable-automation"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    resp = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    status = resp.status if resp else None
    # challenge-aware wait: let Cloudflare/Akamai interstitials clear, then wait for real content
    deadline = time.time() + max(WAIT / 1000.0, 30)
    last_len, stable = 0, 0
    while time.time() < deadline:
        time.sleep(1.5)
        try:
            probe = page.evaluate("() => ({t: document.title, n: document.body.innerText.length, x: document.body.innerText.slice(0,80)})")
        except Exception:
            continue
        txt = (probe.get("x") or "").lower()
        challenging = ("just a moment" in (probe.get("t") or "").lower()
                       or "security verification" in txt or "performing security" in txt
                       or "verifying you are human" in txt)
        n = probe.get("n") or 0
        if not challenging and n > 3000:
            if abs(n - last_len) < 50:
                stable += 1
                if stable >= 2:
                    break
            else:
                stable = 0
            last_len = n
    time.sleep(1.0)

    data = page.evaluate(EXTRACT_JS)

    # pull products out of __NEXT_DATA__ if present
    prods = []
    nd = data.get("nextData")
    if nd:
        def walk(node, depth=0):
            if depth > 12 or len(prods) > 60:
                return
            if isinstance(node, dict):
                name = node.get("name") or node.get("productName") or node.get("title")
                price = node.get("price") or node.get("currentPrice") or node.get("salePrice")
                if isinstance(name, str) and price not in (None, "", {}) and len(name) < 220:
                    prods.append({"name": name, "price": price,
                                  "seller": node.get("sellerName") or node.get("seller"),
                                  "avail": node.get("availabilityStatus") or node.get("availability")})
                for v in node.values():
                    walk(v, depth + 1)
            elif isinstance(node, list):
                for v in node[:120]:
                    walk(v, depth + 1)
        walk(nd)

    slug = re.sub(r"[^a-z0-9]+", "_", URL.lower())[:60]
    outpath = os.path.join(os.environ.get("TMPDIR", "."), f"pw_{slug}.json")
    payload = {"url": URL, "final_url": data.get("url"), "status": status,
               "title": data.get("title"), "body_len": data.get("bodyLen"),
               "head": data.get("head"), "next_data_products": prods[:40],
               "card_items": data.get("items", [])[:40],
               "ld_blocks": len(data.get("ld", [])), "price_texts": data.get("priceTexts", [])}
    json.dump(payload, open(outpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ctx.close()

print(f"status={status} title={payload['title']!r} body_len={payload['body_len']}")
print(f"next_data_products={len(prods)}  card_items={len(payload['card_items'])}  ld={payload['ld_blocks']}")
print("head:", (payload["head"] or "")[:160].replace("\n", " "))
for pr in prods[:6]:
    print("  ND:", json.dumps(pr, ensure_ascii=False)[:150])
for it in payload["card_items"][:6]:
    print("  CARD:", it["text"][:130])
print("saved ->", outpath)
