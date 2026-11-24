"""Single source of truth for HARVEST classification + legend rendering."""
from __future__ import annotations
RULE = {
    "weights": {"strong_buy": 2, "buy": 1, "hold": 0, "sell": -1, "strong_sell": -2},
    "strong_buy": {"score_min": 1.0, "buy_side_min": 0.75},
    "buy": {"score_min": 0.3, "buy_side_min": 0.50},
    "sell": {"score_max": -0.3, "buy_side_max": 0.30},
    "strong_sell": {"score_max": -1.0, "buy_side_max": 0.15},
    "trend": {"min_abs_pp": 2.0, "min_bucket_moves": 2, "noise_floor_pp": "100 / n_now"},
}
REASON_CODES = ("NO_COVERAGE_STRUCTURAL", "NO_COVERAGE_VENDOR", "SYMBOL_UNMAPPED",
                "ACCESS_DENIED_403", "RATE_LIMITED_429", "EMPTY_RESPONSE", "STALE_OK")

def counts_total(strong_buy, buy, hold, sell, strong_sell):
    return strong_buy + buy + hold + sell + strong_sell

def score_of(strong_buy, buy, hold, sell, strong_sell):
    n = counts_total(strong_buy, buy, hold, sell, strong_sell)
    return None if not n else (2 * strong_buy + buy - sell - 2 * strong_sell) / n

def buy_side_of(strong_buy, buy, hold, sell, strong_sell):
    n = counts_total(strong_buy, buy, hold, sell, strong_sell)
    return None if not n else (strong_buy + buy) / n

def label_for_counts(strong_buy, buy, hold, sell, strong_sell):
    score = score_of(strong_buy, buy, hold, sell, strong_sell)
    bs = buy_side_of(strong_buy, buy, hold, sell, strong_sell)
    if score is None:
        return None
    if score >= RULE["strong_buy"]["score_min"] and bs >= RULE["strong_buy"]["buy_side_min"]:
        return "STRONG_BUY"
    if score >= RULE["buy"]["score_min"] and bs >= RULE["buy"]["buy_side_min"]:
        return "BUY"
    if score <= RULE["strong_sell"]["score_max"] and bs <= RULE["strong_sell"]["buy_side_max"]:
        return "STRONG_SELL"
    if score <= RULE["sell"]["score_max"] and bs <= RULE["sell"]["buy_side_max"]:
        return "SELL"
    return "HOLD"

def bucket_moves(prev, now):
    keys = ("strong_buy", "buy", "hold", "sell", "strong_sell")
    return sum(abs(now.get(k, 0) - prev.get(k, 0)) for k in keys) // 2

def direction_for(delta_pp, n_now, moves):
    if delta_pp is None or not n_now:
        return "STABLE"
    floor = max(RULE["trend"]["min_abs_pp"], 100.0 / n_now)
    if abs(delta_pp) < floor or moves < RULE["trend"]["min_bucket_moves"]:
        return "STABLE"
    return "IMPROVING" if delta_pp > 0 else "DETERIORATING"

def consensus_rule_html():
    r = RULE
    return (
        "<p>One label, derived only from the five counts — not a separate opinion. "
        "Each analyst scores +2 (SB), +1 (B), 0 (H), −1 (S), −2 (SS).</p>"
        "<p><code>score = (2·SB + B − S − 2·SS) / analysts</code> · "
        "<code>buy-side = (SB + B) / analysts</code></p>"
        f"<ul><li><b>STRONG BUY</b>: score ≥ {r['strong_buy']['score_min']:.1f} <b>and</b> buy-side ≥ {r['strong_buy']['buy_side_min']:.0%}</li>"
        f"<li><b>BUY</b>: score ≥ {r['buy']['score_min']:.1f} <b>and</b> buy-side ≥ {r['buy']['buy_side_min']:.0%}</li>"
        f"<li><b>SELL</b>: score ≤ {r['sell']['score_max']:.1f} <b>and</b> buy-side ≤ {r['sell']['buy_side_max']:.0%}</li>"
        f"<li><b>STRONG SELL</b>: score ≤ {r['strong_sell']['score_max']:.1f} <b>and</b> buy-side ≤ {r['strong_sell']['buy_side_max']:.0%}</li>"
        "<li><b>HOLD</b>: anything else.</li></ul>"
        "<p><em>Why both conditions?</em> A score alone can label a split name BUY; INTC scores 0.35 "
        "but only 29% of analysts say Buy, so it is HOLD.</p>"
    )

def trend_rule_html():
    r = RULE
    return (
        "<p>Computed once in the pipeline and stored; the page does not re-derive it. "
        "IMPROVING/DETERIORATING requires <b>both</b>:</p>"
        f"<ul><li>|Δ buy-side| ≥ max({r['trend']['min_abs_pp']:.1f} pp, 100 / n_now) — the coverage-relative noise floor</li>"
        f"<li>at least {r['trend']['min_bucket_moves']} analysts changed rating bucket</li></ul>"
        "<p>Otherwise STABLE. If the analyst count changed between months the row is tagged "
        "<code>CHURN_CONTAMINATED</code>. This is a change in the analyst mix, <b>not</b> a firm "
        "upgrade/downgrade event.</p>"
    )
