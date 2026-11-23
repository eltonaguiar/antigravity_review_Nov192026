"""Does supplying a live quote fix the 'price recall failure'? The arm I never ran.

F1 claimed AI entrants fail at recalling prices, measured by brackets that were already void at the fill.
The criticism that landed: I never tested the arm WHERE THE PRICE IS SUPPLIED. If voids collapse when the
quote is in the prompt, F1 is a harness finding, not a model finding.

Design: same contest prompt, same models, two arms.
  ARM A (bare)      - "use realistic price levels near the current market"   <- the original prompt
  ARM B (stamped)   - identical, plus CURRENT QUOTES with a timestamp
Score both against the same quote set with the same bracket rule. Report void counts per arm.

Models: local vLLM (free, GPU) and the free Ollama cloud model. No paid API.
"""
import json, re, ssl, urllib.request, datetime, math

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/157.0.0.0 Safari/537.36"}

SYMS = {"SPY": "SPY", "BTCUSD": "BTCUSDT", "EURUSD": "EURUSD=X", "GLD": "GLD", "TLT": "TLT", "AAPL": "AAPL"}


def quote(sym):
    if sym == "BTCUSD":
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", headers=UA), timeout=20, context=CTX).read())
        return float(r["price"])
    u = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=5d&interval=1d" % SYMS[sym]
    j = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25, context=CTX)
                   .read().decode("utf-8", "replace"))
    return float(j["chart"]["result"][0]["meta"]["regularMarketPrice"])


Q = {}
for s in SYMS:
    try:
        Q[s] = quote(s)
    except Exception as e:
        print("  ! %s %s" % (s, str(e)[:50]))
ts = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")
print("QUOTES as of %s" % ts)
for s, v in Q.items():
    print("   %-7s %12.4f" % (s, v))

BASE = """PAPER TRADING CONTEST - ROUND 01. Notional $1000. Zero real money. You are the entrant.

TASK: pick 2-5 trades across asset classes. Prefer picks that are right FAST with SMALL drawdowns.
SCORING: R-multiple (profit divided by the distance to your stop).
HARD RULES:
1. NO STOP = the pick is VOID. Every pick needs both tp and sl.
2. tp/sl must bracket entry: long needs sl < entry < tp, short needs tp < entry < sl.
3. Total size_usd across all picks must be <= 1000.
4. Your stated entry price is NOT used. The executor fills at the first actual bar open.
5. If price touches both tp and sl in the same bar, the stop wins.

OUTPUT: one JSON object and nothing before it:
{"agent":"<your model name>","round":"R01","budget_usd":1000,"picks":[{"class":"etf","symbol":"SPY","side":"long","tp":0,"sl":0,"size_usd":250,"horizon_hours":48,"style":"swing","why":"<one line>"}]}

Symbols must be real and tradable. Use realistic price levels near the current market."""

STAMPED = BASE.replace(
    "Use realistic price levels near the current market.",
    "CURRENT MARKET QUOTES as of %s (use these exact levels):\n%s"
    % (ts, "\n".join("   %-7s %12.4f" % (s, v) for s, v in Q.items())))

ENDPOINTS = [
    ("vllm Qwen3.6-35B", "http://127.0.0.1:8000/v1/chat/completions", {"model": "Qwen3.6-35B-A3B-NVFP4", "temperature": 0.3, "max_tokens": 1800}),
    ("ollama glm-5.3-flash:cloud", "http://127.0.0.1:11434/v1/chat/completions", {"model": "glm-5.3-flash:cloud", "temperature": 0.3, "max_tokens": 4000}),
]


def ask(url, body, prompt):
    payload = dict(body)
    payload["messages"] = [{"role": "user", "content": prompt}]
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=dict(UA, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=240, context=CTX) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    msg = j["choices"][0]["message"]
    return (msg.get("content") or "") + "\n" + (msg.get("reasoning_content") or "")


def parse(txt):
    for m in re.finditer(r'\{', txt):
        s = m.start(); depth = 0
        for j in range(s, len(txt)):
            if txt[j] == '{': depth += 1
            elif txt[j] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        o = json.loads(txt[s:j + 1])
                        if isinstance(o.get("picks"), list) and o["picks"]:
                            return o
                    except Exception:
                        pass
                    break
    return None


def score(o):
    inside = void = fund = 0
    detail = []
    for p in o.get("picks", []):
        sym = p.get("symbol")
        if str(p.get("class")) == "fund":
            fund += 1; continue
        px = Q.get(sym)
        if px is None:
            detail.append((sym, "UNPRICED")); continue
        tp, sl, side = p.get("tp"), p.get("sl"), str(p.get("side", "")).lower()
        if not tp or not sl:
            void += 1; detail.append((sym, "NO-BRACKET")); continue
        ok = (sl < px < tp) if side == "long" else (tp < px < sl)
        if ok:
            inside += 1; detail.append((sym, "INSIDE"))
        else:
            void += 1; detail.append((sym, "VOID"))
    return inside, void, fund, detail


results = {}
for name, url, body in ENDPOINTS:
    for arm, prompt in (("bare", BASE), ("stamped", STAMPED)):
        try:
            txt = ask(url, body, prompt)
            o = parse(txt)
            if not o:
                print("%-28s %-8s NO JSON PARSED (%d chars)" % (name, arm, len(txt)))
                continue
            ins, vd, fd, det = score(o)
            results["%s|%s" % (name, arm)] = {"inside": ins, "void": vd, "fund": fd, "detail": det}
            print("%-28s %-8s inside=%d void=%d fund=%d  %s" % (name, arm, ins, vd, fd, det))
        except Exception as e:
            print("%-28s %-8s FAILED %s" % (name, arm, str(e)[:90]))

print("\n=== THE QUESTION: does supplying the quote change the void rate? ===")
for name, _, _ in ENDPOINTS:
    b = results.get("%s|bare" % name); s = results.get("%s|stamped" % name)
    if b and s:
        tb = b["inside"] + b["void"]; ts_ = s["inside"] + s["void"]
        print("  %-28s bare %d/%d void -> stamped %d/%d void" % (name, b["void"], tb, s["void"], ts_))
    else:
        print("  %-28s incomplete (one arm failed)" % name)
json.dump({"quotes": Q, "asof": ts, "results": results}, open("_f1_quote_arm.json", "w"), indent=1)
print("\nwrote _f1_quote_arm.json")
