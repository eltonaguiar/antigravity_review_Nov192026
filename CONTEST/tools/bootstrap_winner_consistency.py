#!/usr/bin/env python3
import json, math, os, sys, random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent / "ROUND_01_2026-11-23"  # CONTEST/ROUND_01_2026-11-23
TOOLS = Path(__file__).resolve().parent

COST_BP = {
    "bond": 0.6144, "etf": 6.7122, "equity": 12.0749, "fund": 0.0,
    "crypto": 52.0, "fx": 7.533, "commodity": 20.0,
    "option": 20.0, "futures": 20.0, "prediction": 175.0,
}
CRYPTO_MAJORS = {"BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "LINK", "LTC"}

def cost_bp_for(p):
    cls = p["class"]
    if cls == "crypto":
        stem = str(p["symbol"]).upper().replace("-", "")
        for suffix in ("USDT", "USDC", "USD", "PERP"):
            if stem.endswith(suffix):
                stem = stem[:-len(suffix)]
                break
        return 20.0 if stem in CRYPTO_MAJORS else COST_BP[cls]
    return COST_BP[cls]

def load_prices():
    with open(ROOT / "_prices_live.json") as f:
        raw = json.load(f)
    px = {}
    for sym, bars in raw.items():
        if isinstance(bars, list) and bars:
            last = bars[-1]
            px[sym] = float(last.get("close", last.get("adjclose", last.get("price", 0))))
    return px

def load_all_picks():
    entrants = {}
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        pj = d / "picks.json"
        if not pj.exists():
            continue
        with open(pj) as f:
            sub = json.load(f)
        picks = sub.get("picks", [])
        if not picks:
            continue
        agent_name = sub.get("agent", d.name)
        entrants[d.name] = {"agent": agent_name, "slug": d.name, "picks": picks}
    return entrants
def value_pick(p, live_px):
    sym = p["symbol"]
    side = p["side"]
    if p.get("class") == "fund" and p.get("style") == "buy_and_hold":
        return None, "FUND_NAV"
    tp = float(p["tp"])
    sl = float(p["sl"])
    entry = float(p.get("entry_ref_price") or (tp + sl) / 2.0)
    if sym not in live_px:
        return None, "UNPRICED"
        return None, "UNPRICED"
    if p.get("class") == "fund" and p.get("style") == "buy_and_hold":
        return None, "FUND_NAV"
    risk_px = abs(entry - sl)
    if risk_px <= 0:
        return None, "ZERO_RISK"
    live = live_px[sym]
    if side == "long":
        if live >= tp:
            exit_px = tp
            reason = "tp"
        elif live <= sl:
            exit_px = sl
            reason = "sl"
        else:
            exit_px = live
            reason = "live"
    else:
        if live <= tp:
            exit_px = tp
            reason = "tp"
        elif live >= sl:
            exit_px = sl
            reason = "sl"
        else:
            exit_px = live
            reason = "live"
    gross_r = (exit_px - entry) / risk_px
    if side == "short":
        gross_r = -gross_r
    cost_r = (cost_bp_for(p) / 1e4) * entry / risk_px
    net_r = gross_r - cost_r
    return net_r, reason

def entrant_mean_R(entrants, slug, live_px, rng):
    picks = entrants[slug]["picks"]
    scored = []
    for p in picks:
        r, status = value_pick(p, live_px)
        if r is not None:
            scored.append(r)
    if not scored:
        return None
    resampled = [rng.choice(scored) for _ in range(len(scored))]
    return sum(resampled) / len(resampled)

def main():
    rng = random.Random(11)
    live_px = load_prices()
    entrants = load_all_picks()
    n_entrants = len(entrants)
    print(f"Loaded {n_entrants} entrants, {len(live_px)} priced symbols")

    print("\n=== Point estimates (mean net R per entrant) ===")
    point_means = {}
    for slug in sorted(entrants):
        e = entrants[slug]
        scored = []
        for p in e["picks"]:
            r, status = value_pick(p, live_px)
            if r is not None:
                scored.append(r)
        if scored:
            mean_r = sum(scored) / len(scored)
            point_means[slug] = mean_r
            print(f"  {slug:32s} ({e['agent']:30s}) n={len(scored):2d}  mean_R = {mean_r:+.4f}")
        else:
            point_means[slug] = None
            print(f"  {slug:32s} ({e['agent']:30s}) n=0 scored")

    N_REP = 2000
    wins = defaultdict(int)
    for rep in range(N_REP):
        rep_means = {}
        for slug in entrants:
            m = entrant_mean_R(entrants, slug, live_px, rng)
            if m is not None:
                rep_means[slug] = m
        if not rep_means:
            continue
        winner = max(rep_means, key=rep_means.get)
        wins[winner] += 1

    total = sum(wins.values())
    print(f"\n=== Winner counts over {total} replicates ===")
    for slug, count in sorted(wins.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        e = entrants[slug]
        print(f"  {slug:32s} ({e['agent']:30s}) wins={count:4d}  {pct:5.1f}%")

    dominant = None
    for slug, count in wins.items():
        if count / total >= 0.95:
            dominant = slug
            break

    report = {
        "n_entrants": n_entrants,
        "n_replicates": total,
        "seed": 11,
        "point_means": {k: v for k, v in point_means.items() if v is not None},
        "wins": {k: v for k, v in wins.items()},
        "win_pct": {k: round(v / total * 100, 2) for k, v in wins.items()},
        "dominant_winner": dominant,
        "dominant_pct": round(wins[dominant] / total * 100, 2) if dominant else None,
        "ranking_distinguishable": dominant is not None,
    }
    out_json = TOOLS / "reports" / "bootstrap_winner_consistency.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nWrote {out_json}")

    md_lines = [
        "# Bootstrap winner consistency — R01 entrants",
        "",
        "**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/bootstrap_winner_consistency.py`",
        "",
        "## Question",
        "",
        "RULES.md section 7 states that no leaderboard ranking may be published because, with ",
        "4 picks per entrant at normal volatility, two entrants must differ by 7–14 pp in ",
        "mean return before the gap is distinguishable at t=2. The honest leaderboard has ",
        "18 rows and one column: \"not distinguishable.\"",
        "",
        "This test is the falsifier: resample the 18 entrants' picks with replacement 2000x, ",
        "recompute each entrant's mean R per replicate, and record how often the same entrant ",
        "wins. If one entrant wins 95%+ of replicates, the ranking IS distinguishable and ",
        "RULES.md section 7 must be revised.",
        "",
        "## Method",
        "",
        "Each pick is scored as a net R-multiple, mirroring `assess_contest.py`:",
        "",
        "- `entry` = `entry_ref_price` from picks.json, else midpoint(tp, sl)",
        "- `exit` = live price from `_prices_live.json`; if a barrier is breached, exit at that barrier",
        "- `R` = (exit − entry) / |entry − sl| for long, mirrored for short, net of per-class round-trip cost",
        "- `fund` buy_and_hold picks are scored on $ only, excluded from the R ranking",
        "",
        "For each of 2000 replicates, each entrant's picks are resampled with replacement, ",
        "their mean R is recomputed, and the entrant with the highest mean R wins the replicate.",
        "",
        "## Results",
        "",
        "| Entrant | Agent | Point mean R | Bootstrap wins | Win % |",
        "|---|---|---:|---:|---:|",
    ]

    for slug, count in sorted(wins.items(), key=lambda x: -x[1]):
        e = entrants[slug]
        pct = count / total * 100
        mean_r = point_means.get(slug)
        mean_r_str = f"{mean_r:+.4f}" if mean_r is not None else "n/a"
        md_lines.append(f"| {slug} | {e['agent']} | {mean_r_str} | {count} | {pct:.1f}% |")

    for slug in sorted(entrants):
        if slug not in wins:
            e = entrants[slug]
            mean_r = point_means.get(slug)
            mean_r_str = f"{mean_r:+.4f}" if mean_r is not None else "n/a"
            md_lines.append(f"| {slug} | {e['agent']} | {mean_r_str} | 0 | 0.0% |")

    md_lines += [
        "",
        f"Total replicates: {total}",
        "",
    ]

    if dominant:
        md_lines += [
            "## Verdict: RANKING IS DISTINGUISHABLE",
            "",
            f"**{entrants[dominant]['agent']} ({dominant}) wins {wins[dominant]} of {total} "
            f"replicates ({wins[dominant]/total*100:.1f}%) — above the 95% threshold.**",
            "",
            "The same entrant wins the bootstrap overwhelmingly, meaning its mean-R advantage "
            "over the field is robust to resampling noise. RULES.md section 7's 'no ranking' "
            "claim is falsified for this round and should be revised.",
        ]
    else:
        md_lines += [
            "## Verdict: RANKING NOT DISTINGUISHABLE",
            "",
            "**No entrant wins 95%+ of bootstrap replicates.** The wins are spread across the field, "
            "consistent with RULES.md section 7: with 4 picks per entrant, the sampling noise is "
            "large enough that no ranking is robustly distinguishable.",
            "",
            "The honest leaderboard stands: 18 rows, one column — \"not distinguishable.\"",
        ]

    md_lines += [
        "",
        "*Paper only. Zero capital. Not investment advice.*",
    ]

    out_md = ROOT / "BOOTSTRAP_WINNER_CONSISTENCY.md"
    out_md.write_text("\n".join(md_lines) + "\n")
    print(f"Wrote {out_md}")
    print(f"\nDominant winner: {dominant} ({'%.1f%%' % (wins[dominant]/total*100) if dominant else 'N/A'})")
    print(f"Ranking distinguishable: {dominant is not None}")

if __name__ == "__main__":
    main()
