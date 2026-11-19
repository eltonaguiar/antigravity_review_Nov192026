"""Tests for the audit2 forward-sidecar aggregator.

The page must distinguish "no rows yet" from "cannot load", and a registered
pod with zero rows must stay visible rather than vanish from the table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.audit2_forward_summary import summarize  # noqa: E402


def _row(**kw):
    base = {"hypothesis_id": "H-119", "pod": "POD-CRYPTO", "symbol": "BTCUSDT",
            "benchmark_leg_ret": 0.01, "intrabar_first_touch": True}
    base.update(kw)
    return base


def _write(tmp_path: Path, rows) -> Path:
    p = tmp_path / "forward.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return p


def test_missing_file_is_empty_not_an_error(tmp_path):
    out = summarize(tmp_path / "absent.jsonl", generated_at="2026-11-19T00:00:00Z")
    assert out["n_rows"] == 0
    assert out["by_hypothesis"] == {}
    assert out["generated_at"] == "2026-11-19T00:00:00Z"


def test_counts_benchmark_and_intrabar_coverage(tmp_path):
    rows = [
        _row(benchmark_leg_ret=0.01, intrabar_first_touch=True),
        _row(benchmark_leg_ret=None, intrabar_first_touch=True),
        _row(benchmark_leg_ret=0.02, intrabar_first_touch=False),
    ]
    out = summarize(_write(tmp_path, rows), generated_at="2026-11-19T00:00:00Z")
    h = out["by_hypothesis"]["H-119"]
    assert out["n_rows"] == 3
    assert h == {"n": 3, "benchmark_leg": 2, "intrabar": 2, "pods": ["POD-CRYPTO"]}


def test_hypotheses_are_separated_and_pods_deduped(tmp_path):
    rows = [
        _row(hypothesis_id="H-119", pod="POD-A"),
        _row(hypothesis_id="H-119", pod="POD-A"),
        _row(hypothesis_id="H-EQUITY", pod="POD-B", benchmark_leg_ret=None),
        _row(hypothesis_id=None, pod=None),
    ]
    out = summarize(_write(tmp_path, rows), generated_at="2026-11-19T00:00:00Z")
    assert set(out["by_hypothesis"]) == {"H-119", "H-EQUITY", "?"}
    assert out["by_hypothesis"]["H-119"]["pods"] == ["POD-A"]
    assert out["by_hypothesis"]["H-EQUITY"]["benchmark_leg"] == 0


def test_malformed_lines_are_skipped_not_fatal(tmp_path):
    p = tmp_path / "forward.jsonl"
    p.write_text('{"hypothesis_id":"H-119","benchmark_leg_ret":0.1}\n'
                 'not json\n'
                 '[1,2,3]\n'
                 '\n', encoding="utf-8")
    out = summarize(p, generated_at="2026-11-19T00:00:00Z")
    assert out["n_rows"] == 1
    assert out["by_hypothesis"]["H-119"]["n"] == 1


def test_written_sidecar_is_json_safe(tmp_path):
    from tools.audit2_forward_summary import main
    src = _write(tmp_path, [_row()])
    dst = tmp_path / "sidecar.json"
    assert main(["--src", str(src), "--out", str(dst)]) == 0
    payload = json.loads(dst.read_text(encoding="utf-8"))
    assert payload["n_rows"] == 1
    assert payload["by_hypothesis"]["H-119"]["benchmark_leg"] == 1
