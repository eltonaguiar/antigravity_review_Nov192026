"""TLS/JA3 impersonation test — curl_cffi, no browser.

Anti-bot WAFs fingerprint the TLS handshake and HTTP/2 frame order before serving HTML. curl_cffi
reproduces Chrome's exact handshake in a plain Python client, so a normal script can look like a
real browser at the network layer with no browser overhead.

For each target we report the status AND whether real content came back (status alone lies:
a 403 challenge page and a 200 shell both prove nothing).
"""
import json
import re

from curl_cffi import requests as creq

TARGETS = [
    ("walmart_search", "https://www.walmart.ca/en/search?q=playstation+5", "playstation"),
    ("walmart_api", "https://www.walmart.ca/api/search/products?query=playstation%205&lang=en", None),
    ("staples_search", "https://www.staples.ca/search?query=playstation%205", "playstation"),
    ("memoryexpress", "https://www.memoryexpress.com/Search/Products?Search=playstation+5", "playstation"),
    ("gamestop", "https://www.gamestop.ca/SearchResult/QuickSearch?q=playstation%205", "playstation"),
    ("bestbuy_api", "https://www.bestbuy.ca/ecomm-api/availability/products?accept-language=en-CA&postalCode=M5G&skus=19422130&quantities=1", "availabilities"),
    ("amazon_ca", "https://www.amazon.ca/s?k=playstation+5", "playstation"),
]

rows = []
for name, url, needle in TARGETS:
    row = {"target": name, "url": url}
    for imp in ("chrome", "chrome124", "safari"):
        try:
            r = creq.get(url, impersonate=imp, timeout=35,
                         headers={"Accept-Language": "en-CA,en;q=0.9"})
            body = r.text or ""
            low = body.lower()
            blocked = any(k in low[:4000] for k in
                          ("just a moment", "access denied", "perimeterx", "px-captcha",
                           "attention required", "forbidden"))
            content = (needle.lower() in low) if needle else (len(body) > 100)
            prices = len(re.findall(r"\$\s?\d", body))
            row[imp] = {"status": r.status_code, "bytes": len(body),
                        "blocked_marker": blocked, "has_content": content, "price_tokens": prices}
            if r.status_code == 200 and content and not blocked:
                break
        except Exception as e:
            row[imp] = {"error": f"{type(e).__name__}: {e}"[:110]}
    rows.append(row)

print(f"{'target':16} {'imp':10} {'HTTP':>5} {'bytes':>9} {'blocked':>8} {'content':>8} {'prices':>7}")
print("-" * 72)
for row in rows:
    for imp in ("chrome", "chrome124", "safari"):
        v = row.get(imp)
        if not v or "error" in v:
            if v:
                print(f"{row['target']:16} {imp:10} {'ERR':>5}  {v['error'][:40]}")
            continue
        print(f"{row['target']:16} {imp:10} {v['status']:>5} {v['bytes']:>9} "
              f"{str(v['blocked_marker']):>8} {str(v['has_content']):>8} {v['price_tokens']:>7}")

json.dump(rows, open("curl_cffi_results.json", "w"), indent=1)
print("\nsaved -> curl_cffi_results.json")
