#!/usr/bin/env python3
"""Independent MDE measurement recheck for the Track B calibration.

Reads CLASS_CALIBRATION_PRICE_PANEL.csv (read-only), keeps rows with included == 1,
and computes the gross excess return per row as

    (exit_close/entry_close - 1) - (bench_exit_close/bench_entry_close - 1)

then reports:
  - included row count and distinct symbols
  - row-level SD in pp
  - per-symbol mean returns, and the SD of those means, in pp per monthly hold
  - annualised sigma (x12) in pp/yr
  - MDE at 80% power = 2.802 * sd_symbol_means / sqrt(n_symbols), in pp/month and pp/yr

Both sample (ddof=1) and population (ddof=0) standard deviations are printed, because
the two conventions differ by sqrt(n/(n-1)) and that is the most common source of a
"the number does not reproduce" report.

No files are written. No network. Standard library only.
"""
import csv
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "CLASS_CALIBRATION_PRICE_PANEL.csv")
MDE_Z80 = 2.802          # two-sided alpha=0.05, power=0.80
MONTHS_PER_YEAR = 12


def num(v):
    v = (v or "").strip()
    if v in ("", "NA", "NaN", "nan", "None", "NULL"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    with open(PANEL, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    included = [r for r in rows if (r.get("included") or "").strip() == "1"]

    excess = []            # (symbol, pp)
    skipped = 0
    for r in included:
        e0 = num(r.get("entry_close"))
        e1 = num(r.get("exit_close"))
        b0 = num(r.get("bench_entry_close"))
        b1 = num(r.get("bench_exit_close"))
        if None in (e0, e1, b0, b1) or 0.0 in (e0, b0):
            skipped += 1
            continue
        gross = (e1 / e0 - 1.0) - (b1 / b0 - 1.0)
        excess.append((r["symbol"], gross * 100.0))

    by_symbol = {}
    for sym, x in excess:
        by_symbol.setdefault(sym, []).append(x)
    sym_means = [st.fmean(v) for _, v in sorted(by_symbol.items())]

    n_rows = len(excess)
    n_syms = len(by_symbol)
    row_sd_s = st.stdev([x for _, x in excess])      # ddof=1
    row_sd_p = st.pstdev([x for _, x in excess])     # ddof=0
    sm_sd_s = st.stdev(sym_means)                    # ddof=1
    sm_sd_p = st.pstdev(sym_means)                   # ddof=0
    ann_s = sm_sd_s * MONTHS_PER_YEAR
    ann_p = sm_sd_p * MONTHS_PER_YEAR
    mde_m_s = MDE_Z80 * sm_sd_s / math.sqrt(n_syms)
    mde_m_p = MDE_Z80 * sm_sd_p / math.sqrt(n_syms)
    mde_y_s = mde_m_s * MONTHS_PER_YEAR
    mde_y_p = mde_m_p * MONTHS_PER_YEAR

    print("MDE RECHECK -- %s" % PANEL)
    print("=" * 72)
    print("candidate data rows ................ %d" % len(rows))
    print("included == 1 rows ................. %d" % len(included))
    print("rows usable (all 4 closes present) . %d" % n_rows)
    print("rows skipped (missing/zero close) .. %d" % skipped)
    print("distinct symbols ................... %d" % n_syms)
    print("rows per symbol .................... %.4f" % (n_rows / n_syms))
    print()
    print("row-level gross excess, pp:")
    print("   mean ........................... %+.4f" % st.fmean([x for _, x in excess]))
    print("   median ......................... %+.4f" % st.median([x for _, x in excess]))
    print("   SD (sample, ddof=1) ............ %.4f" % row_sd_s)
    print("   SD (population, ddof=0) ........ %.4f" % row_sd_p)
    print()
    print("per-symbol mean returns, pp per monthly hold:")
    print("   n symbols ...................... %d" % n_syms)
    print("   mean of symbol means ........... %+.4f" % st.fmean(sym_means))
    print("   SD of symbol means (ddof=1) .... %.4f   <-- sd_symbol_means" % sm_sd_s)
    print("   SD of symbol means (ddof=0) .... %.4f" % sm_sd_p)
    print("   min / max symbol mean .......... %+.4f / %+.4f" % (min(sym_means), max(sym_means)))
    print()
    print("annualised sigma (x%d):" % MONTHS_PER_YEAR)
    print("   from ddof=1 .................... %.4f pp/yr" % ann_s)
    print("   from ddof=0 .................... %.4f pp/yr" % ann_p)
    print()
    print("MDE at 80%% power = %.3f * sd_symbol_means / sqrt(n_symbols):" % MDE_Z80)
    print("   ddof=1 ......................... %.4f pp/month = %.4f pp/yr" % (mde_m_s, mde_y_s))
    print("   ddof=0 ......................... %.4f pp/month = %.4f pp/yr" % (mde_m_p, mde_y_p))
    print("=" * 72)
    print("GT_COMPARE  rows=%d symbols=%d sd_sym_1=%.3f ann=%.2f mde_m=%.3f mde_y=%.2f"
          % (n_rows, n_syms, sm_sd_s, ann_s, mde_m_s, mde_y_s))


if __name__ == "__main__":
    main()
