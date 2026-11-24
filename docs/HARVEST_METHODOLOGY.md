# HARVEST — methodology, definitions, and reviewer checklist

**Page:** [`harvest.html`](harvest.html) · **Feed:** [`data/harvest_signals.json`](data/harvest_signals.json)
**Generator:** [`../tools/harvest_signals.py`](../tools/harvest_signals.py) · **Universe:** [`../harvest/universe.json`](../harvest/universe.json)
**Per-run reports:** `/ZOOCODE/COPILOT<DATETIME>.MD` in the repository root
**Last run documented here:** `2026-11-24T10:43:22Z`

This file exists so a reviewer — human or language model — can decide whether the page's
numbers are trustworthy without reverse-engineering the JavaScript.

---

## 0. For a reviewer: the six things worth checking

Do these in order. Each has a stated way to falsify it.

| # | Claim the page makes | How to check it |
|---|---|---|
| 1 | 71 of 99 symbols have analyst consensus | Read `coverage_by_asset_class` in the feed; the `probed` and `with_consensus` fields must sum to the row count in `signals` |
| 2 | Consensus labels derive from the five buckets | Recompute `(2·SB + B − S − 2·SS) / analysts` for any row and re-bucket with the thresholds in §5 |
| 3 | ETFs, bonds and crypto have *no coverage*, while mutual funds are *blocked* | These are different failure states; §7 defines both and the feed stores them in different arrays (`uncovered` vs `errors`) |
| 4 | Two sources are unavailable this run | Read `sources[]`; each carries `status`, `http`, and a `note` naming the exact failure |
| 5 | "Trend" is not an upgrade/downgrade | §8 — it is a month-over-month change in aggregate share, and the page says so in the legend |
| 6 | Nothing is invented | Every row carries `source` and `fetched_at`; the only source with `rows > 0` is the consensus endpoint |

If any of the six fails, the page is wrong and should be corrected rather than explained.

---

## 1. What this page is — and what it is not

**Is:** a dated snapshot of the sell-side analyst rating distribution for a fixed universe of
tickers, with derived summary statistics, an explicit coverage matrix, and an honest register of
which data sources answered and which refused.

**Is not:**

- **Not investment advice.** It reports what covering analysts published. It adds no rating.
- **Not a price or target page.** There is no price, price target, or upside figure anywhere. Those
  need a paid endpoint; see §7.
- **Not a record of upgrade/downgrade events.** It cannot list "who changed their rating on what
  date", because that endpoint is unavailable on the current plan. §8 explains the substitute and
  why it is weaker.
- **Not a complete market view.** The universe is a hand-chosen list of liquid, well-known names
  (§3), not an index. It is not survivorship-adjusted and not market-cap weighted.

---

## 2. Data sources

| Source | Endpoint | Auth | Status this run |
|---|---|---|---|
| Finnhub analyst recommendation | `GET /stock/recommendation?symbol=<SYM>` | `FINNHUB` env var (licensed key) | **OK** — 71 rows |
| Finnhub upgrade/downgrade | `GET /stock/upgrade-downgrade?symbol=<SYM>` | same key | **UNAVAILABLE** — `HTTP 403` (paid plan required) |
| Finnhub price target | `GET /stock/price-target?symbol=<SYM>` | same key | **UNAVAILABLE** — `HTTP 403` |
| FMP upgrades/downgrades | `GET /api/v4/upgrades-downgrades?symbol=<SYM>` | `FMP_API_KEY` | **UNAVAILABLE** — `HTTP 429 "Limit Reach"` |

The feed records each of these in `sources[]` with its `status`, `http` code, `rows`, and a note.
An unavailable source is never silently omitted, and never substituted with a guess.

**Why the unavailable ones matter.** The most valuable field a HARVEST page could carry is the dated
firm-level action — *"China Renaissance raised AAPL to Buy on 2026-11-11, target 425"*. All three
endpoints that publish that are gated on the current plans. What this page shows instead is
strictly weaker, and §8 is explicit about that.

**Licensing note.** Consensus figures are redistributed from a licensed vendor under that vendor's
terms. This is materially different from scraping a public site; do not treat these numbers as
public-domain data.

---

## 3. Universe

Defined in [`../harvest/universe.json`](../harvest/universe.json): 99 symbols across five classes —
71 stocks spanning all eleven GICS sectors, 14 ETFs, 6 bond ETFs, 6 mutual funds, 2 crypto pairs.

Selection is deliberate and **not** systematic: large, liquid, widely covered names. Consequences a
reviewer should weigh:

- Coverage rates are a property of *this list*, not of the asset classes in general.
- No survivorship adjustment; delisted or acquired names are absent.
- Equal weight per symbol. A 70-analyst mega-cap and a 3-analyst name contribute equally to
  `avg_buy_side_pct`.

---

## 4. Field definitions

| Page column | JSON key | Type | Definition |
|---|---|---|---|
| Symbol | `symbol` | string | Ticker as probed |
| Name | `name` | string | Display name from the universe file (not from the vendor) |
| Class | `asset_class` | enum | `STOCK` / `ETF` / `BOND` / `MUTUAL_FUND` / `CRYPTO` |
| Sector | `sector` | string | Sector label from the universe file |
| Period | `period` | date | Month of the snapshot, dated the 1st |
| Consensus | `consensus` | enum | Derived label; §5 |
| Buy-side % | `buy_side_pct` | float | `(strong_buy + buy) / analysts × 100` |
| Analysts | `analysts` | int | `strong_buy + buy + hold + sell + strong_sell` |
| SB·B·H·S·SS | `strong_buy`…`strong_sell` | ints | Counts of covering analysts per bucket |
| MoM pp | `mom_change_pp` | float | `buy_side_pct − prior_buy_side_pct`; §8 |
| Trend | `direction` | enum | `IMPROVING` / `STABLE` / `DETERIORATING` / `NO_PRIOR_PERIOD` |
| Age (d) | `age_days` | int | `generated_at − period`, in days |

Additional keys not surfaced as columns: `consensus_score`, `prior_period`, `prior_buy_side_pct`,
`prior_consensus`, `has_consensus`, `source`, `fetched_at`.

---

## 5. Consensus label — exact formula

Each analyst contributes a weight:

```
STRONG_BUY  +2
BUY         +1
HOLD         0
SELL        −1
STRONG_SELL −2
```

```
consensus_score = (2·strong_buy + 1·buy + 0·hold − 1·sell − 2·strong_sell) / analysts
```

`consensus_score` lands in `[−2, +2]`. It is bucketed as:

| score | label |
|---|---|
| `≥ 1.0` | `STRONG_BUY` |
| `≥ 0.3` and `< 1.0` | `BUY` |
| `> −0.3` and `< 0.3` | `HOLD` |
| `> −1.0` and `≤ −0.3` | `SELL` |
| `≤ −1.0` | `STRONG_SELL` |

**Worked example.** AAPL at `19 / 48 / 3 / 0 / 0`, 70 analysts:
`(2×19 + 1×48 + 0×3 − 1×0 − 2×0) / 70 = 86 / 70 = 1.229` → `STRONG_BUY`.

**Admission:** the thresholds `±0.3` and `±1.0` are a choice, not a calibration. They were not fitted
to any outcome, and no sensitivity analysis has been run. A reviewer who changes them will change
the label distribution — that is a legitimate criticism of this page, not a bug to be argued away.

---

## 6. Coverage states — three, not two

The single most important distinction on this page. Collapsing these into "no data" is the failure
mode this design exists to prevent.

| State | Meaning | Where it lives | Example this run |
|---|---|---|---|
| **Covered** | Source returned one or more months of consensus | `signals[]`, `has_consensus: true` | 71 stocks |
| **No coverage published** | Source returned a well-formed **empty array**. No analyst publishes a rating for this instrument type. | `uncovered[]` | 14 ETFs, 6 bond ETFs, 2 crypto |
| **No access** | Source returned an **error** (403/429/etc). Coverage may exist; *our credentials cannot see it.* | `errors[]` | 6 mutual funds, `HTTP 403 "You don't have access to this resource."` |

The distinction is not pedantic. "No analyst covers SPY" is a true statement about the product.
"Six mutual funds return 403" is a statement about *this licence*. Reporting them identically would
misrepresent one of them.

Note that `coverage_by_asset_class` counts `with_consensus` only, so `MUTUAL_FUND` shows `0%` — read
it together with `errors[]` to get the right reading. The page's coverage table renders the
403 explanation inline for exactly this reason.

---

## 7. Why there are no prices, targets, or upside figures

Those fields require `/stock/price-target` (403) or an equivalent paid endpoint. Adding a column of
invented or stale prices would be worse than omitting the column. If a reviewer wants them, the
path is to enable a paid plan and extend `tools/harvest_signals.py`, recording the new source in
`sources[]` like the others.

---

## 8. MoM pp and Trend — and what they are not

```
mom_change_pp   = buy_side_pct − prior_buy_side_pct
direction       = IMPROVING       if mom_change_pp ≥ +2.0
                = DETERIORATING   if mom_change_pp ≤ −2.0
                = STABLE          otherwise
                = NO_PRIOR_PERIOD when only one period exists
```

**This is not an upgrade or downgrade.** A real upgrade is a dated event: a named firm moves a name
from Hold to Buy. `mom_change_pp` is the change in the *aggregate share* of positive analysts between
two monthly snapshots. A single firm's upgrade can be entirely invisible in it, and a change can
appear with no identifiable event behind it.

The `±2.0 pp` threshold is, like the bucket thresholds, a choice. It is not calibrated.

Where the page says "IMPROVING", read: *the buy-side share rose by at least two points.* Do not read:
*something was upgraded.*

---

## 9. Reproducing a run

```bash
export FINNHUB=<key>
python3 tools/harvest_signals.py            # full universe, ~2 min at 1.1 s/request
python3 tools/harvest_signals.py --limit 8  # smoke test
```

Writes `docs/data/harvest_signals.json` and `ZOOCODE/COPILOT<YYYYMMDDTHHMMZ>.MD`.

Requests are paced at 1.1 s to respect the vendor's 60/min ceiling. The script refuses to run
without `FINNHUB` set, so it cannot emit an empty feed that looks like a real one.

---

## 10. Known limitations — stated plainly

1. **Monthly, not event-level.** No dated firm actions; see §8.
2. **No price, target, or upside.** See §7.
3. **Thresholds uncalibrated.** Bucket edges (`±0.3`, `±1.0`) and trend edges (`±2.0 pp`) are
   unvalidated choices.
4. **Equal-weighted aggregate.** `avg_buy_side_pct` ignores analyst counts and market cap.
5. **Universe is hand-picked** and not survivorship-adjusted. Coverage percentages describe this
   list, not the asset classes.
6. **Mutual funds may be covered by the vendor at a higher plan tier** — their `0%` is a licence
   artifact, not a market fact.
7. **No forward validation.** Nothing here has been tested against subsequent returns. The page
   makes no claim that analyst consensus predicts anything.
8. **Single vendor.** No cross-vendor agreement check; a vendor error propagates unchallenged.

---

## 11. Open questions a reviewer should press on

- Should funds and ETFs be dropped from the universe entirely, given no analyst coverage exists for
  them, and the page's real subject is equity research? (Prior bus note: mutual-fund NAV is struck
  once daily, so they need NAV-staleness analysis, not ratings.)
- Is `buy_side_pct` or `consensus_score` the better primary sort? They disagree for names with a
  large Strong-Buy bloc.
- Should `avg_buy_side_pct` be analyst-weighted rather than equal-weighted?
- Does analyst-count correlate with subsequent dispersion? If so, low-`analysts` rows should be
  quarantined rather than shown.

---

## 12. Ownership and change log

| Date | Change |
|---|---|
| 2026-11-24T10:43Z | First run; 71 stocks covered, 3 sources registered (1 OK, 2 unavailable) |
| 2026-11-24 | This document added, plus the inline legend, header tooltips, and explained summary cards |

**Coordination note.** A parallel HARVEST implementation exists in this repository
(`KILOCODE/harvest_analysts.py`, `docs/harvest.json`) which carries dated firm-level actions and
price targets sourced from Yahoo/Nasdaq. The page currently renders the feed described here and does
**not** render those fields. Consolidating the two — this feed's breadth and provenance discipline
with that feed's event-level depth — is an open action tracked on the COMS bus as
`notes/ghcopilot-harvest-state-2026-11-24`. Reviewers should assess this page on its own terms;
they should also note that its `recent_actions`-equivalent is missing rather than merely unbuilt.
