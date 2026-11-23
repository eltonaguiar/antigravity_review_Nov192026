"""Shared, unit-tested portfolio metrics.

Exists because four separate errors in one agent's fund comparison all came from writing CAGR/Sharpe/Sortino
inline: the expense ratio was subtracted from a series that was already net of it, Sharpe was computed with
rf=0 (a T-bill fund then showed Sharpe 13.6), Sortino divided downside deviation by the count of DOWN days
instead of ALL days, and a rebalance parameter was accepted and never used. Each of those is impossible here
because the function signature does not allow it.

Conventions, stated once so every caller inherits them:
  * prices must be an ADJUSTED (total-return) series - already net of expense ratio, already dividend-reinvested.
    This module therefore NEVER subtracts an expense ratio. If you have raw NAV, adjust it first.
  * Sharpe takes an explicit risk-free rate; there is no rf=0 default.
  * Sortino downside deviation divides by the TOTAL observation count, per Sortino's definition.
  * rebalance() actually rebalances, and charges cost when you tell it to.
"""
import math

TRADING_DAYS = 252


def _check(px):
    if not px or len(px) < 3:
        raise ValueError("need at least 3 price observations")
    if any(p is None or p <= 0 for p in px):
        raise ValueError("prices must all be positive and non-None")
    return px


def returns(px):
    px = _check(px)
    return [px[i] / px[i - 1] - 1.0 for i in range(1, len(px))]


def cagr(px, *, periods_per_year=TRADING_DAYS):
    """Compound annual growth rate of an ADJUSTED series. No fee adjustment - the series is already net.

    periods_per_year is keyword-only on purpose: as a second positional argument it would silently swallow an
    expense ratio, which is exactly the double-count this module exists to prevent.
    """
    px = _check(px)
    years = (len(px) - 1) / float(periods_per_year)
    if years <= 0:
        raise ValueError("series too short for a CAGR")
    return (px[-1] / px[0]) ** (1.0 / years) - 1.0


def annual_vol(px, periods_per_year=TRADING_DAYS):
    r = returns(px)
    mu = sum(r) / len(r)
    var = sum((x - mu) ** 2 for x in r) / (len(r) - 1)
    return math.sqrt(var) * math.sqrt(periods_per_year)


def sharpe(px, rf_annual, periods_per_year=TRADING_DAYS):
    """EXCESS-return Sharpe. rf_annual is required: a T-bill fund must score ~0, not 13.6."""
    if rf_annual is None:
        raise ValueError("rf_annual is required; there is no rf=0 default")
    r = returns(px)
    rf_daily = (1.0 + rf_annual) ** (1.0 / periods_per_year) - 1.0
    ex = [x - rf_daily for x in r]
    mu = sum(ex) / len(ex)
    var = sum((x - mu) ** 2 for x in ex) / (len(ex) - 1)
    sd = math.sqrt(var)
    if sd < 1e-9:
        # No measurable excess volatility: the ratio is 0/0 and its value is noise amplification, not skill.
        # This is the SGOV case - with rf=0 the same series reported Sharpe 13.6 and 1.9e13 in tests.
        return 0.0
    return (mu / sd) * math.sqrt(periods_per_year)


def sortino(px, target_annual=0.0, periods_per_year=TRADING_DAYS):
    """Sortino with downside deviation over ALL observations against a target return (not over down days, not vs 0)."""
    r = returns(px)
    tgt = (1.0 + target_annual) ** (1.0 / periods_per_year) - 1.0
    excess = [x - tgt for x in r]
    dd = math.sqrt(sum(min(x, 0.0) ** 2 for x in excess) / len(excess))
    mu = sum(excess) / len(excess)
    if dd < 1e-9:
        return 0.0
    return (mu / dd) * math.sqrt(periods_per_year)


def max_drawdown(px):
    px = _check(px)
    peak = px[0]
    worst = 0.0
    for p in px:
        peak = max(peak, p)
        worst = min(worst, p / peak - 1.0)
    return worst


def rebalance(daily_returns_by_asset, weights, every_n_days=21, cost_bps=0.0):
    """Weighted portfolio that ACTUALLY rebalances every n periods, charging cost_bps on turnover.

    Without rebalancing the portfolio drifts; treating a fixed-weight sum of daily returns as the portfolio
    return silently assumes costless DAILY rebalancing, which is the defect this function exists to remove.
    """
    if not weights:
        raise ValueError("weights required")
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError("weights must sum to 1.0 (got %.6f)" % total)
    names = list(weights)
    n = len(daily_returns_by_asset[names[0]])
    for nm in names:
        if len(daily_returns_by_asset[nm]) != n:
            raise ValueError("all return series must be the same length")
    w = dict(weights)
    eq = 1.0
    curve = [eq]
    for i in range(n):
        port_r = sum(w[nm] * daily_returns_by_asset[nm][i] for nm in names)
        eq *= (1.0 + port_r)
        curve.append(eq)
        # drift the weights with realised performance
        grown = {nm: w[nm] * (1.0 + daily_returns_by_asset[nm][i]) for nm in names}
        s = sum(grown.values())
        w = {nm: grown[nm] / s for nm in names}
        if every_n_days and (i + 1) % every_n_days == 0:
            turnover = sum(abs(weights[nm] - w[nm]) for nm in names) / 2.0
            eq *= (1.0 - turnover * cost_bps / 1e4)
            curve[-1] = eq
            w = dict(weights)
    return curve
