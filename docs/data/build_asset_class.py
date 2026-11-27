#!/usr/bin/env python3
"""Per-asset-class performance + the best closed picks per class, from at_local_picks.

Two corrections this makes to every earlier published win rate:
  1. DUPLICATES. The engines re-emit the same pick hourly; in a 24h window 78,412
     "resolved" rows collapse to 2,846 unique picks (96.4% re-emission). Counting
     rows over-counts winners and losers alike. Everything here is de-duplicated on
     the pick identity (symbol, direction, entry, TP, SL, source).
  2. LABELS WITHOUT NUMBERS. Rows marked WON/LOST with NULL/0 pnl are excluded from
     means; the count that remain is stated rather than silently averaged as flat.

Writes docs/data/asset_class_perf.json and a <section id="asset-class"> block.

Usage: DB_PASS=... python3 build_asset_class.py --repo /path/to/repo
"""
import argparse, datetime, json, os, re, sys

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
    cur = c.cursor()
    cur.execute("SET SESSION max_execution_time=25000")
    return c, cur


def window(cur, hours):
    cur.execute("SELECT MAX(id) FROM at_local_picks"); mx = cur.fetchone()[0]
    return mx, mx - (3_000_000 if hours <= 24 else 25_000_000)


def collect(cur, hours):
    mx, lo = window(cur, hours)
    d = {"generated_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_hours": hours,
         "max_id": int(mx), "id_floor": int(lo)}

    cur.execute(f"SELECT COUNT(*) FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')")
    d["resolved_rows"] = int(cur.fetchone()[0])
    cur.execute(f"""SELECT COUNT(*) FROM (SELECT 1 FROM at_local_picks
                    WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
                    GROUP BY {KEY}) t""")
    d["unique_picks"] = int(cur.fetchone()[0])
    d["duplicate_share_pct"] = round(100.0 * (d["resolved_rows"] - d["unique_picks"]) / max(1, d["resolved_rows"]), 1)

    # deduped per class
    cur.execute(f"""
      SELECT asset_class, n, w, l, mean_pnl, numbered FROM (
        SELECT COALESCE(asset_class,'(unknown)') asset_class, COUNT(*) n,
               SUM(won) w, SUM(lost) l, AVG(pnl) mean_pnl, COUNT(pnl) numbered,
               SUBSTRING_INDEX(GROUP_CONCAT(pnl ORDER BY pnl SEPARATOR ','), ',', 1) ignored
        FROM (SELECT COALESCE(asset_class,'(unknown)') asset_class, {KEY},
                     MAX(status='WON') won, MAX(status='LOST') lost,
                     MAX(CASE WHEN {PNL_OK} THEN pnl_pct END) pnl
              FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
              GROUP BY 1, {KEY}) t0
        GROUP BY 1) t1 ORDER BY n DESC""")
    rows = cur.fetchall()
    classes = []
    for cls, n, w, l, mean_pnl, numbered in rows:
        n, w, l, numbered = int(n), int(w or 0), int(l or 0), int(numbered or 0)
        cls_c = str(cls)
        # median via a second, bounded query per class
        cur.execute(f"""
          SELECT AVG(pnl) FROM (
            SELECT pnl FROM (
              SELECT MAX(CASE WHEN {PNL_OK} THEN pnl_pct END) pnl
              FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
                AND COALESCE(asset_class,'(unknown)')=%s
              GROUP BY {KEY}) a
            WHERE pnl IS NOT NULL
            ORDER BY pnl
            LIMIT 2 OFFSET (SELECT GREATEST(0, FLOOR(COUNT(*)/2)-1) FROM (
              SELECT MAX(CASE WHEN {PNL_OK} THEN pnl_pct END) pnl2
              FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST','EXPIRED')
                AND COALESCE(asset_class,'(unknown)')=%s
              GROUP BY {KEY}) b WHERE pnl2 IS NOT NULL)) m""", (cls_c, cls_c))
        med = cur.fetchone()[0]
        classes.append(dict(asset_class=cls_c, unique_picks=n, won=w, lost=l,
                            win_pct=round(100.0 * w / max(1, n), 1),
                            mean_pct=(round(float(mean_pnl), 3) if mean_pnl is not None else None),
                            median_pct=(round(float(med), 3) if med is not None else None),
                            with_numbers=numbered,
                            number_share_pct=round(100.0 * numbered / max(1, n), 1)))
    d["per_class"] = classes

    # top closed picks per class (deduped, real numbers only)
    top = {}
    for c_ in classes[:10]:
        cur.execute(f"""
          SELECT * FROM (
            SELECT symbol, direction, source_system, status, pnl_pct, ts,
                   ROW_NUMBER() OVER (ORDER BY pnl_pct DESC) rn FROM (
              SELECT symbol, direction, source_system, status,
                     MAX(CASE WHEN {PNL_OK} THEN pnl_pct END) pnl_pct, MAX(created_at) ts
              FROM at_local_picks WHERE id>={lo} AND status IN ('WON','LOST')
                AND COALESCE(asset_class,'(unknown)')=%s
              GROUP BY {KEY}, status) a
            WHERE pnl_pct IS NOT NULL) b WHERE rn <= 5""", (c_["asset_class"],))
        top[c_["asset_class"]] = [dict(symbol=r[0], direction=r[1], source=r[2], status=r[3],
                                       pnl_pct=round(float(r[4]), 3), at=str(r[5])[:16])
                                  for r in cur.fetchall()]
    d["top_closed"] = top

    # integrity
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
    rows = "".join(
        f'<tr><td><b>{c["asset_class"]}</b></td><td class="num">{c["unique_picks"]:,}</td>'
        f'<td class="num">{c["won"]:,} / {c["lost"]:,}</td>'
        f'<td class="num">{c["win_pct"]:.1f}%</td>'
        f'<td class="num">{"&mdash;" if c["mean_pct"] is None else f"{c[chr(34)+chr(34)] if False else ""}"}</td></tr>' for c in [])
    rows = ""
    for c in d["per_class"]:
        mean_txt = "&mdash;" if c["mean_pct"] is None else f'{c["mean_pct"]:+.3f}%'
        med_txt = "&mdash;" if c["median_pct"] is None else f'{c["median_pct"]:+.3f}%'
        rows += (f'<tr><td><b>{c["asset_class"]}</b></td><td class="num">{c["unique_picks"]:,}</td>'
                 f'<td class="num">{c["won"]:,} / {c["lost"]:,}</td><td class="num">{c["win_pct"]:.1f}%</td>'
                 f'<td class="num">{mean_txt}</td><td class="num">{med_txt}</td>'
                 f'<td class="num">{c["with_numbers"]:,} ({c["number_share_pct"]:.0f}%)</td></tr>')
    blocks = ""
    for cls, picks in d["top_closed"].items():
        if not picks:
            continue
        body = "".join(
            f'<tr><td><code>{p["symbol"]}</code></td><td>{p["direction"] or ""}</td>'
            f'<td><span class="tag {"t-pass" if p["status"]=="WON" else "t-dead"}">{p["status"]}</span></td>'
            f'<td class="num">{p["pnl_pct"]:+.3f}%</td><td>{p["at"]}</td><td><code>{p["source"]}</code></td></tr>'
            for p in picks)
        blocks += (f'<h3>{cls} &mdash; best closed</h3><table><thead><tr><th>Symbol</th><th>Dir</th>'
                   f'<th>Result</th><th class="num">PnL</th><th>Closed (UTC)</th><th>Source</th></tr></thead>'
                   f'<tbody>{body}</tbody></table>')
    er = ", ".join(f'{k} {v:,}' for k, v in list(d["exit_reasons"].items())[:5])
    return f"""<!-- ASSETCLASS:START -->
<section id="asset-class">
  <h2>Performance by asset class &mdash; de-duplicated</h2>
  <p class="lede">Source: <code>at_local_picks</code>, last {d["window_hours"]}h. Generated
  <b>{d["generated_at"]}</b>.</p>

  <div class="callout" style="border:1px solid #7a2f2f;border-left:4px solid #d9534f;padding:14px 18px;margin:18px 0;background:rgba(217,83,79,.07)">
    <b>The correction that matters.</b> {d["resolved_rows"]:,} rows carry a resolved status in this window,
    but they are only <b>{d["unique_picks"]:,} unique picks</b> &mdash;
    <b>{d["duplicate_share_pct"]:.1f}% are the same pick re-emitted</b> by its scanner. Every count,
    win rate and mean below is computed on unique picks; quoting row counts overstates every strategy
    that fires on a schedule.
  </div>

  <table>
    <thead><tr><th>Asset class</th><th class="num">Unique picks</th><th class="num">W / L</th>
        <th class="num">Win</th><th class="num">Mean PnL</th><th class="num">Median PnL</th>
        <th class="num">With a real number</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>

  <p style="color:#9aa7b4;font-size:14px;margin-top:10px">
    Integrity of this window: <b>{d["resolved_missing_tpsl"]:,}</b> resolved rows have no entry/TP/SL at all
    (they can never be re-derived), <b>{d["long_bad_stop"]:,}</b> LONG rows have a stop at or above entry and
    <b>{d["short_bad_stop"]:,}</b> SHORT rows a stop at or below it. Exit reasons behind the resolved rows:
    {er}.
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
    for c_ in d["per_class"][:6]:
        print(f'  {c_["asset_class"]:<10} uniq={c_["unique_picks"]:<6} win={c_["win_pct"]:5.1f}% mean={c_["mean_pct"]}')


if __name__ == "__main__":
    main()
