"""patchright test — undetected Playwright fork that patches the CDP Runtime.enable leak.

Patchright keeps Playwright's API but removes the automation tells WAFs probe for. If any tool
gets past Memory Express's Cloudflare interstitial, it should be this one.
"""
import json
import os
import re
import time

from patchright.sync_api import sync_playwright

URL = "https://www.memoryexpress.com/Search/Products?Search=playstation+5"

JS = r"""JSON.stringify((() => {
  const clean = s => (s || '').replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();
  const body = clean(document.body.innerText);
  const out = {title: document.title, bodyLen: body.length, head: body.slice(0,300), items: []};
  const seen = new Set();
  document.querySelectorAll('a[href]').forEach(a => {
    const t = clean(a.innerText);
    if (!t || t.length < 12 || t.length > 300) return;
    if (!/\$\s?\d/.test(t)) return;
    const k = t.slice(0,80);
    if (seen.has(k)) return;
    seen.add(k);
    out.items.push({text: t.slice(0,220), href: (a.href||'').slice(0,180)});
  });
  return out;
})())"""

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=os.path.join(os.environ["LOCALAPPDATA"], "hermes", "cache", "scratch", "pr_profile"),
        channel="chrome", headless=False, no_viewport=True,
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    resp = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    print("status:", resp.status if resp else None)

    deadline = time.time() + 45
    last, stable = 0, 0
    while time.time() < deadline:
        time.sleep(2)
        try:
            probe = json.loads(page.evaluate(
                "JSON.stringify((() => ({t: document.title, n: document.body.innerText.length,"
                " x: document.body.innerText.slice(0,90).toLowerCase()}))())"))
        except Exception:
            continue
        t = (probe.get("t") or "").lower()
        x = probe.get("x") or ""
        challenging = ("just a moment" in t or "security verification" in x
                       or "performing security" in x or "verifying you are human" in x)
        n = probe.get("n") or 0
        if not challenging and n > 2500:
            stable = stable + 1 if abs(n - last) < 60 else 0
            last = n
            if stable >= 2:
                break

    data = json.loads(page.evaluate(JS))
    ctx.close()

print(f"title={data['title']!r} bodyLen={data['bodyLen']} items={len(data['items'])}")
print("head:", data["head"][:180])
for it in data["items"][:10]:
    print("  ITEM:", it["text"][:140])
json.dump(data, open("patchright_memexpress.json", "w"), indent=1, ensure_ascii=False)
print("saved -> patchright_memexpress.json")
