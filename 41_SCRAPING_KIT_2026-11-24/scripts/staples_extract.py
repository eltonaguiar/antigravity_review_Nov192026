"""Extract real PS5 listings from the Staples search page fetched via TLS impersonation."""
import json
import re

from bs4 import BeautifulSoup
from curl_cffi import requests as creq

r = creq.get("https://www.staples.ca/search?query=playstation%205", impersonate="chrome", timeout=35,
             headers={"Accept-Language": "en-CA,en;q=0.9"})
print("HTTP", r.status_code, len(r.text), "bytes")

soup = BeautifulSoup(r.text, "lxml")

ld = []
for s in soup.find_all("script", type="application/ld+json"):
    try:
        j = json.loads(s.string or "")
    except Exception:
        continue
    ld.extend(j if isinstance(j, list) else [j])

prods = []


def walk(node, d=0):
    if d > 8 or len(prods) > 60:
        return
    if isinstance(node, dict):
        if node.get("@type") == "Product":
            off = node.get("offers") or {}
            if isinstance(off, list):
                off = off[0] if off else {}
            prods.append({"name": (node.get("name") or "")[:110],
                          "price": off.get("price") or node.get("price"),
                          "currency": off.get("priceCurrency"),
                          "avail": str(off.get("availability") or "").split("/")[-1],
                          "sku": node.get("sku") or node.get("productID")})
        for v in node.values():
            walk(v, d + 1)
    elif isinstance(node, list):
        for v in node[:200]:
            walk(v, d + 1)


walk(ld)

if not prods:
    for a in soup.select("a[href]"):
        t = " ".join(a.get_text(" ", strip=True).split())
        if len(t) < 15 or len(t) > 300:
            continue
        m = re.search(r"\$\s?([\d,]+\.\d{2})", t)
        if not m:
            continue
        prods.append({"name": t[:110], "price": m.group(1), "href": (a.get("href") or "")[:90]})

seen, uniq = set(), []
for p in prods:
    k = (str(p.get("name", ""))[:60], str(p.get("price")))
    if k in seen:
        continue
    seen.add(k)
    uniq.append(p)

print(f"products extracted: {len(uniq)}\n")
for p in uniq[:20]:
    print(f"  ${str(p.get('price')):>9}  {str(p.get('avail',''))[:12]:12} {str(p.get('name',''))[:74]}")
json.dump(uniq, open("staples_ps5.json", "w"), indent=1)
print("\nsaved -> staples_ps5.json")
