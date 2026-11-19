# Inventory — Audit pages

Probed 2026-11-19 against `https://findtorontoevents.ca/`:

| Route | HTTP | Size | Status |
|---|---|---|---|
| `/audit` | 200 | 1,437,176 B | Live, canonical dashboard (site mirror = `audit_dashboard/index.html`, 1.4 MB; `template.html` 1.3 MB) |
| `/audit2` | **404** | 992 B | **Dead / superseded.** No `audit2.html` exists anywhere in the repo. The only surviving artifact is the root `score_audit2.py` helper; there is no live page and no active payload. |
| `/audit3` | 200 | 36,331 B | Live, active "Quant Kill Tribunal" ledger page (`audit_dashboard/audit3.html`, mtime 2026-11-19 05:37). |

The user asked to review "audit, audit2, audit3 (whichever has data)". **audit2 has no
data** — it is gone. The data-bearing surfaces are `/audit` and `/audit3`.

## What each live page actually serves

- **`/audit` (`audit_dashboard/index.html`)** — the main dashboard. Heavy (1.4 MB) with
  many tiles: summary cards, kill-switch card, tournament/leaderboard framing, money-ready
  bridge, theory tracker (H-020…H-025), per-class PF/WR panels (two sets per class),
  freshness. Several tiles are stale or misleading (see `02_FINDINGS/data_quality_resolver.md`).
- **`/audit3` (`audit3.html`)** — the strict ledger: Wilson CIs, one-sided binomial vs 50%,
  2,000-resample bootstrap net-expectancy CIs after per-class slippage, BH-FDR,
  split-half stability, concentration caps, kill rule (`net-CI entirely < 0 AND BH harm q
  ≤ 0.10`). This is the best artifact in the repo. It shows **0 PROVEN / 1 CANDIDATE**.
- **`audit_page.html`** — a *different*, stale (May 25) page with 2 tabs (Overview empty,
  Grok picks) referencing `data/grok_top_picks.json`. It is effectively orphaned dead
  surface and is not the live `/audit`.
