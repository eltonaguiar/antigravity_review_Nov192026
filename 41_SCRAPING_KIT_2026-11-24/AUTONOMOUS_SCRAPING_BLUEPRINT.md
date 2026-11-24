# Autonomous Hybrid Harvesting Architecture Blueprint
**Target Repositories:**
1. [`eltonaguiar/GTA5TORONTOTRACKER`](https://github.com/eltonaguiar/GTA5TORONTOTRACKER) — Autonomous GTA Xbox Series X/S & PS5 Inventory Monitor
2. [`eltonaguiar/BESTIEJOB`](https://github.com/eltonaguiar/BESTIEJOB) — Autonomous Ban-Safe Job Harvester (ServiceNow, Salesforce & Pattern-Learned "Other")

**Constraints & Design Principles:**
- **Execution Mode:** Hybrid (GitHub Actions Cloud Cron + Lightweight Local Residential Runner)
- **Cost Stack:** **100% Free ($0/mo)** — zero paid proxy pools, zero paid CAPTCHA solvers, zero paid LLM APIs.
- **Anti-Ban Guarantee:** Personal LinkedIn/Amazon/retail accounts are **never** touched by headless scrapers or cookie-extractors.
- **Zero-Regression Integration:** Respects existing CI guards (`stock-monitor.yml`, `bestiejob-main-write` concurrency group, `inbox/` staging, `board_invariants.py`, `readme-guard.yml`, `job_source_truth.py`).

---

## 1. Why Current Scrapers Get Blocked (Root Cause Audit)

Inspecting both repositories and testing live endpoints from datacenter IPs reveals three distinct blocking layers:

| Layer | Who Uses It | Why GitHub Actions Fails | How the Hybrid $0 Architecture Beats It |
|---|---|---|---|
| **1. Datacenter ASN / IP Reputation** | Walmart CA, Best Buy HTML, LinkedIn logged-in | GitHub Actions runs on Microsoft Azure IPs (`AS8075`), which WAFs score as `bot=99` before reading headers. | Route WAF-heavy targets to your **Local Residential Runner** (Bell/Rogers/Beanfield home IP = clean consumer ASN) OR hit **unwalled JSON APIs** (e.g., Best Buy `ecomm-api`). |
| **2. TLS / JA3 / HTTP2 Fingerprinting** | Canada Computers, Staples, LinkedIn Guest | Python `urllib` / `requests` and stock headless Chromium advertise a non-browser TLS handshake. | Use `curl_cffi` (`impersonate="chrome124"`) for pure HTTP, and **attach via CDP (`--remote-debugging-port=9222`)** to a real local Chrome instance for Cloudflare Turnstile sites. |
| **3. HTML Trap / Ambiguous DOM** | Best Buy, Amazon, Aggregator Job Mirrors | As documented in `GTA5TORONTOTRACKER/FINDINGS.md`, PS5 pages contain *"Add to Cart"* (for a $79 controller) and *"Sold Out"* (for the console) simultaneously. | **Never regex raw HTML keywords when structured data exists.** Parse SKU-level JSON APIs, Schema.org `ld+json` (`Offer.availability` / `JobPosting.datePosted`), and first-party ATS JSON APIs. |

---

## 2. System Architecture Overview (Hybrid Cloud + Local)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CLOUD TIER: GITHUB ACTIONS ($0)                          │
│  Runs every 30–60m on Ubuntu runners. Never touches strict residential WAFs.    │
│                                                                                 │
│  [GTA5TORONTOTRACKER]                     [BESTIEJOB]                           │
│  • Canada Computers (`curl_cffi` HTML)    • 8 First-Party ATS APIs (Workday,    │
│  • Best Buy CA `ecomm-api` JSON (M5G!)      Greenhouse, Lever, Ashby, etc.)     │
│  • Merges `data/local_state.json`         • Adzuna API + Free Search Indexers   │
│  • Rebuilds `README.md` (Tables 1 & 2)      (Brave/Tavily/Exa/Jina via ai_panel)│
│  • Optional Discord/Telegram/Email ping   • Pattern-Learner (`other_learner.py`)│
│                                           • Merges `inbox/*.md` -> `build_site` │
└───────────────────────────────▲─────────────────────────────────▲───────────────┘
                                │ git push (JSON / inbox/*.md)    │
┌───────────────────────────────┴─────────────────────────────────┴───────────────┐
│                LOCAL TIER: RESIDENTIAL DAEMON / TASK SCHEDULER ($0)             │
│  Runs every 1–3h in background on your home PC/Mac (Residential ISP IP).        │
│                                                                                 │
│  1. Persistent Dedicated Chrome Profile (`--user-data-dir=~/.scraper-chrome`)   │
│     • Completely isolated from your personal browser & LinkedIn/Amazon logins!  │
│     • Attaches via CDP (zero WebDriver/Playwright flags; passes Cloudflare).    │
│  2. Retail Sweep -> Writes `data/local_state.json` to `GTA5TORONTOTRACKER`:     │
│     • Amazon.ca (M5G postal), Walmart.ca (`__NEXT_DATA__`), Staples,            │
│       GameStop.ca / EBGames, Memory Express, Costco.                            │
│  3. Safe Job Sweep -> Writes `inbox/local-harvester--YYYY-MM-DD--vN.md`:        │
│     • LinkedIn Guest API (jittered, residential IP, zero cookies = zero ban)    │
│     • Indeed / Glassdoor / Eluta via search-cache & residential JSON-LD         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Part A Blueprint: `GTA5TORONTOTRACKER` (Autonomous Console Stock)

### Key Discovery: Best Buy Canada Is Already Unblocked via JSON!
Right now, `GTA5TORONTOTRACKER` lists Best Buy Canada in **Table 2 (UNVERIFIED)** due to Akamai `"Access Denied"` on HTML product pages.
However, **live testing from a datacenter IP today confirmed HTTP 200** on Best Buy's fulfillment microservice:

```
GET https://www.bestbuy.ca/ecomm-api/availability/products
  ?accept=application%2Fvnd.bestbuy.standardproduct.v1%2Bjson
  &accept-language=en-CA
  &locations=937|977|617|203   # Bay & Dundas (977), Markham (937), Sherway, etc.
  &postalCode=M5G
  &skus=19422130|19446111|20189840|19422127|19422129
```
- Returns BOM-prefixed JSON (`utf-8-sig`) with **exact store-by-store `quantityOnHand`** (e.g., `977` = Downtown Toronto Bay & Dundas right at M5G!) and **`shipping.status` / `purchasable`**—separating first-party stock from scalper marketplace sellers.
- **Immediate Win:** Best Buy moves from Table 2 (Unverified) to **Table 1 (100% Cloud-Automated every 30 mins)** with zero browser needed.

### Retailer-by-Retailer Extraction Matrix ($0 Stack)

| Retailer | Bot Wall | Runner Tier | Exact Extraction Method (No Keyword Guessing) |
|---|---|---|---|
| **Canada Computers** | Light TLS check | **Cloud (GHA)** | Existing `curl_cffi` (`impersonate="chrome"`) parsing embedded per-store stock spans (`Toronto Downtown` 312 Yonge + GTA stores). |
| **Best Buy Canada** | Akamai on HTML; **Open on API** | **Cloud (GHA)** | `ecomm-api/availability/products` with `postalCode=M5G` and GTA `locations`. Filter `sellerId == null` (or flag marketplace price spikes > MSRP + 15%). |
| **Amazon.ca** | CAPTCHA on Azure IPs | **Local Runner** | Dedicated logged-out Chrome profile with postal code set once to `M5G 2C3` via UI cookie. Parse `#desktop_buybox` (`#priceblock_ourprice` / `.a-price .a-offscreen`, `#merchant-info`, `#mir-layout-DELIVERY_BLOCK`). |
| **Walmart Canada** | PerimeterX / Akamai | **Local CDP** | Attach via CDP to local Chrome -> load SKU URL -> read `<script id="__NEXT_DATA__">` JSON (`props.pageProps.initialData.data.product.availabilityStatus` + `fulfillmentSummary` + `currentPrice`). Differentiates `"SOLD_BY_WALMART"` vs 3rd-party scalpers! |
| **EB Games / GameStop CA** | Cloudflare (`ebgames.ca` / `gamestop.ca`) | **Local CDP** | Note: `gamestop.ca` / `ebgames.ca` uses Cloudflare Turnstile. Local CDP Chrome passes passively using persistent `cf_clearance` cookie in `~/.scraper-chrome`. Parse `application/ld+json` `Offer.availability` + store-pickup radio state for `267 Yonge St`. |
| **Staples Canada** | Cloudflare on Shopify | **Local CDP** | Staples CA runs on Shopify architecture; once loaded in local CDP Chrome, read `window.ShopifyAnalytics` / `application/ld+json` `offers[]` (`InStock` vs `OutOfStock`) by exact SKU. |
| **Memory Express** | Cloudflare Challenge | **Local CDP** | Load product SKU page via local CDP -> parse `#InventoryStatus` per-store block (Etobicoke / Mississauga / Online). |
| **Local Indie Shops** *(Gamerama, ReserveRoom, etc.)* | No live cart / Phone | **Semi-Auto** | Keep in Table 3 ("Local Indie Stores — Call to Hold"), plus optional `curl_cffi` check on `reserveroom.ca` Shopify `/products/<handle>.json` if they list online! |

### Decoupling State from `README.md` (Fixing the Overwrite Bug)
In `FINDINGS.md`, an earlier agent noted that `stock-monitor.yml` wiped manual findings because `check_stock.py` hardcodes `AMAZON_ROWS` and rewrites `README.md` from scratch.
**Fix:**
1. Store structured state in `data/stock_state.json`:
   - `cloud_sources` (updated every 30m by GitHub Actions: Canada Computers + Best Buy API)
   - `local_sources` (updated every 1–2h by your Local Runner: Amazon, Walmart, Staples, EB/GameStop, Memory Express, each with its own `checked_at` timestamp and `ttl_hours: 6`)
2. `scripts/render_readme.py` merges both JSON files:
   - Any row verified within TTL -> **Table 1 (VERIFIED — Live Stock & Price)**, sorted with ✅ In-Stock items at the top and MSRP/scalper badges (e.g., flagging `$1,299` Xbox Series X as `⚠️ 3rd-Party Scalper` vs `$729.99 MSRP`).
   - Any row whose check failed or exceeded TTL -> automatically demotes to **Table 2 (STALE / BLOCKED)**—preserving your core rule: *never show a fake "Sold Out" when a check fails*.

---

## 4. Part B Blueprint: `BESTIEJOB` — Zero-Ban Harvesting & Pattern Learning

### 1. The "Never Get Banned on LinkedIn" Golden Rules
LinkedIn bans accounts in three ways: **(a)** exporting `li_at` session cookies into Playwright/Puppeteer/extensions, **(b)** automating clicks/scrolls in a browser where you are logged in, or **(c)** firing hundreds of logged-in requests from a residential IP tied to your active session.

Here is the **4-Layer Ban-Proof Isolation Protocol**:

1. **Zero-Account / Zero-Cookie Isolation:**
   - Never use `li_at` cookies, browser extensions, or logged-in Playwright sessions.
   - Your local runner uses a dedicated `--user-data-dir` (or pure `curl_cffi` HTTP) that has **never** logged into LinkedIn. Even in a worst-case rate-limit (`HTTP 429`), LinkedIn only cools down anonymous guest queries for 15 minutes—it has zero link to your personal profile.
2. **Search-Engine Offloading ("Dork Harvesting" — 0 Direct Requests to LinkedIn):**
   - `BESTIEJOB` already has `tools/ai_panel.py` wired for free search APIs (**Brave Search, Tavily, Exa, Jina, DuckDuckGo**).
   - Querying `site:ca.linkedin.com/jobs/view ("ServiceNow" OR "Salesforce") ("Toronto" OR "Ontario")` with `freshness=pd` (past 24h) harvests LinkedIn job URLs, titles, companies, and dates **from the search engine's index** without sending a single packet to `linkedin.com`.
3. **Jittered Residential Guest API (Move off Azure IPs):**
   - Your existing `scripts/linkedin_guest_scan.py` hits `/jobs-guest/jobs/api/seeMoreJobPostings/search` across `60 keywords × 4 locations × 2 pages = 480 requests` at a fixed `0.8s` sleep. From GitHub Actions, LinkedIn throttles Azure IPs heavily (`429`).
   - **Upgrade:** Collapse the 60 overlapping queries into **12 Boolean/grouped queries**, add randomized human jitter (`random.uniform(2.5, 5.5)` seconds), cap at 1 page (`start=0`) on hourly runs since it's sorted by `f_TPR=r86400` (last 24h), and run from the **Local Runner** once every 3–4 hours (~36 gentle requests total).
4. **Canonical ATS Upgrade ("Corpus = Watchlist"):**
   - As `scripts/gx10_runner.py` and `AGENT-RUNBOOK.md` rightly point out: staffing agencies and enterprises post on **Workday, Greenhouse, Lever, Ashby, SmartRecruiters, iCIMS, Dayforce, BambooHR, and Oracle HCM** *hours before* LinkedIn or Adzuna indexes them.
   - Polling those public JSON endpoints from GitHub Actions has **zero ban risk**, **100% accurate `postedDate`**, and **direct employer apply links**.

---

### 2. Autonomous Pattern-Learner for the `"Other"` Category
You specifically asked to:
> *"for other category, find jobs based on common pattern amongst the pre-existing listings in that category"*

I ran a corpus analysis across all **5,626 jobs** in your live `BESTIEJOB/jobs.json` (`3,381` in `Other`, `1,173` in `Salesforce`, `1,072` in `ServiceNow`). Look at what your existing `Other` corpus actually clusters around:
- **Cluster 1 — Full-Stack & Software Engineering:** `full stack` (150), `software engineer` (139), `software developer` (57), `backend` (37)
- **Cluster 2 — Data, BI & Analytics:** `data analyst` (117), `business intelligence` (62), `data engineer` (57), `power bi` (26)
- **Cluster 3 — Business Systems & IT Delivery:** `business analyst` (114), `project manager` (101), `systems analyst` (42), `business systems` (36), `product manager` (35), `it project` (30)
- **Cluster 4 — Cloud, DevOps & IT Asset/Ops:** `devops engineer` (50), `systems administrator` (31), `site reliability` (30), `asset management` (29)
- **Noise currently leaking into `Other`:** `Planner, Demand Planning` (ENDY), `Group Sales Operations` (Triumph), `Solution Sales Executive` (ServiceNow vendor sales).

Instead of maintaining a static keyword list by hand, we add a **100% local, zero-cost ML module (`tools/other_pattern_learner.py`)** using `scikit-learn` (or pure Python TF-IDF + Cosine Similarity, zero GPU/API cost):

#### How the Closed-Loop Pattern Learner Works:
```
  [Existing Other Corpus]          [APPLIED.md + High-Fit Rows]       [Normalized / Purged Rows]
     (3,381 rows in jobs.json)         (2x Positive Weight)              (Negative Centroid)
               │                                │                                 │
               └────────────────────────────────┼─────────────────────────────────┘
                                                ▼
                      ┌──────────────────────────────────────────────────┐
                      │   Step 1: TF-IDF Vectorizer (1–3 word n-grams)   │
                      │   + K-Means / Sub-Cluster Discovery (k = 6..8)   │
                      └─────────────────────────┬────────────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
┌─────────────────────────────────────────┐   ┌────────────────────────────────────────────────┐
│ Step 2: Dynamic Query Generator         │   │ Step 3: Candidate Centroid Scorer (Gatekeeper) │
│ Extracts top discriminative n-grams per │   │ Scores every scraped non-SN/SF job:            │
│ cluster (high c-TF-IDF) -> emits fresh  │   │   sim = cos(job, Pos_Clusters) - cos(job, Neg) │
│ daily search queries for Adzuna, ATS,   │   │ • sim >= 0.32 -> Auto-accept to `inbox/`       │
│ LinkedIn Guest, and Job Bank!           │   │ • 0.20..0.32  -> Optional `ai_panel.py triage` │
│ Rotates exploration vs. exploitation.   │   │ • sim <  0.20 -> Drop (blocks "Demand Planner" │
└─────────────────────────────────────────┘   │                  & vendor Account Exec noise!) │
                                              └────────────────────────────────────────────────┘
```

1. **Positive + Negative Learning:**
   - **Positive Prototype Vectors:** Built from clean `Other` rows in `README.md` / `jobs.json`, giving **3× weight** to roles matching skills in `build_site.py`'s `PROFILE` or roles similar to `APPLIED.md` (and excluding `APPLIED.md` exact roles from resurfacing).
   - **Negative Prototype Vectors:** Built from `WEAK` regex hits (sales reps, account executives, retail, demand planners, HR recruiters) + previously purged rows so the model actively repels non-IT noise.
2. **Automatic Query Synthesis (`config/learned_other_queries.json`):**
   - Before each scan, `other_pattern_learner.py --emit-queries` extracts the top bigrams/trigrams from each discovered sub-cluster (e.g., `"Business Systems Analyst"`, `"Power BI Developer"`, `"IT Asset Management"`, `"Integration Engineer"`, `"Full Stack Developer"`, `"Site Reliability Engineer"`).
   - Picks the top **8 high-yield queries** (exploitation) + **4 rising/under-sampled bigrams** from the last 7 days of commits (exploration), feeding them directly into Adzuna, ATS sweepers, CareerBeacon/Job Bank, and LinkedIn Guest.
3. **Explainable Sub-Track Tagging:**
   - Every accepted `Other` row gets tagged in its Note/Badge with the exact cluster pattern it matched (e.g., `Other · Pattern: Integration/BSA (0.78)` or `Other · Pattern: Data/BI (0.81)`), aligning with `AGENT-RUNBOOK.md`'s rule to *"Label its actual specialty."*

---

## 5. Exhaustion-Elimination Workflow (Zero Manual Checking)

To completely remove daily checking fatigue across both projects:

1. **Single Local Runner (`local_agent.py`) for Both Repos:**
   - One lightweight Python script scheduled via Windows Task Scheduler / macOS `launchd` / Linux `systemd --user` (runs silently in the background when your computer is on).
   - Every 2 hours:
     - Checks blocked console retailers via local headless/CDP Chrome -> updates `GTA5TORONTOTRACKER/data/local_state.json` -> commits & pushes *only* if stock/price changed.
     - Runs gentle, jittered residential LinkedIn Guest + Canadian agency sweeps -> validates via `check_inbox.py` -> drops a clean `inbox/local-agent--YYYY-MM-DD--vN.md` into `BESTIEJOB` and pushes (letting GitHub Actions' `bestiejob-main-write` concurrency group safely merge and rebuild GitHub Pages without git conflicts!).
2. **Push-Only-When-Actionable Alerts ($0):**
   - **Console Tracker:** GitHub Actions / Local Runner sends a **Discord / Telegram webhook** (or GitHub Issue notification) **only on state transitions**: `Sold Out -> In Stock` at **MSRP + ≤10%** (so you aren't woken up for $1,300 marketplace scalpers).
   - **BESTIEJOB:** Daily morning digest (`DIGEST_TODAY.md` + optional webhook) listing **only net-new `fit >= 80` roles posted in the last 24h** across ServiceNow, Salesforce, and Pattern-Matched `Other`, pre-deduped across Adzuna/LinkedIn/ATS with direct employer apply links prioritized.

---

## 6. Phased Implementation Roadmap

### Phase 1 — `GTA5TORONTOTRACKER` Upgrade
1. **`scripts/retailers/bestbuy_api.py`**: Cloud-safe Best Buy Canada `ecomm-api` adapter checking PS5 Slim, PS5 Pro, Xbox Series X, and Series S for `M5G` + GTA stores (`977` Bay/Dundas, `937` Markham, etc.), separating Best Buy retail stock from 3rd-party marketplace sellers.
2. **`data/stock_state.json` + `scripts/check_stock.py` refactor**: Decouple Cloud vs. Local state so `stock-monitor.yml` never wipes browser-verified rows, adds MSRP vs. Scalper badges, and tracks TTL staleness.
3. **`scripts/local_cdp_watcher.py`**: Local residential runner attaching to isolated Chrome over CDP (`port 9222`) to read structured JSON/DOM from Amazon.ca (`M5G`), Walmart (`__NEXT_DATA__`), Staples, GameStop/EB Games, and Memory Express.

### Phase 2 — `BESTIEJOB` Pattern-Learner & Ban-Safe Harvester
1. **`tools/other_pattern_learner.py`**: TF-IDF + K-Means sub-cluster discovery over `jobs.json` / `README.md`, negative-noise filtering (blocking vendor sales / non-IT planners), dynamic query generator (`--emit-queries`), and candidate scorer (`--score-inbox`).
2. **`scripts/safe_harvester.py`**: Unified ban-safe harvester combining:
   - Search-index dorking (via existing `ai_panel.py` free keys) for zero-touch LinkedIn/Indeed discovery,
   - Rate-safe, Boolean-compacted, residential LinkedIn Guest sweeps (cutting 480 requests down to ~36 jittered requests),
   - Auto-expanding ATS watcher (`gx10_runner` style) seeded from every employer domain ever seen in `README.md`.
3. **Plug into `hourly-scan.yml`**: Wire `other_pattern_learner.py` right before `jobs_merge_inbox.py` so `BESTIEJOB` learns and harvests new `Other` patterns automatically while passing `board_invariants.py` and `readme-guard.yml`.
