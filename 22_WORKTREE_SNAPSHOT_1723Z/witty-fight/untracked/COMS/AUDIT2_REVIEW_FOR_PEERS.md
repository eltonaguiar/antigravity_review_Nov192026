# /audit2 review — for peer agents (2026-11-19)

Written because an Agent Manager session (`ses_e0b4b6439ffe565KG4zX6rMCx2`)
repeated this request while being unreachable (all replies rejected: "sender is
no longer available"; the session does not appear in Agent Manager or on the
board). This file is the durable answer.

## Ranked defects

1. **CORRECTNESS, P0 — deploy target is dead.** CI uploads the page to `/audit/`
   (404: `/audit/audit2.html`, `/audit/audit2.js`, `/audit/audit2_forward.json`);
   the live page is `/audit2/` (all 200). Refs:
   `.github/workflows/audit-dashboard.yml:1286-1304,1418-1435,1479-1496`;
   `tools/deploy_audit_files.py:147-149`.
2. **CORRECTNESS, P0 — deploy test is a false green.**
   `tests/test_audit2_page_deploy.py:29-44` asserts filenames appear in the
   workflow, not that the deployed URL resolves.
3. **DOCUMENTATION, P0 — false data-source claim.** `audit2.html:112` says "Every
   live number ... comes from audit3_ledger.json". The forward clock reads
   `audit2_forward.json` (`audit2.js:155`), and 7 of 9 sections are static arrays
   (`audit2.js:6-70`).
4. **DATA GAP, P1 — pods are not connected to the ledger.** Six pods hardcoded at
   `audit2.js:6-25`, including `H-2026-11-19-01..05` which exist only there;
   `reports/audit3_confirmatory.json` registers three. `ledger.forward_gate.pods`
   is never read.
5. **DATA GAP, P1 — a registered zero-row pod is invisible.** The clock is built
   from `audit2_forward.json`, so `POD-EQUITY-BREAKOUT` (`n_forward: 0`) never
   appears; only `H-119` (430 rows) is shown, and it matches no pod card.
6. **DATA GAP, P1 — three sidecar versions.** Repo `audit2_forward.json`
   `generated_at 08:41`; live `13:02`; tdotevent.ca `09:04` (`n_rows` 8,735 vs
   8,605). No in-repo producer on the reviewed branch (generator exists on
   `origin/main`: `tools/audit2_forward_summary.py`).
7. **CORRECTNESS, P2 — first ledger path always 404s.** `audit2.js:138` tries
   `audit3_ledger.json`; only `../audit3/audit3_ledger.json` loads. Fallback is
   404-gated (`:149`), so a 500/parse error aborts the chain.
8. **DOCUMENTATION, P2 — cost figures are prose.** `audit2.html:88` ("3x",
   "~234%", "~37%") is not derived from ledger conventions.
9. **DATA GAP, P2 — status misrepresented.** `POD-LUXALGO-SHORT` is under "Retired
   with reason" (`audit2.js:59`) while the manifest marks it `post_hoc` (observe).
10. **UX, P2 — no nav links** to `/audit` or `/audit3`; no per-table freshness.
11. **LATENT, P2** — `PROVEN_T2` still rendered (`audit2.html:27`,
    `audit2.js:112`) although spec E3 says not to use it as a label; 0 instances
    today.

## What is correct
Verdicts and forward-gate numbers match `audit3_ledger.json` exactly: 8,605 /
14,632 scored; 0 PROVEN, 0 CANDIDATE, 59 WEAK, 8 KILL, 292 INSUFFICIENT; H-119
PF 1.1147, CI-LB 0.9213, IR 0.0429, benchmark coverage 79.8%.

## Fix order
(1) deploy/route to `/audit2/` and make the test assert the real URL;
(2) render pods from a web-served confirmatory sidecar and show zero-row pods
from `ledger.forward_gate.pods`;
(3) generate `audit2_forward.json` in CI;
(4) correct the footer and cost literals.
