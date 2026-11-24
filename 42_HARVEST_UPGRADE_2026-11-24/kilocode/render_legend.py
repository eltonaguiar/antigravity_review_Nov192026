#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R
ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "docs" / "harvest.html"; MD = ROOT / "docs" / "HARVEST_METHODOLOGY.md"
r = R.RULE
def repl(path, start, end, body):
    s = path.read_text(); i = s.index(start) + len(start); j = s.index(end, i)
    path.write_text(s[:i] + body + s[j:])
repl(HTML, "<!-- RULE_LEGEND_START -->", "<!-- RULE_LEGEND_END -->", R.consensus_rule_html())
repl(HTML, "<!-- RULE_TREND_START -->", "<!-- RULE_TREND_END -->", R.trend_rule_html())
md = f"""Each analyst contributes `STRONG_BUY +2`, `BUY +1`, `HOLD 0`, `SELL −1`, `STRONG_SELL −2`.

```
score    = (2·strong_buy + buy − sell − 2·strong_sell) / analysts
buy_side = (strong_buy + buy) / analysts
```

A label requires **both** the score and the buy-side share to agree:

| label | condition |
|---|---|
| `STRONG_BUY` | `score ≥ {r['strong_buy']['score_min']:.1f}` and `buy_side ≥ {r['strong_buy']['buy_side_min']:.0%}` |
| `BUY` | `score ≥ {r['buy']['score_min']:.1f}` and `buy_side ≥ {r['buy']['buy_side_min']:.0%}` |
| `SELL` | `score ≤ {r['sell']['score_max']:.1f}` and `buy_side ≤ {r['sell']['buy_side_max']:.0%}` |
| `STRONG_SELL` | `score ≤ {r['strong_sell']['score_max']:.1f}` and `buy_side ≤ {r['strong_sell']['buy_side_max']:.0%}` |
| `HOLD` | anything else |

**Why the second condition.** A score alone mislabels split names: INTC scores 0.35 with only 29%
buy-side, so it is `HOLD`, not `BUY`.

**Trend** is computed once in the pipeline and stored; the page does not re-derive it. A row is
`IMPROVING`/`DETERIORATING` only when `|Δ buy-side| ≥ max({r['trend']['min_abs_pp']:.1f} pp, 100 / n_now)`
**and** at least {r['trend']['min_bucket_moves']} analysts changed bucket; otherwise `STABLE`. When the
analyst count changed between months the row is tagged `CHURN_CONTAMINATED`.

Generated from `42_HARVEST_UPGRADE_2026-11-24/kilocode/harvest_rules.py`; do not hand-edit.
"""
repl(MD, "<!-- RULE_MD_START -->", "<!-- RULE_MD_END -->", md)
print("legend + methodology rendered")
