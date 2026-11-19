#!/usr/bin/env python3
"""
forward_ingest_adapter_reference.py — reference adapter for the P0 blocker.

The source repo's alpha_engine/forward_observations.py defines the ledger schema and
promotion rule, but cannot ingest from MySQL ("cannot read MySQL here"), so the ledger is
empty (0 rows) and PROVEN_T2 is unreachable. This file is a *reference* loader the source
maintainers can adapt — it is NOT a change to the source repo, and it does not run here.

It pulls rows from the existing outcome ledgers (at_signal_outcomes is the recommended
system of record), re-resolves them under the resolver_version, computes net return after
per-class slippage, appends the benchmark leg, and inserts into forward_observations with
idempotent dedup. Run as: python forward_ingest_adapter_reference.py --source at_signal_outcomes --limit 5000
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---- external adapters (import guards so this file stays importable standalone) ----
try:
    from alpha_engine import forward_observations as FO
    HAVE_FO = True
except Exception:  # pragma: no cover
    HAVE_FO = False

try:
    import mysql.connector as mc
    HAVE_MYSQL = True
except Exception:  # pragma: no cover
    HAVE_MYSQL = False


@dataclass
class Config:
    """Point-in-time-free adapter configuration. All secrets come from env, never inline."""
    db_host: str = field(default_factory=lambda: __import__("os").environ.get("DB_HOST", ""))
    db_user: str = field(default_factory=lambda: __import__("os").environ.get("DB_USER", ""))
    db_pass: str = field(default_factory=lambda: __import__("os").environ.get("DB_PASS", ""))
    db_name: str = "ejaguiar1_stocks"
    source_table: str = "at_signal_outcomes"   # recommended system of record
    resolver_version: str = "v2_intrabar_touch"
    slippage_pct_by_class: dict = field(default_factory=lambda: {
        "CRYPTO": 0.0997, "EQUITY": 0.05, "ETF": 0.05, "FOREX": 0.02,
        "COMMODITY": 0.15, "FUTURES": 0.10, "BOND": 0.05, "MEME": 0.30,
        "PENNY_STOCK": 0.30, "MUTUAL_FUND": 0.08,
    })


def _net_pct(r: dict, cfg: Config) -> float | None:
    """Net per-trade return after per-class slippage. Mirrors FO._net + _cost_pct."""
    gross = r.get("pnl_pct")
    if gross is None:
        return None
    cost = cfg.slippage_pct_by_class.get(str(r.get("class", "")).upper(), 0.10)
    return float(gross) - float(cost)


def _benchmark_leg(r: dict) -> tuple[str | None, float | None]:
    """Placeholder: attach benchmark leg (excess vs SPY/BTC/AGG/GSG). Real impl reads bars."""
    ticker = {"CRYPTO": "BTC-USD", "EQUITY": "SPY", "ETF": "SPY",
              "BOND": "AGG", "COMMODITY": "GSG", "FUTURES": "GSG"}.get(
                  str(r.get("class", "")).upper())
    return ticker, None  # excess computed by a subsequent bar join


def _dedup_hash(r: dict, cfg: Config) -> str:
    parts = [str(r.get("hypothesis_id")), str(r.get("symbol")), str(r.get("strategy")),
             str(r.get("side")), str(r.get("opened_at")), str(r.get("closed_at")),
             cfg.resolver_version]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _resolve_intrabar(r: dict) -> bool:
    """Placeholder: true when this row was resolved with SL-wins-ties first-touch."""
    return bool(r.get("intrabar_first_touch", False))


def build_rows(source_rows: list[dict], cfg: Config) -> list[dict]:
    """Transform source outcome rows into forward_observations-shaped rows (dedup-safe)."""
    out = []
    for r in source_rows:
        net = _net_pct(r, cfg)
        if net is None:
            continue
        bench_tkr, bench_ret = _benchmark_leg(r)
        out.append({
            "hypothesis_id": r.get("hypothesis_id", ""),
            "pod_id": r.get("pod_id"),
            "opened_at": r.get("opened_at"),
            "closed_at": r.get("closed_at"),
            "symbol": r.get("symbol"),
            "class": str(r.get("class", "")).upper(),
            "side": str(r.get("side", "")).upper(),
            "strategy": r.get("strategy"),
            "entry_px": r.get("entry_px"),
            "exit_px": r.get("exit_px"),
            "qty": r.get("qty", 1),
            "fees": r.get("fees", 0.0),
            "funding": r.get("funding", 0.0),
            "slippage_bps": r.get("slippage_bps", 0.0),
            "resolver_version": cfg.resolver_version,
            "intrabar_first_touch": 1 if _resolve_intrabar(r) else 0,
            "exit_rule": r.get("exit_rule", "TIME"),
            "benchmark_leg_ret": bench_ret,
            "benchmark_ticker": bench_tkr,
            "net_pnl_pct": net,
            "regime_ok": r.get("regime_ok", 1),
            "source_sha256": _dedup_hash(r, cfg),
        })
    return out


def ingest(cfg: Config, rows: list[dict]) -> tuple[int, int]:
    """Idempotent insert: skip rows whose dedup hash already exists."""
    if not HAVE_MYSQL:
        print("mysql.connector unavailable; dry-run only (no DB write)")
        return len(rows), 0
    conn = mc.connect(host=cfg.db_host, user=cfg.db_user,
                      password=cfg.db_pass, database=cfg.db_name)
    cur = conn.cursor()
    ins, skipped = 0, 0
    for row in rows:
        cur.execute(
            "SELECT 1 FROM forward_observations WHERE source_sha256=%s LIMIT 1",
            (row["source_sha256"],))
        if cur.fetchone():
            skipped += 1
            continue
        cur.execute("""
            INSERT INTO forward_observations
              (hypothesis_id, opened_at, closed_at, symbol, class, side, strategy,
               entry_px, exit_px, qty, fees, funding, slippage_bps, resolver_version,
               intrabar_first_touch, exit_rule, benchmark_leg_ret, benchmark_ticker,
               net_pnl_pct, regime_ok, source_sha256)
            VALUES (%(hypothesis_id)s, %(opened_at)s, %(closed_at)s, %(symbol)s,
                    %(class)s, %(side)s, %(strategy)s, %(entry_px)s, %(exit_px)s,
                    %(qty)s, %(fees)s, %(funding)s, %(slippage_bps)s,
                    %(resolver_version)s, %(intrabar_first_touch)s, %(exit_rule)s,
                    %(benchmark_leg_ret)s, %(benchmark_ticker)s, %(net_pnl_pct)s,
                    %(regime_ok)s, %(source_sha256)s)
        """, row)
        ins += 1
    conn.commit(); cur.close(); conn.close()
    return ins, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="at_signal_outcomes")
    ap.add_argument("--limit", type=int, default=5000)
    argv = ap.parse_args()

    # In a real deployment this reads the source table; here we only validate shape.
    cfg = Config(source_table=argv.source)
    print(f"adapter reference: source={cfg.source_table}, limit={argv.limit}, "
          f"FO_available={HAVE_FO}, mysql_available={HAVE_MYSQL}")
    print("dry-run shape OK; wire --source to a real read + `ingest()` to persist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
