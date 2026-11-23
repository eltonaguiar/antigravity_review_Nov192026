"""
engine.py -- a small, honest research harness for "top gainers" style signals.

Deliberately built so that the *default* answer is "no edge", because that is the
correct answer for most of these ideas. It contains:

  1. make_synthetic_universe()  -- regime-switching, vol-clustered, fat-tailed price
                                   data for 4 asset classes, with ONE deliberately
                                   planted edge so we can verify the harness can
                                   actually detect something when it exists.
  2. triangular_barrier_backtest() -- ATR-based TP/SL ("triple barrier"), with
                                   per-side costs, giving R-multiples per trade.
  3. metrics()                   -- hit rate, expectancy R, profit factor, Sharpe,
                                   Sortino, max DD, Calmar, PSR, Deflated Sharpe,
                                   block-bootstrap CI, min track record length.
  4. top_gainer_study()          -- the actual "are daily top gainers predictive?"
                                   study, sliced by asset class, symbol, and
                                   symbol x direction, cross-sectionally demeaned
                                   so market beta cannot fake an edge.
  5. purged_walk_forward()       -- chronological folds with embargo, to test a
                                   conditional signal out-of-sample.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from scipy import stats

TRADING_DAYS = {"equity": 252, "fund": 252, "crypto": 365, "fx": 260}


# ----------------------------------------------------------------------------
# 1. Synthetic universe (stand-in for real vendor data)
# ----------------------------------------------------------------------------
@dataclass
class Asset:
    symbol: str
    asset_class: str
    ann_vol: float
    ann_drift: float = 0.0
    # planted edges (all zero = "nothing is predictable", the null world)
    mom: float = 0.0          # coefficient on trailing 5d z-scored return
    mr: float = 0.0           # coefficient on 5d z-scored (negative => reversal)
    jump_prob: float = 0.004
    jump_scale: float = 0.06
    autocorr_nav: float = 0.0  # stale NAV smoothing (mutual funds)
    vol_persistence: float = 0.94


def make_synthetic_universe(seed: int = 7, n_days: int = 2200) -> dict[str, pd.DataFrame]:
    """Returns {symbol: DataFrame[open, high, low, close, volume]} on a business-day index."""
    rng = np.random.default_rng(seed)
    specs = [
        # ---- equities -------------------------------------------------------
        Asset("AAA", "equity", 0.24, 0.06, mom=0.0, jump_prob=0.010, jump_scale=0.09),
        Asset("BBB", "equity", 0.34, 0.02, mr=-0.010, jump_prob=0.008),
        Asset("CCC", "equity", 0.45, -0.05, jump_prob=0.015, jump_scale=0.11),
        # ---- crypto ---------------------------------------------------------
        Asset("BTCUSD", "crypto", 0.55, 0.15, mom=0.12, jump_prob=0.020, jump_scale=0.07),
        Asset("ETHUSD", "crypto", 0.72, 0.10, jump_prob=0.020, jump_scale=0.09),
        Asset("SOLUSD", "crypto", 0.95, 0.05, mr=-0.05, jump_prob=0.030, jump_scale=0.12),
        # ---- fx -------------------------------------------------------------
        Asset("EURUSD", "fx", 0.075, 0.0, mr=-0.09),
        Asset("USDJPY", "fx", 0.090, 0.0, mr=-0.008),
        # ---- mutual fund (NAV-only, stale pricing, high fee drag) -----------
        Asset("MFUNDX", "fund", 0.16, 0.03, autocorr_nav=0.35),
    ]
    idx = pd.bdate_range("2017-01-02", periods=n_days)
    out = {}
    for a in specs:
        n = n_days
        # volatility clustering: AR(1) log-vol (OU) + Markov vol regimes,
        # then rescaled so realised annualised vol matches the target exactly.
        target = a.ann_vol / np.sqrt(TRADING_DAYS[a.asset_class])
        state, p_stay, regime = 0, 0.985, np.ones(n)
        for t in range(1, n):
            if rng.random() > p_stay:
                state = 1 - state
            regime[t] = 1.6 if state else 0.8
        logv = np.zeros(n)
        for t in range(1, n):
            logv[t] = 0.97 * logv[t - 1] + 0.15 * rng.standard_normal()
        sig = target * np.exp(logv - logv.mean()) * regime
        sig *= target / sig.std()          # exact rescale
        shocks = rng.standard_t(df=5, size=n) / np.sqrt(5 / 3)  # unit-variance t5

        mu = a.ann_drift / TRADING_DAYS[a.asset_class]
        eps = sig * shocks
        r = np.full(n, mu) + eps

        # planted predictable component from trailing 5d z-scored return
        z = np.zeros(n)
        for t in range(6, n):
            past = r[t - 5:t]
            s = past.std()
            z[t] = (past.sum() - 5 * mu) / (s * np.sqrt(5)) if s > 0 else 0.0
            r[t] += (a.mom + a.mr) * z[t] * sig[t]

        # rare jumps
        jmask = rng.random(n) < a.jump_prob
        r[jmask] += rng.normal(0, a.jump_scale, jmask.sum())

        close = 100 * np.exp(np.cumsum(r))
        # intraday OHLC: open gaps, high/low bracket the day
        gap = rng.normal(0, 0.35, n) * sig
        open_ = np.empty(n)
        open_[0] = close[0]
        open_[1:] = close[:-1] * np.exp(gap[1:])
        rng_ = np.abs(rng.normal(0, 0.9, n)) * sig
        high = np.maximum(open_, close) * np.exp(rng_)
        low = np.minimum(open_, close) * np.exp(-np.abs(rng.normal(0, 0.9, n)) * sig)
        vol = np.exp(rng.normal(8, 0.5, n)) * (1 + 3 * np.abs(r))

        if a.autocorr_nav:  # stale NAV: smooths returns => fake low vol, fake persistence
            w = a.autocorr_nav
            close = pd.Series(np.log(close)).ewm(alpha=1 - w).mean().pipe(np.exp).values
            close *= np.linspace(1, 1.6, n)
            open_, high, low = close, close, close
            vol[:] = np.nan

        df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                           "volume": vol}, index=idx)
        df["asset_class"] = a.asset_class
        out[a.symbol] = df
    return out


# ----------------------------------------------------------------------------
# 2. TP/SL backtest (triple barrier, ATR units, per-side costs)
# ----------------------------------------------------------------------------
@dataclass
class Trade:
    symbol: str
    asset_class: str
    side: int          # +1 long, -1 short
    entry_date: pd.Timestamp
    entry: float
    exit_date: pd.Timestamp
    exit: float
    reason: str        # 'tp' | 'sl' | 'time'
    r: float           # R-multiple net of costs
    bars: int


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    tr = pd.concat([(df.high - df.low),
                    (df.high - df.close.shift()).abs(),
                    (df.low - df.close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def triangular_barrier_backtest(df: pd.DataFrame, signals: pd.DataFrame, *,
                                tp_mult: float = 2.0, sl_mult: float = 1.0,
                                horizon: int = 10, cost_bps: float = 8.0,
                                atr_n: int = 14) -> pd.DataFrame:
    """signals: DataFrame indexed by date with columns ['side'] in {-1,0,+1}.
    Entry is at the NEXT bar's open (no look-ahead). Barriers are set in ATR units
    from that entry; whichever of TP / SL / horizon is hit first closes the trade.
    Costs: cost_bps charged on entry and exit (spread + commission + slippage)."""
    a = atr(df, atr_n)
    lo, hi, op, cl, ix = (df.low.values, df.high.values, df.open.values,
                          df.close.values, df.index)
    rows = []
    sid = signals["side"].reindex(df.index).fillna(0).values
    for i in np.flatnonzero(sid):
        side = int(sid[i])
        if side == 0 or i + 1 >= len(df) or not np.isfinite(a.iloc[i]):
            continue
        entry = op[i + 1]
        risk = sl_mult * a.iloc[i]
        if not np.isfinite(risk) or risk <= 0:
            continue
        tp_px = entry + side * tp_mult * a.iloc[i]
        sl_px = entry - side * risk
        exit_px, reason, bars = cl[min(i + horizon, len(df) - 1)], "time", horizon
        for j in range(i + 1, min(i + 1 + horizon, len(df))):
            hit_sl = (lo[j] <= sl_px) if side > 0 else (hi[j] >= sl_px)
            hit_tp = (hi[j] >= tp_px) if side > 0 else (lo[j] <= tp_px)
            if hit_sl and hit_tp:      # intrabar ambiguity -> assume the bad one
                exit_px, reason, bars = sl_px, "sl", j - i
                break
            if hit_sl:
                exit_px, reason, bars = sl_px, "sl", j - i
                break
            if hit_tp:
                exit_px, reason, bars = tp_px, "tp", j - i
                break
        gross = side * (exit_px - entry) / risk
        net = gross - (2 * cost_bps / 1e4) * entry / risk
        rows.append(Trade(df.asset_class.iloc[0] if "asset_class" in df else "",
                          "", side, ix[i + 1], entry, ix[min(i + 1 + bars, len(df) - 1)],
                          exit_px, reason, net, bars))
    t = pd.DataFrame([vars(r) for r in rows])
    return t


# ----------------------------------------------------------------------------
# 3. Metrics
# ----------------------------------------------------------------------------
def _ann(x: pd.Series, ppy: int) -> float:
    sd = x.std()
    return 0.0 if sd == 0 else float(np.sqrt(ppy) * x.mean() / sd)


def psr(returns: np.ndarray, sr_benchmark: float = 0.0, ppy: int = 252) -> float:
    """Probabilistic Sharpe Ratio (Bailey & Lopez de Prado): P(true SR > benchmark)."""
    r = np.asarray(returns, float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 5:
        return np.nan
    sr = r.mean() / r.std(ddof=1) * np.sqrt(ppy)
    skew = stats.skew(r)
    kurt = stats.kurtosis(r, fisher=False)
    denom = np.sqrt(1 - skew * sr / np.sqrt(ppy) + (kurt - 1) / 4 * (sr ** 2) / ppy)
    return float(stats.norm.cdf((sr - sr_benchmark) * np.sqrt(n - 1) / denom))


def deflated_sharpe(returns: np.ndarray, n_trials: int, ppy: int = 252) -> tuple[float, float]:
    """Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014).

    If you tried N configurations and kept the best, the best one's Sharpe is a
    maximum of N draws: its expected value under a true null is NOT zero. DSR
    asks: given that selection, what is P(true SR > 0)?

    Returns (E[max SR | null], DSR).  DSR > 0.95 is the bar to clear.
    """
    r = np.asarray(returns, float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 20 or n_trials < 2:
        return np.nan, np.nan
    sr = r.mean() / r.std(ddof=1)                       # per-period SR
    skew, kurt = stats.skew(r), stats.kurtosis(r, fisher=False)
    var_sr = (1 - skew * sr + (kurt - 1) / 4 * sr ** 2) / max(n - 1, 1)
    emc = 0.5772156649
    z1 = stats.norm.ppf(1 - 1 / n_trials)
    z2 = stats.norm.ppf(1 - 1 / (n_trials * np.e))
    sr0 = np.sqrt(var_sr) * ((1 - emc) * z1 + emc * z2)  # per-period
    dsr = psr(r, sr0 * np.sqrt(ppy), ppy)               # compare on annualised scale
    return float(sr0 * np.sqrt(ppy)), float(dsr)


def block_bootstrap_ci(x: np.ndarray, n_boot: int = 4000, block: int = 10,
                       alpha: float = 0.05, seed: int = 1) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 20:
        return np.nan, np.nan
    nb = int(np.ceil(len(x) / block))
    out = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, len(x) - block, nb)
        out[b] = np.concatenate([x[s:s + block] for s in starts]).mean()
    return float(np.quantile(out, alpha / 2)), float(np.quantile(out, 1 - alpha / 2))


def metrics(r: np.ndarray, ppy: int = 252, n_trials: int = 1) -> dict:
    """r: per-trade R-multiples OR per-period returns. Reports both trade stats
    and (if many observations) time-series style stats."""
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 5:
        return {}
    eq = np.cumsum(r)
    dd = eq - np.maximum.accumulate(eq)
    sr = _ann(pd.Series(r), ppy)
    downside = r[r < 0].std(ddof=1) if (r < 0).sum() > 1 else np.nan
    sr0, dsr = deflated_sharpe(r, n_trials, ppy)
    lo, hi = block_bootstrap_ci(r)
    wins, losses = r[r > 0], r[r <= 0]
    m = {
        "n": len(r),
        "hit_rate": float((r > 0).mean()),
        "expectancy_R": float(r.mean()),
        "median_R": float(np.median(r)),
        "total_R": float(r.sum()),
        "profit_factor": float(wins.sum() / -losses.sum()) if losses.sum() < 0 else np.inf,
        "avg_win_R": float(wins.mean()) if len(wins) else np.nan,
        "avg_loss_R": float(losses.mean()) if len(losses) else np.nan,
        "payoff_ratio": float(wins.mean() / -losses.mean()) if len(losses) and losses.mean() != 0 else np.nan,
        "sharpe_ann": sr,
        "sortino_ann": float(np.sqrt(ppy) * r.mean() / downside) if downside and downside > 0 else np.nan,
        "max_dd_R": float(dd.min()),
        "calmar": float(r.mean() * ppy / abs(dd.min())) if dd.min() < 0 else np.nan,
        "skew": float(stats.skew(r)),
        "kurt": float(stats.kurtosis(r, fisher=False)),
        "PSR_vs_0": psr(r, 0.0, ppy),
        "DSR_n_trials": n_trials,
        "E[maxSR|null]": sr0,
        "DSR": dsr,
        "boot_ci_lo": lo,
        "boot_ci_hi": hi,
        "t_stat": float(stats.ttest_1samp(r, 0).statistic),
        "p_value": float(stats.ttest_1samp(r, 0).pvalue),
    }
    return m


def min_track_record(returns: np.ndarray, target_sr: float = 1.0, ppy: int = 252) -> float:
    """Bailey-LdP minimum track record length (in same units as returns)."""
    r = np.asarray(returns, float)
    r = r[np.isfinite(r)]
    sr = r.mean() / r.std(ddof=1)
    skew, kurt = stats.skew(r), stats.kurtosis(r, fisher=False)
    num = 1 - skew * sr + (kurt - 1) / 4 * sr ** 2
    return float(1 + num * (stats.norm.ppf(0.95) / (target_sr / np.sqrt(ppy) - sr)) ** 2)


# ----------------------------------------------------------------------------
# 4. The actual study: are daily top gainers predictive?
# ----------------------------------------------------------------------------
def build_panel(universe: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for sym, df in universe.items():
        d = df.copy()
        d["ret"] = d.close.pct_change()
        d["symbol"] = sym
        d["class"] = d.asset_class.iloc[0] if isinstance(d.asset_class, pd.Series) else d.asset_class
        rows.append(d[["symbol", "class", "open", "high", "low", "close", "ret", "volume"]])
    return pd.concat(rows).reset_index().rename(columns={"index": "date"})


def top_gainer_study(panel: pd.DataFrame, *, lookback: int = 1, forward: int = 5,
                     quantile: float = 0.7, side_filter: int | None = None) -> dict:
    """For each date and class, rank symbols on trailing `lookback`-day return,
    take the top quantile, and measure the FORWARD `forward`-day return *relative to
    the class mean that day* (so market beta / class drift is removed).
    Also reports the reverse (buy the loser) and short-the-winner legs."""
    p = panel.sort_values(["symbol", "date"]).copy()
    p["trail"] = p.groupby("symbol").ret.transform(
        lambda s: (1 + s).rolling(lookback).apply(np.prod, raw=True) - 1)
    p["fwd"] = p.groupby("symbol").ret.transform(
        lambda s: (1 + s.shift(-1)).rolling(forward).apply(np.prod, raw=True) - 1)
    # shift forward window so entry is next bar (no look-ahead)
    p["fwd"] = p.groupby("symbol").fwd.shift(-(forward - 1))
    p = p.dropna(subset=["trail", "fwd"])

    out = {"vintage_date": None, "slices": []}
    for klass, g in p.groupby("class"):
        g = g.dropna(subset=["trail", "fwd"])
        if g.symbol.nunique() < 2:
            continue
        # cross-sectional demeaning within class-date
        g = g.copy()
        g["xs_mean"] = g.groupby("date").fwd.transform("mean")
        g["excess"] = g.fwd - g.xs_mean
        g["rank"] = g.groupby("date").trail.rank(pct=True)
        top = g[g["rank"] >= quantile]
        bot = g[g["rank"] <= 1 - quantile]

        def stat(frame, sign, label):
            x = sign * frame.excess.values
            lo, hi = block_bootstrap_ci(x)
            t = stats.ttest_1samp(x, 0) if len(x) > 5 else None
            return {"slice": label, "n_obs": int(len(x)),
                    "mean_excess_fwd_ret": float(np.mean(x)) if len(x) else np.nan,
                    "ci_lo": lo, "ci_hi": hi,
                    "t": float(t.statistic) if t else np.nan,
                    "p": float(t.pvalue) if t else np.nan,
                    "hit_rate": float((x > 0).mean()) if len(x) else np.nan}

        out["slices"] += [stat(top, +1, f"{klass}: LONG top-gainer"),
                          stat(top, -1, f"{klass}: SHORT top-gainer"),
                          stat(bot, +1, f"{klass}: LONG top-loser"),
                          stat(bot, -1, f"{klass}: SHORT top-loser")]
        # per-symbol
        for sym, sg in g.groupby("symbol"):
            s_top = sg[sg["rank"] >= quantile]
            s_bot = sg[sg["rank"] <= 1 - quantile]
            out["slices"] += [stat(s_top, +1, f"{klass}/{sym}: LONG after up-move"),
                              stat(s_top, -1, f"{klass}/{sym}: SHORT after up-move"),
                              stat(s_bot, +1, f"{klass}/{sym}: LONG after down-move")]
    df = pd.DataFrame(out["slices"])
    # Benjamini-Hochberg FDR across every slice we just tested
    df["p_adj_BH"] = stats.false_discovery_control(df.p.fillna(1), method="bh")
    df["significant_5pct"] = df.p_adj_BH < 0.05
    return df


# ----------------------------------------------------------------------------
# 5. Purged walk-forward with embargo
# ----------------------------------------------------------------------------
def purged_walk_forward(panel: pd.DataFrame, *, n_folds: int = 5, embargo: int = 10,
                        horizon: int = 5):
    """Yield (train_idx_dates, test_idx_dates) with an embargo gap so overlapping
    labels can't leak. Use for fitting any conditional model (e.g. LightGBM on
    RVOL, gap, float, short interest, news flag)."""
    dates = np.sort(panel.date.unique())
    fold = len(dates) // (n_folds + 1)
    for k in range(1, n_folds + 1):
        train = dates[: k * fold - embargo]
        test = dates[k * fold: (k + 1) * fold]
        yield train, test
