LEAKAGE CONTEXT — Read before analyzing:

The following known data-quality incidents affect this project's datasets. Your
first task is to determine whether ANY of them invalidate the numbers below. If
so, say so explicitly and adjust.

 - H-101 (COMMODITY): COT publication-lag look-ahead. Pre-dedup commodity numbers
   showed PF~4.3/WR~58%; post-policy ground truth is PF~0.31/WR~11%. Any
   commodity analysis citing PF>1.0 on multi_asset_copytrader/multi_asset_cot is
   contaminated unless proven otherwise.
 - M-095 (COMMODITY): CT=F cotton re-emission — 230 closed picks from 16 unique
   signal dates (~14x). One trade counted ~14x.
 - M-069 (NET): slippage-adjusted re-judgment reclassifies marginal wins as
   losses; gross-PF and net-PF can diverge 2-3x.
 - QUALITY_BUCKETS (ALL): the quality_bucket field is POST-HOC and circular
   ("profitable_tp" = picks that hit TP). Never a pre-trade filter.
 - RETRACTED 2026-11-19: an earlier "ETF TAA Sharpe 0.88 / MaxDD -19%" claim was
   withdrawn — it reproduced only at same-close (lag-0) execution; honest 1-day
   lag gives Sharpe 0.82 vs SPY 0.69 with CAGR 8.94% vs SPY 10.79%. Diagnosis:
   WINDOW artefact (2018-2026 excluded 2008). 0/576 pre-registered grid cells met
   the bar. What survived: drawdown control (MaxDD -50.8% -> -31.6%, -38%), NOT
   alpha.
 - RETRACTED 2026-11-22: "EQUITY is the only +alpha class" — full-population
   +0.158%/trade vs recent-24m -0.953%/trade (sign flip under window change).
 - Peer freebuff retracted a CRYPTO "PROVEN": PF 1.313 -> 0.2656 over 22,864
   picks, -0.0464%/trade GROSS; it was window selection.
 - Our own kill-gate: a scoring signal is admissible iff eff=(mean_score|WON -
   mean_score|LOST)/pooled_sd >= 0.30 with the SAME SIGN in >= 3 windows of >= 80
   picks. Calibration just showed: false-positive rate 0.0% at zero edge, but
   true-positive rate only 10% at a genuine eff=0.26, 4% at eff=0.21, and it
   DECLINES with more data per window. MDE at n=80 is 0.44 > the 0.30 bar.

QUESTION — answer as a quant risk/portfolio researcher, not as a financial adviser.

I ran the SAME five constructions on ten asset classes, monthly bars, yfinance
adjusted close (dividends included), signal uses data through month t-1 close and
earns month t (lag = 1 month), costs charged on one-way turnover at 20bp
(and stress-tested to 40bp).

The five constructions:
  BH_EW      equal-weight buy & hold of the class basket
  XS_MOM_TOP3 12-1 month cross-sectional momentum, top 3, long only, monthly
  XS_REV_BOT3 1-month reversal, bottom 3, long only
  TREND_EW   10-month simple moving average on the equal-weight class index:
             fully invested when last close > 10m SMA, else 100% in SHY (1-3y T)
  VOLTGT_EW  inverse-vol / 10% vol-target overlay on the equal-weight index

Measured (net of 20bp), best construction per class:

  class        best        Sharpe  CAGR%   MaxDD%  worst-12m  DSR(K=5-6)  40bp Sharpe
  EQUITY       TREND_EW     0.809   8.26   -18.10   -16.23     0.9999      0.751
  ETF          TREND_EW     0.800   6.02   -13.12   -12.57     0.9972      0.734
  INDEX        TREND_EW     0.684   7.00   -20.43   -20.43     0.9998      0.633
  MUTUAL_FUND  TREND_EW     0.938   7.03   -15.67   -13.36     1.0000      0.872
  BOND         BH_EW        0.572   3.48   -20.03   -18.24     0.9765      0.570
  COMMODITY    TREND_EW     0.759  10.23   -34.77   -21.22     0.9986      0.723
  FUTURES      TREND_EW     0.828   6.50   -11.66    -8.55     0.9766      0.757
  FOREX        TREND_EW     0.134   0.32   -10.95    -9.12     0.6205     -0.146
  PENNY_STOCK  TREND_EW     0.512  16.69   -53.23   -28.98     0.9300      0.494
  CRYPTO       BH_EW        0.692  37.45   -78.92   -74.05     0.9392      0.692

  Benchmarks: SPY buy&hold 0.693 Sharpe / 10.01% CAGR / -50.78% MaxDD.
  Cross-sectional momentum L/S was catastrophic nearly everywhere
  (FUTURES -18% CAGR, PENNY -94% CAGR, CRYPTO -70% CAGR).
  Note PENNY_STOCK: currently-listed sub-$5 names only => survivorship-biased
  upward; the 20-40bp turnover cost used is far below real OTC spreads.

Two things I want from you, and I want them falsifiable, not agreeable:

1. INTERPRETATION. Is "10-month SMA trend overlay on a class-level equal-weight
   index" a real, durable, *implementable* risk-control construction, or is it a
   well-known artifact of monthly data that will not survive live execution?
   Be specific: what exactly decays, and by how much? Cite the mechanism.

2. WHAT BREAKS IT / WHAT I HAVE NOT MEASURED. Name the specific tests a desk
   would require before allocating, that I have not run. For each, give the
   statistic, the threshold, and the failure mode it catches. Prioritise by
   expected damage — I would rather find the one that invalidates everything than
   ten that polish it.

Constraints on your answer: no price targets, no "you should buy X", no
personalised advice. Cite mechanisms and named statistics. If you are unsure,
say UNVERIFIED rather than inventing a number. Do not restate my table back to
me — assume I have read it.
