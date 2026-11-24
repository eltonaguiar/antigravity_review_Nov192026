# Clean events: does a reiteration count?

zoo-savant, 2026-11-24. Evidence for the owner's decision -- **the prereg is not modified here.**

Source: `tracker/analyst_actions.csv`, 122,746 rows, 308 tickers, 291 firms.

Action mix: `main` 88,341 · `up` 9,873 · `down` 9,720 · `init` 8,812 · `reit` 6,000.

- **Definition A:** `action IN (up, down, init)` -- an event only when the opinion changes.
- **Definition B:** `action IN (up, down, init, reit)` -- as briefed.
- **Definition C:** `action IN (up, down, init, reit, main)` -- B plus `main`, i.e. *every* row.

C is included because `reit` and `main` are both reiterations: B is only "all reiterations"
if `main` is also counted, so the choice is really A vs C.

## (1) Top 10 firms by A

| firm | A (up/down/init) | B (+reit) | C (+reit+main) |
|---|---|---|---|
| Goldman Sachs | 1,236 | 1,261 | 3,148 |
| BofA Securities | 1,221 | 1,408 | 4,047 |
| Morgan Stanley | 1,213 | 1,413 | 10,095 |
| J.P. Morgan | 1,057 | 1,075 | 5,585 |
| UBS | 1,002 | 1,015 | 5,435 |
| Citi | 984 | 1,038 | 6,593 |
| Barclays | 951 | 964 | 7,779 |
| Wells Fargo | 944 | 960 | 5,908 |
| Deutsche Bank | 909 | 933 | 4,609 |
| Jefferies | 844 | 859 | 3,460 |

## (2) Firms reaching each floor

| floor | A | B | C |
|---|---|---|---|
| 300 | **28** | **37** | 51 |
| 500 | **18** | **26** | 46 |
| 750 | **11** | **14** | 37 |

## (3) Effect on the 308-ticker breadth result

Small under A vs B, and misleading under C. Going 155 -> 308 tickers took A from 14/5/0 to
28/18/11, so **the 750 floor is reachable under A already** -- the definition is not what
decides reachability at this breadth, contrary to the premise. Choosing C would raise 750
from 11 firms to 37, but mostly by counting Morgan Stanley's 10,095 rows, of which 8,882
are reiterations of a rating that did not change. A floor crossed by repeating oneself is
not evidence of a firm's track record.

## (4) Recommendation

**Use A (`up/down/init`): a reiteration is not a change of opinion, and the prereg's own
language is "clean events" for a track record that asks whether a firm's *rating changes*
predicted returns.**

Risk if B or C is chosen instead: the per-firm record is diluted with non-events, so a firm
that reiterates often looks well-covered while its actual calls stay few. The Deflated
Sharpe denominator (`trials`) would also be inflated by restatements of the same opinion,
which makes the deflation too lenient -- the exact failure mode the trial-log rule exists
to prevent.

## (5) The check I ran before writing a next_probe

next_probe: is A itself contaminated, i.e. do `up`/`down` rows carry an unchanged grade?

Measured on the same CSV, so this is answered, not deferred: of 19,593 `up`/`down` rows,
**191 (1.0%) have an unchanged or missing grade pair** -- e.g. `Cowen & Co. MSFT up '' ->
Outperform`, a blank `from_grade` rather than a true restatement. Dropping them leaves the
floors at **28 / 18 / 11** (top 3: Goldman 1,225, BofA 1,209, Morgan Stanley 1,207).
**So A is clean and the recommendation above stands unchanged.**

next_probe: for the owner's decision, the cheapest remaining measurement is the per-firm
placebo p95 under A for the 11 firms that clear 750 -- if none of them beats its own
placebo, the floor is reachable but the track record it would certify is empty, which is
the outcome the program's standing expectation predicts.
