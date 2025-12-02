#!/usr/bin/env python3
"""
Simple utility to compute net PnL by option type (CE / PE) from a trades log.

Usage:
    python tools/pnl_by_type.py path/to/trades.log

Outputs a short summary of total PnL and counts for CE and PE trades.
"""
from __future__ import annotations

import argparse
import re
from typing import Dict, Tuple


PNL_RE = re.compile(r"\|\s*(?P<symbol>\S+)\s*\|.*?PnL:\s*(?P<pnl>[-+]?[0-9]+(?:\.[0-9]+)?)")


def parse_pnl_lines(lines) -> Dict[str, Dict[str, float]]:
    """Parse an iterable of lines and return aggregated PnL and counts for CE and PE.

    Returns a dict like:
        { 'CE': {'pnl': 123.0, 'count': 5}, 'PE': {'pnl': -10.25, 'count': 6} }
    """
    agg = {"CE": {"pnl": 0.0, "count": 0}, "PE": {"pnl": 0.0, "count": 0}}

    for ln in lines:
        m = PNL_RE.search(ln)
        if not m:
            continue
        symbol = m.group("symbol")
        pnl = float(m.group("pnl"))
        # classify by trailing token CE or PE (symbol may include other chars)
        if symbol.endswith("CE"):
            agg["CE"]["pnl"] += pnl
            agg["CE"]["count"] += 1
        elif symbol.endswith("PE"):
            agg["PE"]["pnl"] += pnl
            agg["PE"]["count"] += 1

    return agg


def format_summary(agg: Dict[str, Dict[str, float]]) -> str:
    ce = agg.get("CE", {"pnl": 0.0, "count": 0})
    pe = agg.get("PE", {"pnl": 0.0, "count": 0})
    total = ce["pnl"] + pe["pnl"]
    return (
        f"CE: total_pnl={ce['pnl']:.2f}, trades={int(ce['count'])}\n"
        f"PE: total_pnl={pe['pnl']:.2f}, trades={int(pe['count'])}\n"
        f"TOTAL: {total:.2f}\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Compute CE / PE PnL from trades.log")
    parser.add_argument("path", help="Path to trades.log file")
    args = parser.parse_args()

    with open(args.path, "r", encoding="utf-8") as fh:
        agg = parse_pnl_lines(fh)

    print(format_summary(agg))


if __name__ == "__main__":
    main()
