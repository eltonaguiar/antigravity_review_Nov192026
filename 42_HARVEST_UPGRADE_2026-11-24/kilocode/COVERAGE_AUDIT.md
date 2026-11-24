# Coverage audit — every live pick surface

Checked 2026-11-24T11:25Z.

## /audit dashboard_data.json (26 MB, generated 10:03Z)

| Surface | Count | Status / action |
|---|---|---|
| picks.active | 13 | all OPEN |
| picks.active_raw | **4,210** | **562 OPEN**, 3,618 EXPIRED, 19 SL, 11 TP — ingest all 562 |
| picks.recent_closed | 3,500 | full closed population 15,063 |
| picks.ueps_kpi | present | ingest UEPS |
| picks.smart_picks | **0** | EMPTY producer |
| portfolios | 23 | ingest |
| leaderboard | 1,013 | ingest |
| predictions_leaderboard | 222 | ingest |
| consensus | object | ingest |
| analyst_leaderboard | **0 / 0** | BROKEN — HARVEST not joined |
| money_ready_verdicts | 11 classes | incl. MEME, PENNY_STOCK, CHEAP_STOCKS |
| smart_picks_by_asset | 8 classes | ingest |
| conflicts | 13 | store resolved direction |

## /audit3 audit3_ledger.json
- classes 7 (CRYPTO/COMMODITY KILL; EQUITY/ETF/FOREX/BOND WEAK; FUTURES INSUFFICIENT_N)
- cells 366 (68 tested, 0 proven); symbols/hypotheses/sleeves/segments present; forward_gate enforced.

## Other
- /audit2: 200 but RETIRED; exclude.
- /investments: portal, no single pick ledger.
- GitHub antigravity_review: HARVEST 71, best-picks 9, simulation synthetic, rating demo, DQ docs.
- GitHub findtorontoevents: dashboard_data + audit3 ledger + PRs #1018/#1067/#1046/#1003.

## Gaps
1. Ingest active_raw 562 open (not just 13), labelled by visibility/gate.
2. Fix smart_picks=[] and analyst bridge 0/0.
3. Add taxonomy: SPORTS, MEME, PENNY_STOCK, CHEAP_STOCKS, MUTUAL_FUND.
4. Store conflict resolution + risk events.
5. Exclude /audit2; no feed from /investments.
6. Run DQ_CHECKS.sql nightly.
