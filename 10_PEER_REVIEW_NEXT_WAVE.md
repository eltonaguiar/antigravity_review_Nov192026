# Peer Review — next wave (2026-11-19, evening) — Kilo, `universal-pisces`

**Reviewer:** Kilo, `universal-pisces` · **Date:** 2026-11-19
**Scope:** this reviews the newest peer deliverables landed since my earlier passes:

| New artifact | Owned by | What it is |
|---|---|---|
| `05_AUDIT2_SPEC.md` | peer | Curated audit2 content spec (candidate pods P1–P8, measures library, quotes, boring portfolio) |
| `05_KILO_REVIEW/PAGES_AUDIT2_AUDIT3.md` | Kilo/peer | Live split review of `/audit3` vs orphaned `/audit2` (v2) |
| `05_KILO_REVIEW/SWARM_AUDIT2_HISTORY.md` | Kilo/peer | Gemini-swarm "fix audit2" reconstruction + FTP-secret fix |
| `02_FINDINGS/peer_worktree_review.md` | peer | Independent review of `quant-audit`, copilot WIRED_IN, others |
| `05_KILO_REVIEW/FINDINGS_ROOT_CAUSE.md` | peer | F1–F7 root causes (reviewed in `08`) |

---

## 1. What I verified independently (not taken on trust)

| Peer claim | My re-check | Verdict |
|---|---|---|
| Crypto stop-fill overshoot ≈ 98.8% of class loss (planned 1.919% → realized 2.990%; +828pp vs −837.8pp) | `quant-audit…/03_ideas_ranked/RANKED_IDEAS.md:12`; `console_r_multiples.txt` | ✅ **real & reproducible** (see nuance in §3) |
| `exit_price ≠ stop_loss` in 703/773 stopped trades | `…/02_per_asset_class/ANALYSIS.md:88` | ✅ |
| `/audit2` (v2) baked data frozen 2026-05-16, live-fetch TODO never done, no deploy path | `audit_dashboard/v2/index.html:532,801,823,828`; grep of `.github/workflows` | ✅ |
| audit3 denylist now wired into emission (no longer theatre) | `feed_hygiene.py:194`, `forward_validator.py:763` | ✅ (I flagged this same fact in `08`) |
| FTP secret names corrected in audit3 workflows | `audit3-ledger.yml:144–149` | ✅ |

The peer work is empirically grounded; I have no numbers dispute.

---

## 2. Strong points (agree)

1. **The stop-fill overshoot is the single most actionable new mechanical finding** in
   the whole effort: it says crypto losses are dominated by *fill slippage*, not signal.
   This should be added to the tunable-variable set as "polled-stop vs rested-stop /
   fill model" and to audit2 as a headline measurement, not buried in a research folder.
2. **The conceptual split is right:** audit3 = kill tribunal (denial), audit = wide
   dashboard, audit2 = candidate/methodology library (the positive side). My `09`
   independently argued the same division; the peer's `05` is more polished.
3. **The `v2/index.html` contradiction is a real trust hazard.** It is committed but
   orphaned, frozen at May 2026, and contradicts audit3 on the *sign* of CRYPTO/COMMODITY.
   Retiring or re-pointing it (301 → `/audit3/`) is the correct call.
4. **`SWARM_AUDIT2_HISTORY.md` is good forensic work** — it independently confirms audit2
   was never built (404), found the FTP-secret bug, and documented its fix. The path to
   audit3 being live is now clearer.

---

## 3. Pushback / nuance

1. **Mean vs median on the overshoot.** The "98.8%" uses *means*. The console evidence
   (`console_r_multiples.txt`) shows the **median** planned 1.50% → realized 2.13%,
   overshoot **+41.9%**. Still large and directionally identical, but the headline should
   carry the median too so it is not read as "98.8% of every trade." Recommend reporting
   both and the gap distribution.
2. **EFFECTIVE-N caution on audit2 candidate pods.** Several pods in `05` have tiny n:
   P5 (POSITION-horizon, n=33) and P8 (mega_mutation, n=19). They are correctly labeled
   "observe, don't trade," but I'd move P5 to the **observe** tier (not candidate) until
   n ≥ 100 forward. Keep the *n*, the *interval*, and a power/MDE target on every pod card
   (matches my `09` recommendation).
3. **Counts differ by survey** (166 vs 171/45 cells; 3,500 vs 3,447 picks). Direction is
   identical everywhere; audit2 must display a **single denominator** (the audit3 ledger or
   the canonical `resolved_closed_picks_net` view) rather than each pod's own slice.
4. **"Boring portfolio" (Section D of `05`) is a good addition** but should be explicitly
   separated from the *research* content of audit2 — it is capital allocation advice, not
   a measurement. Keep it as its own panel, clearly marked, so it can't be read as a pick.
5. **P4 (EQUITY/ETF breakout family)** is the strongest forward candidate because it is
   already pre-registered (`POD-EQUITY-BREAKOUT`). It should be the *default first pod* of
   audit2, ahead of the research-heavy P1/P2 which need new data plumbing.

---

## 4. Reconciliation of the two audit2 specs

My `09_AUDIT2_CONTENT_RECOMMENDATION.md` and the peer's `05_AUDIT2_SPEC.md` overlap ~80%.
They should be **merged**, not kept as two competing specs. Consolidated result is in
`11_AUDIT2_SPEC_CONSOLIDATED.md`:

- Take from `05`: the division-of-labour framing, P1–P8 pod registry, measures library,
  boring-portfolio panel, "explicitly do NOT include" list, page requirements E1–E5.
- Take from `09`: the 3-tier strategy shortlist (A verified / B candidate / C traps), the
  conflation-bug list, the 7-panel architecture, the targeted file:line evidence.
- Add from this wave: the stop-fill overshoot measurement (mean+median), the effective-N /
  power target rule, the single-denominator rule, and the explicit "retire v2/index.html"
  action from `PAGES_…`.

---

## 5. Risk rating of the new peer work

| Item | Risk | Note |
|---|---|---|
| Stop-fill overshoot finding | Low (high value) | Add to variables + audit2; cite mean+median |
| Audit2 spec `05` | Low | Converges with `09`; merge |
| v2/index.html live contradiction | **High** (trust) | Retire / 301 → audit3 |
| P5/P8 tiny-n as "candidates" | Med | Downgrade to observe tier + power target |
| Single-denominator drift | Med | Enforce one denominator across audit2 |

---

## 6. Bottom line

The next wave materially improves the programme: it finds a concrete, fixable risk-model
bug, gives audit2 a clean candidate/methodology skeleton, and exposes a live contradiction
(v2) that must be retired. My corrections are refinements (median alongside mean, single
denominator, effective-N tiering, merged spec), not disagreements. Recommended next action:
**land the consolidated audit2 spec (`11_…`) and add the stop-fill overshoot as a tracked
tunable variable.**

*Not investment advice.*
