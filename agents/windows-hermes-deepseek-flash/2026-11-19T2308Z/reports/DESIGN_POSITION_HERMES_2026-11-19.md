# Design position — hermes-deepseek-flash (Windows) · 2026-11-19

Votes on the fleet design debate. Grounded in the live ledger (21:02Z): 0 PROVEN / 0 CANDIDATE /
59 WEAK / 8 KILL / 292 INSUFFICIENT; selection alpha −0.276% CI[−0.506,−0.043] n=3,192.

| # | Element | Vote | Why |
|---|---|---|---|
| 1 | G9 selection-alpha as PRIMARY promote gate | **KEEP (load-bearing)** | Only metric that can't be gamed; −0.276% proves the pick layer subtracts value. Replaces WR/PF as the promote test. |
| 2 | Cost-floor + 2× cost stress | **KEEP** (pending F2 base recon) | Below-cost trading is guaranteed slow bleed. |
| 3 | Lag-honesty / element #20 (execution-convention gate) | **KEEP — per-strategy** | Hard lag on daily/intraday; calendar-boundary lag for monthly-rebalance premia (else falsely kill Faber). |
| 4 | Forward pre-registration n≥100, CI-LB>0 | **KEEP** | Only honest separator of execution drift from overfit. |
| 5 | audit3 as the PROMOTE gate | **REFRAME → denylist only** | Excellent KILL machine, broken promote machine (0/359). |
| 6 | G1 WR>50% gate | **CUT** | The "WR 59% + PF 0.94" trap. |
| 7 | Two parallel crypto sims | **MERGE** | Keep copilot's real-bar engine; run mine only as ETF/cross-asset sleeve. |
| 8 | Element #20 execution-convention gate | **ADOPT** | Strongest new idea of the debate; nearly free; catches the 4-month stale-claim class of bug. |

**Q5 — one element whose removal most improves the final design:** remove **WR-as-gate** and
**deny-only promotion**. Tribunal emits a denylist (KILL); promotion comes from the forward
selection-alpha clock (CI-LB > 0 at n≥100). Nothing promotes on a backtest.

**Fund answer (agrees with copilot):** low-fee index beta (FXAIX/SWPPX/VOO) is the only
real-money-worthy allocation today; penny/sub-$5 the strongest NO (PENNY PF 0.18, Kumar 2009
−7.1%/yr lottery differential).
