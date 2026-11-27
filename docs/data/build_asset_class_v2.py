#!/usr/bin/env python3
"""Per-asset-class performance + best closed picks per class, from at_local_picks.

Corrections applied to every earlier published number:
  1. DUPLICATES - engines re-emit the same pick hourly; a 24h window of 78k
     "resolved" rows is only ~2.8k unique picks. Stats are computed on unique picks
     (symbol, direction, entry, TP, SL, source).
  2. LABELS WITHOUT NUMBERS - WON/LOST rows with NULL/0 pnl are counted, not
     averaged as flat.

Single query pulls the deduped rows; all statistics (incl. median) are computed in
Python so no window-function/offset gymnastics are needed.

Usage: DB_PASS=... python3 build_asset_class_v2.py --repo /path [--hours 24]
"""
import argparse, datetime, json, os, re, statistics, sys

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")

NOW = datetime.datetime.now(datetime.timezone.utc)
KEY = "symbol, direction, entry_price, take_profit, stop_loss, source_system"
PNL_OK = "pnl_pct IS NOT NULL AND pnl_pct <> 0 AND ABS(pnl_pct) <= 50"


def connect():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    c = pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                        user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                        password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"))
    cur = c.cursor(); cur.execute("SET SESSION max_execution_time=25000")
    return c, cur


def collect(cur, hours):
    cur.execute("SELECT MAX(id) FROM at_local_picks"); mx = cur.fetchone()[0]
    lo = mx - (3_000_000 if hours <= 24 else 25_000_000)
    d = {"generated_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_hours": hours,
         "max_id": int(mx), "id_floor": int(lo)}

    cur.execute(f"""SELECT COUNT(*) FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')""")
    d["resolved_rows"] = int(cur.fetchone()[0])

    # one pass: the deduped pick set
    cur.execute(f"""
      SELECT COALESCE(asset_class,'(unknown)') cls, symbol, direction, source_system, status,
             MAX(CASE WHEN {PNL_OK} THEN pnl_pct END) pnl, MAX(created_at) ts
      FROM at_local_picks
      WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
      GROUP BY 1, {KEY}, status""")
    picks = [dict(cls=r[0], symbol=r[1], direction=r[2], source=r[3], status=r[4],
                  pnl=(float(r[5]) if r[5] is not None else None), ts=str(r[6])[:16])
             for r in cur.fetchall()]
    d["unique_picks"] = len(picks)
    d["duplicate_share_pct"] = round(100.0 * (d["resolved_rows"] - len(picks)) / max(1, d["resolved_rows"]), 1)

    by = {}
    for p in picks:
        by.setdefault(p["cls"], []).append(p)
    classes = []
    for cls, ps in by.items():
        n = len(ps)
        won = sum(1 for p in ps if p["status"] == "WON")
        lost = sum(1 for p in ps if p["status"] == "LOST")
        vals = [p["pnl"] for p in ps if p["pnl"] is not None]
        classes.append(dict(
            asset_class=cls, unique_picks=n, won=won, lost=lost,
            win_pct=round(100.0 * won / max(1, n), 1),
            mean_pct=(round(sum(vals) / len(vals), 3) if vals else None),
            median_pct=(round(statistics.median(vals), 3) if vals else None),
            with_numbers=len(vals), number_share_pct=round(100.0 * len(vals) / max(1, n), 1),
            best=(round(max(vals), 3) if vals else None),
            worst=(round(min(vals), 3) if vals else None)))
    classes.sort(key=lambda c: -c["unique_picks"])
    d["per_class"] = classes

    top = {}
    for c in classes[:10]:
        cand = [p for p in by[c["asset_class"]] if p["pnl"] is not None and p["status"] in ("WON", "LOST")]
        cand.sort(key=lambda p: -p["pnl"])
        top[c["asset_class"]] = [{k: p[k] for k in ("symbol", "direction", "source", "status", "pnl", "ts")}
                                 for p in cand[:5]]
    d["top_closed"] = top

    cur.execute(f"""SELECT COUNT(*) FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
                    AND (entry_price IS NULL OR take_profit IS NULL OR stop_loss IS NULL)""")
    d["resolved_missing_tpsl"] = int(cur.fetchone()[0])
    cur.execute(f"""SELECT COUNT(*) FROM at_local_picks WHERE id>={lo} AND direction='LONG'
                    AND entry_price>0 AND stop_loss IS NOT NULL AND stop_loss>=entry_price""")
    d["long_bad_stop"] = int(cur.fetchone()[0])
    cur.execute(f"""SELECT COUNT(*) FROM at_local_picks WHERE id>={lo} AND direction='SHORT'
                    AND entry_price>0 AND stop_loss IS NOT NULL AND stop_loss<=entry_price""")
    d["short_bad_stop"] = int(cur.fetchone()[0])
    cur.execute(f"""SELECT COALESCE(exit_reason,'(none)'), COUNT(*) FROM at_local_picks
                    WHERE id>={lo} AND status IN ('WON','LOST') GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
    d["exit_reasons"] = {str(r[0]): int(r[1]) for r in cur.fetchall()}
    return d


def sec(d):
    rows = ""
    for c in d["per_class"]:
        m = "&mdash;" if c["mean_pct"] is None else f'{c["mean_pct"]:+.3f}%'
        md = "&mdash;" if c["median_pct"] is None else f'{c["median_pct"]:+.3f}%'
        rows += (f'<tr><td><b>{c["asset_class"]}</b></td><td class="num">{c["unique_picks"]:,}</td>'
                 f'<td class="num">{c["won"]:,} / {c["lost"]:,}</td><td class="num">{c["win_pct"]:.1f}%</td>'
                 f'<td class="num">{m}</td><td class="num">{md}</td>'
                 f'<td class="num">{c["with_numbers"]:,} ({c["number_share_pct"]:.0f}%)</td></tr>')
    blocks = ""
    for cls, picks in d["top_closed"].items():
        if not picks:
            continue
        body = "".join(
            f'<tr><td><code>{p["symbol"]}</code></td><td>{p["direction"] or ""}</td>'
            f'<td><span class="tag {"t-pass" if p["status"]=="WON" else "t-dead"}">{p["status"]}</span></td>'
            f'<td class="num">{p["pnl"]:+.3f}%</td><td>{p["ts"]}</td><td><code>{p["source"]}</code></td></tr>'
            for p in picks)
        blocks += (f'<h3>{cls} &mdash; best closed picks</h3><table><thead><tr><th>Symbol</th><th>Dir</th>'
                   f'<th>Result</th><th class="num">PnL</th><th>Closed (UTC)</th><th>Source</th></tr></thead>'
                   f'<tbody>{body}</tbody></table>')
    er = ", ".join(f'{k} {v:,}' for k, v in list(d["exit_reasons"].items())[:5])
    return f"""<!-- ASSETCLASS:START -->
<section id="asset-class">
  <h2>Performance by asset class &mdash; de-duplicated</h2>
  <p class="lede"><code>at_local_picks</code>, last {d["window_hours"]}h. Generated <b>{d["generated_at"]}</b>.</p>

  <div class="callout" style="border:1px solid #7a2f2f;border-left:4px solid #d9534f;padding:14px 18px;margin:18px 0;background:rgba(217,83,79,.07)">
    <b>The correction that changes every number below.</b> {d["resolved_rows"]:,} rows carry a resolved
    status in this window but they are only <b>{d["unique_picks"]:,} unique picks</b> &mdash;
    <b>{d["duplicate_share_pct"]:.1f}%</b> are the same pick re-emitted by its scanner. Win rates computed
    on row counts overstate every strategy that fires on a schedule.
  </div>

  <table>
    <thead><tr><th>Asset class</th><th class="num">Unique picks</th><th class="num">W / L</th>
        <th class="num">Win</th><th class="num">Mean PnL</th><th class="num">Median PnL</th>
        <th class="num">With a real number</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>

  <p style="color:#9aa7b4;font-size:14px;margin-top:10px">
    Integrity: <b>{d["resolved_missing_tpsl"]:,}</b> resolved rows have no entry/TP/SL (cannot be re-derived),
    <b>{d["long_bad_stop"]:,}</b> LONG rows have a stop at/above entry, <b>{d["short_bad_stop"]:,}</b> SHORT
    rows a stop at/below it. Exit reasons: {er}.
  </p>

  {blocks}
</section>
<!-- ASSETCLASS:END -->"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()
    c, cur = connect()
    d = collect(cur, a.hours)
    c.close()
    p = os.path.join(a.repo, "docs", "data", "asset_class_perf.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(d, open(p, "w"), indent=1, default=str)
    print("wrote", p, os.path.getsize(p), "B")
    idx = os.path.join(a.repo, "docs", "index.html")
    html = open(idx, encoding="utf-8").read()
    body = sec(d)
    if "<!-- ASSETCLASS:START -->" in html:
        html = re.sub(r"<!-- ASSETCLASS:START -->.*?<!-- ASSETCLASS:END -->", body, html, flags=re.S)
        act = "replaced"
    else:
        anchor = "<!-- LATEST:START -->"
        html = html.replace(anchor, body + "\n" + anchor, 1) if anchor in html else html.replace("</header>", "</header>\n" + body, 1)
        act = "inserted"
    open(idx, "w", encoding="utf-8").write(html)
    print(act, "asset-class section in", idx, os.path.getsize(idx), "B")
    for x in d["per_class"][:8]:
        print(f'  {x["asset_class"]:<10} uniq={x["unique_picks"]:<6} win={x["win_pct"]:5.1f}% mean={x["mean_pct"]} median={x["median_pct"]}')


if __name__ == "__main__":
    main()
