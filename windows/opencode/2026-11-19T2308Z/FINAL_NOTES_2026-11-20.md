# Final notes — Windows / opencode — 2026-11-20T02:20Z

**Agent:** opencode (Windows, desktop-081g9oh)
**Seat:** `inbox/desktop-081g9oh/findtorontoevents_antigravity-ca/opencode`
**Snapshot:** 2026-11-20T02:20Z
**findtorontoevents main:** `ec387e42b561`
**AGENT_FOLDERFRAMEWORK main:** `269f121`
**Isolated review packet:** `antigravity_review_Nov192026` → `windows/opencode/2026-11-19T2308Z/` (PR #1)

## 1. Live state

- `/audit`, `/audit2`, `/audit3`: HTTP 200.
- `audit3_ledger.json` generated **2026-11-20T01:57:23Z**, provenance `b5363b282409b564`.
- 8,769 scored of 16,372 closed (coverage ~53.6%); 0 PROVEN / 0 CANDIDATE / 59 WEAK / 8 KILL.
- Selection alpha **−0.2681%/trade**, CI [−0.5029, −0.0178].
- Forward: 430 rows, only H-119; `POD-EQUITY-BREAKOUT` = **0**.
- `/audit` money-ready: money=[], watch=[COMMODITY].
- **Nothing is money-ready.** Cheap beta remains the only justifiable real-money allocation.

## 2. Corrections since `00_SUMMARY.md`

### 2.1 B1 is not an emitter bug — the pod names never existed

Kilo's DB evidence (`docs/B1_POD_STRATEGY_NAMES_FINDING_2026-11-20.md`) shows the four
`POD-EQUITY-BREAKOUT` strategies (`donchian-stock-breakout`, `rs-breakout-scout`,
`vol-contraction-scout`, `adx-trend-scout`) have **zero rows** in `trading_picks`,
`at_pick_outcomes`, and `at_signal_outcomes`. They were never emitted; the names exist only in
the audit3 payload/backtest namespace.

**This qualifies my earlier EQUITY recommendation.** EQUITY is still the only class with a
positive point estimate, but the specific confirmatory cell cannot accrue forward evidence
because the emitter does not exist. A real-money path requires either:

- **A (recommended):** a dated pre-registration amendment to real emitters
  (`donchian_breakout_scalp`, `proven_donchian_adx_trend`, `adx_momentum`), with the forward
  clock restarting at the amendment — legitimate only because zero forward rows accrued under
  the old names; or
- **B:** implement the four exact strategies (more work; thesis already covered).

Also add an **`emitted: true/false`** flag to every cell, computed from
`strategy EXISTS in trading_picks`, and run it for all pods. Audit3 must never display a
confirmatory cell for a strategy no live system emits.

### 2.2 Zero CANDIDATE is still not DSR-driven

Reason counts on the 21:02Z ledger: n<20 = 292, split-half = 41, win-rate = 43,
profit-factor = 14, single-symbol = 5, KILL = 8; zero DSR/BH/alpha/forward reasons.
The queue is empty at the early floors, not from the 658 floor.

### 2.3 TAA is drawdown control, not excess return

Lag-1 result: Sharpe 0.82 vs SPY 0.69, MDD −20.9% vs −52.9%, but CAGR 8.9% vs 10.8%.
Keep it as a suitability sleeve, not an alpha claim.

### 2.4 Buffy's $2k critique is correct

The 20% rotation sleeve points at the weakest evidence (ETF class PF 1.005, net +0.006%/trade,
CI [−0.235, +0.239], WEAK; 0.6 bp expectancy vs ~5 bp cost; 2× stress fails in every class).
Use **90/0/10 or 100% core** until the rotation arm accrues n≥200 forward; the $200 sandbox
stays paper.

## 3. Windows COMS bug found and fixed

A peer message containing U+2212 crashed `coms.ps1 check` under PS 5.1:
`UnicodeEncodeError: 'charmap' codec can't encode character '\u2212'`.
Fix: force `PYTHONIOENCODING=utf-8` and UTF-8 console/output encoding for every Python child.
Verified: `unicode_errors=0` on the exact message that triggered it.
PR: https://github.com/eltonaguiar/AGENT_FOLDERFRAMEWORK/pull/4 (code; review before merge).

## 4. Merge / backup state

- **Merged this session (Hermes report + verified on main):** #972, #977, #969, #968,
  #903, #894, #872.
- **Open / blocked:** #965 (`feat/audit3-p0-p1-correctness`) — 15 `alpha_engine` conflicts,
  stale ledger, superseded by main; **do not merge wholesale**. #983 (restore CI Tests) open.
- Kilo's `feat/kilo-todo-sweep-clean` (@07b0204, 200 tests) is clean off main and ready once
  #965 is reconciled.
- **OpenCode PRs:** #3 (framework review docs), #1 (isolated packet), #4 (UTF-8 fix).
- **Archive tags:** `archive/2026-11-19/{review-windows, pr965, audit2-3-p0-p1,
  buffy-money-maker, buffy-findings, audit2-3-review}`.
- **Quarantine:** `feat/audit-review-organization-2026-11-19` contains a credential commit.
  Rotate, rewrite, cherry-pick non-secret work; do not merge/tag.
- **Next merge candidate:** `fix/audit2-3-p0-p1` after CI.

## 5. Roll call

| Agent | Seat | Status |
|---|---|---|
| deepseek-flash (Linux) | `review-main/deepseek-v4-flash` | ACK pending |
| Kilo (ext/Linux) | `auditpage/kilo`, `vanilla-handsaw/kilo`, `findtorontoevents-ca/kilo` | active |
| FreeBuff (Linux) | none | **unregistered** — register + ACK |
| GitHub Copilot (VS Code) | `copilot-cli-moneyresearch` (CLI) | confirm IDE seat + ACK |
| Google Swarm (Linux) | none | **unregistered** — register + ACK |
| Hermes (Windows) | `communication/hermes-deepseek-flash` | active |
| OpenCode (Windows) | this seat | active |
| Buffy (Linux) | `findtorontoevents-ca/buffy` | active; confirm FreeBuff identity |
| grok-4-7 / deepmind-antigravity | `auditpage/*` | ACK pending |

## 6. Recommendation

1. **No real money** in any strategy sleeve. Keep cheap beta; paper-only until a real pod
   accrues n≥100 forward and passes 2× cost + benchmark.
2. **Decide A or B for the equity pod today.** Prefer A (dated amendment to real emitters) and
   add the `emitted` flag for every pod.
3. Do not merge #965 wholesale; open a fresh branch from current main for unique tests/fixes.
4. Merge the UTF-8 fix after review; it is low-risk and unblocks Windows check/listen.
5. Rotate the quarantined credential and remove the branch/history.

## 7. Verify

```powershell
# live
Invoke-RestMethod https://findtorontoevents.ca/audit3/audit3_ledger.json |
  Select-Object generated_at,@{n='p';e={$_.summary.n_proven}},@{n='c';e={$_.summary.n_candidate}}
# review packet
git clone https://github.com/eltonaguiar/antigravity_review_Nov192026
# framework review
git fetch origin review/windows-2026-11-19
```

*Review artifact, not investment advice.*
