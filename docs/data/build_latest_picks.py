#!/usr/bin/env python3
"""Build docs/data/latest_picks.json and the 'Latest picks & results' section.

Source of truth: ejaguiar1_stocks.at_local_picks - the only table still being
written to. trading_picks_v2 froze on 2026-06-05 and mercury2 stopped scanning
on 2026-11-26, so both are reported as frozen rather than silently averaged in.

Why the window is id-based: `created_at` has no index on a 76M-row table, so
`WHERE created_at >= NOW() - INTERVAL ...` triggers a full scan and is killed by
max_execution_time. Ids are monotonic with time, so a binary search on `id`
finds the boundary in ~20 primary-key lookups.

Usage: DB_PASS=... python3 build_latest_picks.py --repo /path/to/repo
"""
import argparse, datetime, os, re, sys

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")

NOW = datetime.datetime.now(datetime.timezone.utc)
RESOLVED = ("WON", "LOST", "EXPIRED")


def connect():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    return pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                           user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                           password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"))


def id_floor(cur, hours):
    """Smallest id whose created_at is within `hours` of now (binary search on the PK)."""
    cur.execute("SELECT MAX(id) FROM at_local_picks")
    hi = cur.fetchone()[0]
    cutoff = NOW.replace(tzinfo=None) - datetime.timedelta(hours=hours)
    cur.execute("SELECT created_at FROM at_local_picks WHERE id <= %s ORDER BY id DESC LIMIT 1", (hi,))
    newest = cur.fetchone()[0]
    if newest is None or newest < cutoff:
        return hi + 1                       # nothing in the window
    lo, best = 0, hi
    for _ in range(30):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        cur.execute("SELECT created_at FROM at_local_picks WHERE id >= %s ORDER BY id ASC LIMIT 1", (mid,))
        row = cur.fetchone()
        if row is None:
            hi = mid
            continue
        if row[0] and row[0] >= cutoff:
            best, hi = mid, mid
        else:
            lo = mid
    return best


def collect(cur):
    cur.execute("SET SESSION max_execution_time=25000")
    floor24 = id_floor(cur, 24)
    floor1 = id_floor(cur, 1)

    d = {"generated_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_hours": 24}

    # overall status mix in the 24h window
    cur.execute("""SELECT COALESCE(status,'(null)'), COUNT(*) FROM at_local_picks
                   WHERE id >= %s GROUP BY 1 ORDER BY 2 DESC""", (floor24,))
    d["status_mix"] = {r[0]: int(r[1]) for r in cur.fetchall()}

    # per-source within 24h: volume, resolved count, W/L, mean pnl over resolved
    cur.execute("""SELECT source_system,
                          COUNT(*),
                          SUM(status IN ('WON','LOST','EXPIRED')),
                          SUM(status='WON'), SUM(status='LOST'),
                          ROUND(AVG(CASE WHEN status IN ('WON','LOST','EXPIRED') AND pnl_pct IS NOT NULL
                                         AND ABS(pnl_pct) <= 50 AND pnl_pct <> 0 THEN pnl_pct END), 3),
                          SUM(status IN ('WON','LOST','EXPIRED') AND (pnl_pct IS NULL OR pnl_pct = 0))
                   FROM at_local_picks WHERE id >= %s
                   GROUP BY 1 ORDER BY 2 DESC LIMIT 12""", (floor24,))
    d["by_source"] = [dict(source=r[0], picks=int(r[1]), resolved=int(r[2] or 0),
                           won=int(r[3] or 0), lost=int(r[4] or 0),
                           mean_pct=(float(r[5]) if r[5] is not None else None),
                           no_pnl=int(r[6] or 0)) for r in cur.fetchall()]

    # newest resolved picks (real results, excluding the ACTIVE mass)
    cur.execute("""SELECT created_at, symbol, direction, status, pnl_pct, source_system
                   FROM at_local_picks
                   WHERE id >= %s AND status IN ('WON','LOST','EXPIRED')
                   ORDER BY id DESC LIMIT 20""", (floor24,))
    d["latest_resolved"] = [dict(at=r[0].strftime("%Y-%m-%d %H:%M") if r[0] else None,
                                 symbol=r[1], direction=r[2], status=r[3],
                                 pnl_pct=(float(r[4]) if r[4] is not None else None),
                                 source=r[5]) for r in cur.fetchall()]

    # newest picks of any status (what the engines are emitting right now)
    cur.execute("""SELECT created_at, symbol, direction, status, pnl_pct, source_system
                   FROM at_local_picks WHERE id >= %s ORDER BY id DESC LIMIT 12""", (floor1,))
    d["latest_emitted"] = [dict(at=r[0].strftime("%H:%M") if r[0] else None, symbol=r[1],
                                direction=r[2], status=r[3],
                                pnl_pct=(float(r[4]) if r[4] is not None else None),
                                source=r[5]) for r in cur.fetchall()]

    # frozen stores, stated as facts rather than averaged in
    frozen = {}
    for tbl, col in (("trading_picks_v2", "signal_timestamp"), ("trading_picks", "created_at")):
        try:
            cur.execute(f"SELECT MAX({col}) FROM {tbl}")
            v = cur.fetchone()[0]
            frozen[tbl] = v.strftime("%Y-%m-%d") if v else None
        except Exception:
            frozen[tbl] = None
    d["frozen_stores"] = frozen
    return d


def fmt_pct(v):
    return "&mdash;" if v is None else f"{v:+.3f}%"


def html_section(d):
    mix = d["status_mix"]
    resolved = sum(mix.get(s, 0) for s in RESOLVED)
    won = mix.get("WON", 0)
    win_rt = 100.0 * won / resolved if resolved else 0.0
    src_rows = "".join(
        (f'<tr><td><code>{r["source"]}</code></td><td class="num">{r["picks"]:,}</td>'
         f'<td class="num">{r["resolved"]:,}</td><td class="num">{r["won"]:,} / {r["lost"]:,}</td>'
         f'<td class="num">{100.0*r["won"]/r["resolved"]:.1f}%</td>'
         f'<td class="num">{fmt_pct(r["mean_pct"])}</td>'
         f'<td class="num">{r["no_pnl"]:,}</td></tr>')
        if r["resolved"] else
        (f'<tr><td><code>{r["source"]}</code></td><td class="num">{r["picks"]:,}</td>'
         f'<td class="num">0</td><td class="num">&mdash;</td><td class="num">&mdash;</td>'
         f'<td class="num">&mdash;</td><td class="num">{r["no_pnl"]:,}</td></tr>')
        for r in d["by_source"])

    res_rows = "".join(
        f'<tr><td>{p["at"] or "&mdash;"}</td><td><code>{p["symbol"]}</code></td>'
        f'<td>{p["direction"] or ""}</td>'
        f'<td><span class="tag {"t-pass" if p["status"]=="WON" else "t-dead"}">{p["status"]}</span></td>'
        f'<td class="num">{fmt_pct(p["pnl_pct"])}</td><td><code>{p["source"]}</code></td></tr>'
        for p in d["latest_resolved"]) or '<tr><td colspan="6">No resolved picks in the last 24h.</td></tr>'

    emit = ", ".join(f'{p["symbol"]} {p["direction"] or ""}'.strip() for p in d["latest_emitted"][:8])
    fs = d["frozen_stores"]
    return f"""<!-- LATEST:START -->
<section id="latest">
  <h2>Latest picks &amp; their results</h2>
  <p class="lede">Everything below is read from <code>at_local_picks</code> &mdash; the only pick table
  still being written to &mdash; over the last <b>{d["window_hours"]}h</b>. Regenerated at
  <b>{d["generated_at"]}</b>.</p>

  <table>
    <thead><tr><th>Source</th><th class="num">Picks</th><th class="num">Resolved</th>
        <th class="num">W / L</th><th class="num">Win rate</th><th class="num">Mean PnL</th>
        <th class="num">Resolved w/o PnL</th></tr></thead>
    <tbody>{src_rows}</tbody>
  </table>
  <p style="color:#9aa7b4;font-size:14px;margin-top:10px">
    Window totals: <b>{sum(mix.values()):,}</b> picks &mdash; <b>{resolved:,}</b> resolved
    ({won:,} W / {mix.get("LOST",0):,} L, <b>{win_rt:.1f}%</b> win),
    <b>{mix.get("ACTIVE",0)+mix.get("OPEN",0):,}</b> still open,
    <b>{mix.get("EXPIRED",0):,}</b> expired. Emitting right now: {emit or "&mdash;"}.
  </p>

  <h3>Most recent resolved picks</h3>
  <table>
    <thead><tr><th>Time (UTC)</th><th>Symbol</th><th>Dir</th><th>Result</th><th class="num">PnL</th><th>Source</th></tr></thead>
    <tbody>{res_rows}</tbody>
  </table>

  <div class="callout" style="border:1px solid #5a4a1f;border-left:4px solid #e0b23a;padding:14px 18px;margin:18px 0;background:rgba(224,178,58,.07)">
    <b>Two things this section deliberately does not hide.</b>
    (1) Most rows in the window are <b>unresolved by design</b> &mdash; the <code>coinglass</code> scanner writes
    <code>ACTIVE</code> rows that never get a result, so they are counted separately and kept out of every
    win rate. (2) <b>"Resolved w/o PnL"</b> is the live resolution gap: picks marked WON/LOST whose PnL is
    NULL or exactly 0, because the column is <code>NOT NULL DEFAULT 0</code>. A WON with no number is not
    evidence of profit.
    <br><br>
    <b>Frozen stores.</b> <code>trading_picks_v2</code> stopped at
    <b>{fs.get("trading_picks_v2") or "?"}</b> and <code>trading_picks</code> at
    <b>{fs.get("trading_picks") or "?"}</b>. Neither receives new picks, so nothing in this section is
    averaged across them.
  </div>
</section>
<!-- LATEST:END -->"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    c = connect(); cur = c.cursor()
    d = collect(cur); c.close()

    p = os.path.join(a.repo, "docs", "data", "latest_picks.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    import json
    json.dump(d, open(p, "w"), indent=1, default=str)
    print("wrote", p, os.path.getsize(p), "B")

    idx = os.path.join(a.repo, "docs", "index.html")
    html = open(idx, encoding="utf-8").read()
    sec = html_section(d)
    if "<!-- LATEST:START -->" in html:
        html = re.sub(r"<!-- LATEST:START -->.*?<!-- LATEST:END -->", sec, html, flags=re.S)
        action = "replaced"
    else:
        anchor = "<!-- SUMMARY:START -->"
        html = html.replace(anchor, sec + "\n" + anchor, 1) if anchor in html else html.replace("</header>", "</header>\n" + sec, 1)
        action = "inserted"
    open(idx, "w", encoding="utf-8").write(html)
    print(action, "latest section in", idx, os.path.getsize(idx), "B")


if __name__ == "__main__":
    main()
