# Swarm History — "fix audit2 page" (Google/Gemini swarm, 2026-11-19)

**Source:** Gemini/Google swarm state (not committed to the repo). Located at:
`/home/eaguiar2015/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/swarm/`
(`swarm.json`, `members.json`, `board.jsonl`).

---

## The swarm

| Field | Value |
|---|---|
| Swarm ID | `bb43e24c-a087-4dec-81c2-6be2d8acf5ad` |
| Title | **fix audit2 page** |
| Created | 2026-11-19T04:15:12Z |
| Backend | local |
| Model | `ULTRA_FREE_CLOUD_LARGE` (Google/Gemini) — applied to all members |
| Members | coordinator, investigator, verifier, deployer, monitor, coms-auditor, history-recovery |
| Board | 14 posts (`board.jsonl`), append-only, ended same morning |

A second, earlier swarm `6675f415-…` (2026-11-16, "GH Actions Health" cadence,
761 posts) also touched `audit2` in its ground-truth tick lines, but that was a
GH-Actions-health swarm, not the audit2-fix swarm.

---

## What it was asked to do (initial briefs, seq 1–8)

The coordinator assumed `/audit2/` was a JS SPA (HTTP 200 + `<div id="app">` +
hashed JS) and briefed:
- `@investigator` — diagnose why `/audit2/` "is not working" while `/audit/` works (read-only).
- `@verifier` — verify the audit2 fix diff.
- `@deployer` — deploy the verified fix.
- `@coms-auditor` — COMS health + anything affecting audit2 deploy.
- `@history-recovery` — recover in-flight work from the terminated swarm.

## What it actually found

1. **`/audit2/` is a genuine 404 — it does not exist.** (investigator, seq 9–10)
   - "Accessing `/audit2/` results in a 404 error… no references to `/audit2/`
     in the workflows or repo, confirming it is not deployed."

2. **The coordinator re-scoped the whole swarm** (seq 11), after checking for
   itself:
   > "there is NO audit2 SPA. `/audit2/` returns a genuine Apache 404 and no
   > `assets/data/audit_endpoints.json` exists anywhere in the repo (I verified by
   > recursive grep). **The real deliverable being prepared is `/audit3/`** — a
   > static kill-tribunal ledger deployed via ftplib to `findtorontoevents.ca/audit3`,
   > using secrets `FTP_50WEBS_HOST/USER/PASS`."

3. **COMS broker is up** (coms-auditor, seq 12–13): `COMS status` → broker
   `192.168.2.52:1883/tcp: open`; 3 live seats; no `coms.service` (client is
   just a script, not a systemd unit).

4. **The audit3 deploy referenced non-existent GitHub secrets** (coms-auditor,
   seq 14, the actionable find):
   - `secrets.FTP_50WEBS_HOST` → **absent** (actual: `FTP_HOST`, `FTP_SERVER_50WEBS`)
   - `secrets.FTP_50WEBS_USER` → **absent** (actual: `FTP_USER`, `FTP_USERNAME_50WEBS`)
   - `secrets.FTP_50WEBS_PASS` → **absent** (actual: `FTP_PASS`, `FTP_PASSWORD_50WEBS`)
   - Verified via `gh secret list` (86 secrets).

## Was the fix applied? — Yes

The current `.github/workflows/audit3-ledger.yml` (lines 144–149) and
`.github/workflows/audit3-evidence.yml` (lines 90–92) now use the correct names:

```yaml
# 50webs secret names as they actually exist in this repo (2026-11-19 audit).
FTP_HOST: ${{ secrets.FTP_SERVER_50WEBS }}
FTP_USER: ${{ secrets.FTP_USERNAME_50WEBS }}
FTP_PASS: ${{ secrets.FTP_PASSWORD_50WEBS }}
```

So the "fix audit2 page" swarm effectively became "there is no audit2; deploy
audit3", and its one concrete bug (mismatched FTP secret names blocking the
audit3 deploy) is now fixed in the workflow files.

---

## Implication for this review

This confirms the page-review conclusion in `PAGES_AUDIT2_AUDIT3.md`:

- **There is no audit2.** The live `/audit2/` is a 404 and was never built or
  deployed — independently corroborated by the Gemini swarm's investigator and
  coordinator, not just by grep.
- **audit3 is the real deliverable**, and the swarm's remaining risk was
  deployment plumbing (FTP secret names), which is now corrected.

The `audit_dashboard/v2/index.html` "Statistical Edge per Asset Class v2"
dashboard is a separate, orphaned artifact (stale May-2026 baked data) — it is
not what `/audit2/` served, because `/audit2/` served nothing.
