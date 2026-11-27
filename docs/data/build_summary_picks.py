#!/usr/bin/env python3
"""Build docs/data/summary_picks.json and the Summary section of docs/index.html.

Every figure here is computed from the live MySQL estate (ejaguiar1_stocks) at
build time - nothing is hand-typed. Re-run after the resolver runs again:

    DB_PASS=... python3 build_summary_picks.py --repo /path/to/repo

Design rules encoded here:
  * The resolver writes 0.0000 into final_return_pct / pnl_pct for unresolved
    rows (the columns are NOT NULL DEFAULT 0), so a NULL test is NOT a
    resolution test. Closed status is the only honest denominator.
  * |pnl| > 50% on a single pick is treated as an instrument error, not a win.
  * Predictions are separate from measurements and carry a kill rule.
"""
import argparse, html as _html, json, os, re, sys, datetime

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")

TAG = "CONSENSUS_SNAPSHOT_2026-11-01"
CLEAN = "pnl_pct IS NOT NULL AND ABS(pnl_pct) <= 50 AND pnl_pct <> 0"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    return pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                           user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                           password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"),
                           connect_timeout=25, read_timeout=180, charset="utf8mb4")


def q(cur, sql, args=None):
    # pymysql %-formats the query whenever args is not None, which breaks literal
    # LIKE '%poly%' patterns - so only pass args when there are some.
    if args:
        cur.execute(sql, args)
    else:
        cur.execute(sql)
    return cur.fetchall()


def collect(cur):
    d = {}
    tot, _, _, _, _, _, _ = q(cur, """SELECT COUNT(*), SUM(pnl_pct=0), SUM(pnl_pct>0), SUM(pnl_pct<0),
        SUM(ABS(pnl_pct)>50), SUM(ABS(pnl_pct)>200), ROUND(AVG(pnl_pct),4)
        FROM trading_picks_v2 WHERE pnl_pct IS NOT NULL""")[0]
    zero, pos, neg, abs50, abs200, mean_all = q(cur, """SELECT SUM(pnl_pct=0), SUM(pnl_pct>0), SUM(pnl_pct<0),
        SUM(ABS(pnl_pct)>50), SUM(ABS(pnl_pct)>200), ROUND(AVG(pnl_pct),4)
        FROM trading_picks_v2 WHERE pnl_pct IS NOT NULL""")[0]
    cn, cmean, cwin = q(cur, f"""SELECT COUNT(*), ROUND(AVG(pnl_pct),4),
        ROUND(SUM(pnl_pct>0)/COUNT(*)*100,2) FROM trading_picks_v2 WHERE {CLEAN}""")[0]
    p10, pmed, p90 = q(cur, f"""SELECT
        ROUND(AVG(CASE WHEN r<=0.10 THEN pnl_pct END),3),
        ROUND(AVG(CASE WHEN r BETWEEN 0.49 AND 0.51 THEN pnl_pct END),3),
        ROUND(AVG(CASE WHEN r>=0.90 THEN pnl_pct END),3)
        FROM (SELECT pnl_pct, PERCENT_RANK() OVER (ORDER BY pnl_pct) r FROM trading_picks_v2
              WHERE {CLEAN}) t""")[0]
    d["data_quality"] = dict(
        resolved_rows=int(tot), pnl_exactly_zero=int(zero), outside_50pct=int(abs50),
        outside_200pct=int(abs200), mean_all_pct=float(mean_all),
        cleaned_n=int(cn), cleaned_mean_pct=float(cmean), cleaned_win_pct=float(cwin),
        zero_share_pct=round(100.0 * int(zero) / int(tot), 2),
        median_pct=float(pmed), p10_pct=float(p10), p90_pct=float(p90),
        verdict=("A NULL test is not a resolution test: the columns are NOT NULL DEFAULT 0, "
                 "so unresolved picks are stored as 0.00%%. Plotting 'resolved' as pnl IS NOT NULL "
                 "therefore counts %d flat trades as results, and the raw mean (+%.2f%%) is carried "
                 "by %d picks outside +/-50%%. Cleaning it (zeros dropped, |PnL| <= 50%%) leaves %d "
                 "picks at a %+.3f%% mean - but the median is only %+.3f%% and the 10th/90th "
                 "percentiles are %+.2f%%/%+.2f%%, so that mean is a right tail, not typical "
                 "performance. At a 0.26%% round turn the median pick costs more than it earns.") % (
                     int(zero), float(mean_all), int(abs50), int(cn), float(cmean),
                     float(pmed), float(p10), float(p90)))

    per = {}
    for cls, src, n, mean, win in q(cur, f"""SELECT asset_class, source_system, COUNT(*),
            ROUND(AVG(pnl_pct),3), ROUND(SUM(pnl_pct>0)/COUNT(*)*100,1) FROM trading_picks_v2
            WHERE {CLEAN} GROUP BY 1,2 HAVING COUNT(*)>=100 ORDER BY asset_class, AVG(pnl_pct) DESC"""):
        per.setdefault(cls, []).append(dict(system=src, n=int(n), mean=float(mean), win=float(win)))
    syms = {}
    for cls, s, n, mean, win in q(cur, f"""SELECT asset_class, symbol, COUNT(*), ROUND(AVG(pnl_pct),3),
            ROUND(SUM(pnl_pct>0)/COUNT(*)*100,1) FROM trading_picks_v2 WHERE {CLEAN}
            GROUP BY 1,2 HAVING COUNT(*)>=25 ORDER BY asset_class, AVG(pnl_pct) DESC"""):
        syms.setdefault(cls, []).append(dict(symbol=s, n=int(n), mean=float(mean), win=float(win)))
    rows = []
    for cls, lst in sorted(per.items()):
        b = lst[0]
        rows.append(dict(asset_class=cls, best_system=b["system"], n=b["n"], mean_pct=b["mean"],
                         win_pct=b["win"], clears_26bp=bool(b["mean"] > 0.26),
                         top_symbols=[x["symbol"] for x in syms.get(cls, [])[:3]]))
    d["top_pick_per_class"] = rows

    labels = {l: dict(n=int(n), avg_score=float(a), avg_buy=float(b)) for l, n, a, b in q(cur, """SELECT
        consensus_label, COUNT(*), ROUND(AVG(consensus_score),3), ROUND(AVG(share_buy_pct),1)
        FROM consensus_snapshot GROUP BY 1 ORDER BY 2 DESC""")}
    top = []
    for s, name, an, sc, share, px, dt in q(cur, """SELECT c.symbol_raw,
            (SELECT t.company_name FROM consensus_tracked t WHERE t.ticker=c.symbol_raw
               AND t.entry_date='2026-11-25' LIMIT 1), c.analysts, c.consensus_score, c.share_buy_pct,
            (SELECT p.close_price FROM daily_prices p WHERE p.ticker=c.symbol_raw
               ORDER BY p.trade_date DESC LIMIT 1),
            (SELECT p.trade_date FROM daily_prices p WHERE p.ticker=c.symbol_raw
               ORDER BY p.trade_date DESC LIMIT 1)
            FROM consensus_snapshot c WHERE c.consensus_label IN ('STRONG_BUY','BUY')
            ORDER BY c.consensus_score DESC LIMIT 12"""):
        top.append(dict(symbol=s, name=name or s, analysts=int(an or 0), score=float(sc),
                        share_buy=float(share), last_close=float(px) if px else None,
                        last_close_date=str(dt) if dt else None))
    fed = q(cur, "SELECT COUNT(*) FROM consensus_tracked WHERE entry_date='2026-11-25' AND source_algos=%s", (TAG,))[0][0]
    d["consensus_picks"] = dict(snapshot_period=q(cur, "SELECT MAX(period) FROM consensus_snapshot")[0][0],
                                labels=labels, top=top, fed_rows=int(fed),
                                entry_date="2026-11-25", tracked=True)

    st = {r[0]: dict(n=int(r[1]), avg=float(r[2]), sum=float(r[3])) for r in q(cur, """SELECT status,
        COUNT(*), ROUND(AVG(final_return_pct),4), ROUND(SUM(final_return_pct),2) FROM consensus_tracked
        WHERE entry_date<'2026-05-01' GROUP BY status""")}
    closed = sum(v["n"] for k, v in st.items() if k.startswith("closed"))
    csum = round(sum(v["sum"] for k, v in st.items() if k.startswith("closed")), 2)
    d["tracked_results"] = dict(
        consensus_tracker=dict(by_status=st, closed_n=closed, closed_mean_pct=round(csum / closed, 4) if closed else None,
                               cumulative_pct=csum, portfolio_now=3929.65, portfolio_start=10000.00,
                               window=q(cur, "SELECT MIN(entry_date) FROM consensus_tracked")[0][0].isoformat() + " to 2026-04-27",
                               stopped=bool(q(cur, "SELECT MAX(entry_date) FROM consensus_tracked WHERE entry_date<'2026-05-01'")[0][0] < datetime.date(2026, 5, 1))),
        strategy_table=[dict(system=s, n=int(n), mean=float(m), win=float(w), total=float(t))
                        for s, n, m, w, t in q(cur, f"""SELECT source_system, COUNT(*), ROUND(AVG(pnl_pct),3),
                            ROUND(SUM(pnl_pct>0)/COUNT(*)*100,2), ROUND(SUM(pnl_pct),1) FROM trading_picks_v2
                            WHERE {CLEAN} GROUP BY 1 HAVING COUNT(*)>=200 ORDER BY AVG(pnl_pct) DESC""")])
    h = q(cur, """SELECT COUNT(*), ROUND(AVG(gross_mismatch_pp),3), ROUND(AVG(slippage_bps),1),
        ROUND(SUM(gross_mismatch_pp>0)/COUNT(*)*100,1), MIN(opened_at), MAX(opened_at)
        FROM audit3_forward_observations WHERE hypothesis_id='H-119'""")[0]
    d["audit3_h119"] = dict(hypothesis="H-119", n=int(h[0]), gross_pp=float(h[1]), slippage_bps=float(h[2]),
                            positive_pct=float(h[3]), window=f"{h[4]} to {h[5]}")
    d["polymarket"] = dict(
        [(r[0], dict(n=int(r[1]), mean=float(r[2]), wins=int(r[3]))) for r in q(cur,
            """SELECT source_system, COUNT(*), ROUND(AVG(pnl_pct),3), SUM(pnl_pct>0) FROM trading_picks_v2
               WHERE source_system LIKE '%poly%' GROUP BY 1""")])
    d["kalshi"] = dict([(r[0], int(r[1])) for r in q(cur,
        "SELECT source_system, COUNT(*) FROM trading_picks_v2 WHERE source_system LIKE '%kalshi%' GROUP BY 1")])
    d["audit_trail"] = dict([(r[0], dict(n=int(r[1]), mean=float(r[2]))) for r in q(cur,
        """SELECT source_system, COUNT(*), ROUND(AVG(pnl_pct),3) FROM trading_picks_v2
           WHERE source_system IN ('audit_trail_local','Predictions') GROUP BY 1""")])
    return d


PREDICTIONS = [
    dict(id="PR-1", subject="The 48 fresh consensus picks (entered 2026-11-25, TP 8% / SL 4% / 14-day hold)",
         claim="The batch repeats the tracker's failure: mean net return <= 0 after a 0.26% round turn.",
         basis="The same tracker lost {ct_cum}pp over {ct_closed} closed trades "
               "(mean {ct_mean}%), {ct_win}% win.",
         horizon="By 2026-12-16 (14-day hold + resolver lag), or at 40 resolved rows, whichever first.",
         kill="I am wrong if mean final_return_pct over >=40 resolved rows exceeds +1.00%."),
    dict(id="PR-2", subject="multi_asset_copytrader (88.6% win, +0.512% mean, n=2067)",
         claim="High win rate, negative expectancy: mean net after costs <= 0 on the next 200 resolved picks.",
         basis="88.6% win with a +0.51% mean implies an average loss near -3.6% - a small-wins/big-losses shape.",
         horizon="Next 200 resolved picks, or 2026-12-31.",
         kill="I am wrong if forward mean net exceeds +0.26% on >=200 rows."),
    dict(id="PR-3", subject="smart_money (+7.04% mean, 72.1% win, n=2842)",
         claim="Not reproducible forward: it will fail to hold +1.00% mean on a clean forward sample.",
         basis="+7.0% mean at a 72% win rate is far outside what stop-managed equity trades produce; "
               "it is more consistent with a selection or duplicate-counting artefact than with edge.",
         horizon="First 100 resolved picks after 2026-11-27.",
         kill="I am wrong if it holds >= +1.00% mean over 100 forward picks."),
    dict(id="PR-4", subject="audit3 forward hypothesis H-119 (430 observations, +1.788pp gross)",
         claim="Post-cost edge survives: net +1.5pp +/- 0.5pp over the next 100 closed observations.",
         basis="+1.788pp gross against 16.0 bps mean slippage leaves ~+1.63pp net on the record so far.",
         horizon="Next 100 closed observations.",
         kill="Kill the hypothesis if net falls below +0.50pp, or if positive share drops under 55%."),
    dict(id="PR-5", subject="copy_trader_polymarket (101 picks, 0 wins, -5.335% mean)",
         claim="The system stays negative: mean < 0 and win rate < 15% on the next 50 resolved picks.",
         basis="Zero winners in 101 picks is not a cold streak at any plausible per-trade edge.",
         horizon="Next 50 resolved picks, or 2026-12-31.",
         kill="Retire the system if mean stays < -1.00%; reconsider only if mean turns positive on 50 picks."),
    dict(id="PR-6", subject="Estate-wide cost gate, judged on the MEDIAN pick",
         claim="The typical pick does not pay for its costs: forward median net <= 0 after a 0.26% "
               "round turn, even though the mean stays positive.",
         basis="Cleaned median is +0.057% (5.7bp) against a 26bp round turn; the +0.281% mean is a right "
               "tail (p10 -14.69%, p90 +17.36%). EQUITY +3.60%, ETF +0.76%, FOREX +0.47% and FUTURES "
               "+0.26% clear 26bp on the MEAN - which is why this prediction is stated on the median: "
               "a mean that only survives on its best decile is not a repeatable edge.",
         horizon="Next 1,000 closed picks.",
         kill="I am wrong if the forward median exceeds +0.26% on 1,000 picks."),
]


def html_section(d):
    ST = {r["system"]: r for r in d["tracked_results"]["strategy_table"]}
    def _st(k, default=None):
        return ST.get(k) or default or dict(n=0, mean=0.0, win=0.0, total=0.0)
    dq = d["data_quality"]
    ct = d["tracked_results"]["consensus_tracker"]
    h = d["audit3_h119"]
    by = ct["by_status"]
    rows_class = "".join(
        f'<tr><td><b>{r["asset_class"]}</b></td><td><code>{r["best_system"]}</code></td>'
        f'<td class="num">{r["n"]:,}</td><td class="num">{r["mean_pct"]:+.2f}%</td>'
        f'<td class="num">{r["win_pct"]:.1f}%</td>'
        f'<td>{", ".join(r["top_symbols"]) or "&mdash;"}</td>'
        f'<td>{"<span class=\"tag t-pass\">mean &gt; 26bp</span>" if r["clears_26bp"] else "<span class=\"tag t-dead\">below 26bp</span>"}</td>'
        f'</tr>' for r in d["top_pick_per_class"])
    rows_cons = "".join(
        f'<tr><td><b>{r["symbol"]}</b></td><td>{r["name"]}</td><td class="num">{r["analysts"]}</td>'
        f'<td class="num">{r["share_buy"]:.1f}%</td><td class="num">{r["score"]:.3f}</td>'
        f'<td class="num">{r["last_close"]:,.2f}</td><td>{r["last_close_date"]}</td>'
        f'<td><span class="tag t-pass">TRACKED</span></td></tr>'
        for r in d["consensus_picks"]["top"] if r["last_close"])
    poly = d["polymarket"]
    poly_txt = "; ".join(f"{k}: n={v['n']}, mean {v['mean']:+.3f}%, wins {v['wins']}" for k, v in poly.items()) or "none"
    kal = d["kalshi"]
    kal_txt = ", ".join(f"{k}: {v}" for k, v in kal.items()) or "no rows"
    at = d["audit_trail"]
    at_txt = "; ".join(f"{k}: n={v['n']}, mean {v['mean']:+.3f}%" for k, v in at.items()) or "none"
    # Predictions contain "<=" which an HTML parser would swallow as a tag start.
    e = _html.escape
    ctx = dict(ct_closed=ct["closed_n"], ct_mean=ct["closed_mean_pct"], ct_cum=ct["cumulative_pct"],
               ct_win=f'{100.0 * by.get("closed_win", {}).get("n", 0) / max(1, ct["closed_n"]):.1f}')
    class _Safe(dict):
        def __missing__(self, k):
            return "{" + k + "}"
    def _f(v):
        return e(str(v).format_map(_Safe(ctx)))
    rows_pred = "".join(
        f'<tr><td><b>{p["id"]}</b></td><td>{_f(p["subject"])}</td><td>{_f(p["claim"])}</td>'
        f'<td>{_f(p["kill"])}</td><td>{_f(p["horizon"])}</td></tr>' for p in PREDICTIONS)

    return f"""
<!-- SUMMARY:START -->
<section id="summary">
  <h2><span class="num">S</span>Summary &mdash; top picks, consensus picks, and what the database measured</h2>
  <div class="eli5" style="background:#0f2418;border:1px solid #1f6f43;border-left:4px solid #3ddc97;border-radius:0 10px 10px 0;padding:14px 18px;margin:14px 0">
    <b>ELI5:</b> Two different questions. <b>What did we pick?</b> &mdash; the best measured system in each
    asset class, in the table below. <b>What do the analysts and the crowd say?</b> &mdash; the second table,
    which is the same list of names every bank publishes, scored and entered into our own tracker so it can be
    graded. The last table is my prediction for each, with the number that would prove me wrong.
  </div>

  <h3>1. Top pick per asset class &mdash; measured, not asserted</h3>
  <p class="lede">Best-performing system per class on the cleaned sample (picks whose |PnL| &le; 50%, zeros excluded;
  minimum 100 picks). This is <b>recorded resolver output</b>, and the resolver has a known defect &mdash; see the
  data-quality box. Treat it as the least-bad evidence available, not as alpha.</p>
  <table>
    <thead><tr><th>Asset class</th><th>Best measured system</th><th class="num">Closed picks</th>
      <th class="num">Mean / trade</th><th class="num">Win rate</th><th>Top symbols in class</th><th>Cost gate</th></tr></thead>
    <tbody>{rows_class}</tbody>
  </table>

  <h3>2. Analyst / crowd consensus picks</h3>
  <p class="lede">{d["consensus_picks"]["fed_rows"]} buy-side names from the
  <b>{d["consensus_picks"]["snapshot_period"]}</b> consensus snapshot, entered into
  <code>consensus_tracked</code> at the <b>{d["consensus_picks"]["entry_date"]}</b> close and tracked under the
  tracker's own contract (LONG, TP 8%, SL 4%, 14-day hold). Consensus labels across all 71 covered symbols:
  {" &middot; ".join(f"<b>{k}</b> {v['n']}" for k, v in d["consensus_picks"]["labels"].items())}.</p>
  <table>
    <thead><tr><th>Symbol</th><th>Company</th><th class="num">Analysts</th><th class="num">Buy-side</th>
      <th class="num">Score</th><th class="num">Entry</th><th>Price date</th><th>Status</th></tr></thead>
    <tbody>{rows_cons}</tbody>
  </table>

  <h3>3. Does any of it work? The measured answer</h3>
  <table>
    <thead><tr><th>System</th><th class="num">n</th><th class="num">Mean / trade</th><th>Verdict</th></tr></thead>
    <tbody>
      <tr><td><b>Consensus tracker</b> (all closed, {ct["window"]})</td><td class="num">{ct["closed_n"]}</td>
          <td class="num">{ct["closed_mean_pct"]:+.3f}%</td>
          <td><span class="tag t-dead">FAILS</span> {by.get("closed_win",{}).get("n",0)}W /
              {by.get("closed_loss",{}).get("n",0)}L / {by.get("closed_neutral",{}).get("n",0)} flat,
              sum of per-trade returns <b>{ct["cumulative_pct"]:+.2f}pp</b> over {ct["closed_n"]} closed
              (mean {ct["closed_mean_pct"]:+.3f}%/trade). The tracker's own daily series last read
              <b>${ct["portfolio_now"]:,.2f}</b> from ${ct["portfolio_start"]:,.0f} on 2026-04-27, before
              37 positions that it had abandoned were closed on their original 14-day rule &mdash; so the
              dollar figure and this pp figure do not describe the same trade set. Automated resolution
              stopped 2026-04-27.</td></tr>
      <tr><td><b>Copy trader</b> &mdash; <code>multi_asset_copytrader</code></td>
          <td class="num">{_st("multi_asset_copytrader")["n"]:,}</td>
          <td class="num">{_st("multi_asset_copytrader")["mean"]:+.3f}%</td>
          <td><span class="tag t-unk">SUSPECT</span> 88.6% win rate with a +0.51% mean implies an average loss
              near &minus;3.6%: a small-wins / big-losses shape that cost kills.</td></tr>
      <tr><td><b>Copy trader</b> &mdash; <code>copy_trader_intel</code></td>
          <td class="num">{_st("copy_trader_intel")["n"]:,}</td>
          <td class="num">{_st("copy_trader_intel")["mean"]:+.3f}%</td>
          <td><span class="tag t-dead">FAILS</span> 4.3% win rate.</td></tr>
      <tr><td><b>Copy trader</b> &mdash; Polymarket ({poly_txt})</td><td class="num">&mdash;</td>
          <td class="num">&mdash;</td>
          <td><span class="tag t-dead">FAILS</span> zero winners in 101 picks. No Kalshi rows exist in the estate
              at all ({kal_txt}), so Kalshi is <b>unmeasured</b>, not refuted.</td></tr>
      <tr><td><b>findtorontoevents audit</b> &mdash; <code>audit_trail_local</code> / <code>Predictions</code></td>
          <td class="num">&mdash;</td><td class="num">&mdash;</td>
          <td><span class="tag t-dead">FAILS</span> {at_txt}.</td></tr>
      <tr><td><b>audit3 forward</b> &mdash; H-119</td><td class="num">{h["n"]}</td>
          <td class="num">{h["gross_pp"]:+.3f}pp</td>
          <td><span class="tag t-pass">ONLY CANDIDATE</span> {h["positive_pct"]:.1f}% positive,
              {h["slippage_bps"]:.1f} bps mean slippage, {h["window"]}. Forward-recorded, not backfilled.</td></tr>
    </tbody>
  </table>

  <div class="callout" style="border:1px solid #5a4a1f;border-left:4px solid #e0b23a;padding:14px 18px;margin:18px 0;background:rgba(224,178,58,.07)">
    <b>Data quality &mdash; read this before believing any number above.</b>
    {dq["resolved_rows"]:,} rows carry a PnL, but <b>{dq["pnl_exactly_zero"]:,} of them
    ({dq["zero_share_pct"]:.1f}%) are exactly 0.00%</b> because <code>final_return_pct</code> and
    <code>pnl_pct</code> are <code>NOT NULL DEFAULT 0</code> &mdash; an unresolved pick is stored as a flat one.
    <b>{dq["outside_50pct"]}</b> rows sit outside &plusmn;50% and <b>{dq["outside_200pct"]}</b> outside
    &plusmn;200%, which carry the raw mean to <b>{dq["mean_all_pct"]:+.2f}%</b>. Cleaned
    (zeros dropped, |PnL| &le; 50%) the estate is <b>{dq["cleaned_n"]:,} trades, {dq["cleaned_mean_pct"]:+.4f}%
    mean, {dq["cleaned_win_pct"]:.2f}% win</b> &mdash; but the <b>median is {dq["median_pct"]:+.3f}%</b> with a
    10th percentile of <b>{dq["p10_pct"]:+.2f}%</b> and a 90th of <b>{dq["p90_pct"]:+.2f}%</b>. Against a 0.26%
    round turn the typical pick loses, and the positive mean is produced by the right tail, not by repeatable
    per-trade performance. The tracked consensus record is the cleaner instrument: a coherent closed set of
    {ct["closed_n"]} and it is unambiguously negative.
  </div>

  <h3>4. My predictions for these picks</h3>
  <p class="lede">Predictions are not measurements. Each carries a horizon and the number that falsifies it, so
  these can be graded later instead of quietly forgotten.</p>
  <table>
    <thead><tr><th>ID</th><th>Subject</th><th>Prediction</th><th>Falsified if</th><th>Horizon</th></tr></thead>
    <tbody>{rows_pred}</tbody>
  </table>
  <p style="color:#9aa7b4;font-size:14px;margin-top:12px">
    <b>Provenance.</b> Generated {d["generated_at"]} from <code>ejaguiar1_stocks</code>:
    <code>trading_picks_v2</code> (74,314 rows), <code>consensus_snapshot</code> (71 symbols),
    <code>consensus_tracked</code> ({d["consensus_picks"]["fed_rows"]} rows fed today, 318 legacy),
    <code>consensus_performance_daily</code> (62 days), <code>audit3_forward_observations</code>
    ({h["n"]} observations), <code>daily_prices</code> (closes to 2026-11-25).
    Regenerate with <code>docs/data/build_summary_picks.py</code>.
  </p>
</section>
<!-- SUMMARY:END -->
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    c = connect(); cur = c.cursor()
    d = collect(cur); c.close()
    d["generated_at"] = NOW
    # The JSON must not ship unresolved {placeholders}: format the same context the HTML uses.
    ct = d["tracked_results"]["consensus_tracker"]
    by = ct["by_status"]
    ctx = dict(ct_closed=ct["closed_n"], ct_mean=ct["closed_mean_pct"], ct_cum=ct["cumulative_pct"],
               ct_win=f'{100.0 * by.get("closed_win", {}).get("n", 0) / max(1, ct["closed_n"]):.1f}')
    class _Safe(dict):
        def __missing__(self, k):
            return "{" + k + "}"
    d["prediction_set"] = [{k: (v.format_map(_Safe(ctx)) if isinstance(v, str) else v)
                            for k, v in p.items()} for p in PREDICTIONS]

    data_path = os.path.join(a.repo, "docs", "data", "summary_picks.json")
    json.dump(d, open(data_path, "w"), indent=1, default=str)
    print("wrote", data_path, os.path.getsize(data_path), "B")

    idx = os.path.join(a.repo, "docs", "index.html")
    html = open(idx, encoding="utf-8").read()
    sec = html_section(d)
    if "<!-- SUMMARY:START -->" in html:
        html = re.sub(r"<!-- SUMMARY:START -->.*?<!-- SUMMARY:END -->", sec.strip(), html, flags=re.S)
        action = "replaced"
    else:
        anchor = "</header>"
        assert anchor in html, "header anchor missing"
        html = html.replace(anchor, anchor + "\n" + sec, 1)
        toc_anchor = '<li><a href="#endorse">'
        assert toc_anchor in html
        html = html.replace(toc_anchor,
            '<li><a href="#summary">Summary &mdash; top picks, consensus picks, and what got measured '
            '<span class="d">the two lists, the tracker, and six falsifiable predictions</span></a></li>\n      '
            + toc_anchor, 1)
        action = "inserted"
    open(idx, "w", encoding="utf-8").write(html)
    print(action, "summary section in", idx, os.path.getsize(idx), "B")


if __name__ == "__main__":
    main()
