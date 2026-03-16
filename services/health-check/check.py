#!/usr/bin/env python3
"""
autoevolve health check — signal freshness and source balance.

Reads signals.jsonl and prints a health report. Exits 0 if healthy, 1 if
there are warnings (e.g., no self-reported signals for an extended period).

Usage:
    python check.py /path/to/signals.jsonl
    SIGNALS_PATH=/path/to/signals.jsonl python check.py
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter


# ── configuration ────────────────────────────────────────────────────────────
STALENESS_DAYS = 7          # warn if no self-reported signal in this window
WINDOW_DAYS = 7             # "recent" window for the summary

SELF_SOURCES = {"self"}
EXTERNAL_SOURCES = {"discord"}


# ── helpers ──────────────────────────────────────────────────────────────────

def parse_ts(ts_str: str) -> datetime:
    """Parse an ISO-8601 timestamp, tolerant of minor format differences."""
    ts_str = ts_str.replace("Z", "+00:00")
    return datetime.fromisoformat(ts_str)


def load_signals(path: Path) -> list[dict]:
    """Load all valid JSONL entries from the signals file."""
    signals = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                signals.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  [warn] skipping malformed line {lineno}", file=sys.stderr)
    return signals


# ── report ───────────────────────────────────────────────────────────────────

def report(signals: list[dict]) -> bool:
    """Print a health report. Returns True if healthy, False if warnings."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=WINDOW_DAYS)
    warnings: list[str] = []

    print("autoevolve signal health check")
    print("─" * 50)
    print(f"Total signals:   {len(signals)}")

    if not signals:
        warnings.append("Signals file is empty — no data at all.")
        print()
        for w in warnings:
            print(f"  ⚠  {w}")
        return False

    for s in signals:
        s["_ts"] = parse_ts(s["ts"])

    recent = [s for s in signals if s["_ts"] >= window_start]
    print(f"Signals (last {WINDOW_DAYS}d): {len(recent)}")
    print()

    # breakdown by source
    source_counts = Counter(s.get("source", "unknown") for s in signals)
    source_counts_recent = Counter(s.get("source", "unknown") for s in recent)

    print("By source (all time / last 7d):")
    all_sources = sorted(set(source_counts) | set(source_counts_recent))
    for src in all_sources:
        print(f"  {src:20s}  {source_counts[src]:>5d}  /  {source_counts_recent[src]:>5d}")
    print()

    # breakdown by type
    type_counts = Counter(s.get("type", "unknown") for s in signals)
    type_counts_recent = Counter(s.get("type", "unknown") for s in recent)

    print("By type (all time / last 7d):")
    all_types = sorted(set(type_counts) | set(type_counts_recent))
    for t in all_types:
        print(f"  {t:20s}  {type_counts[t]:>5d}  /  {type_counts_recent[t]:>5d}")
    print()

    # last signal per source
    last_by_source: dict[str, datetime] = {}
    for s in signals:
        src = s.get("source", "unknown")
        ts = s["_ts"]
        if src not in last_by_source or ts > last_by_source[src]:
            last_by_source[src] = ts

    print("Last signal per source:")
    for src in sorted(last_by_source):
        ts = last_by_source[src]
        age = now - ts
        age_str = f"{age.days}d {age.seconds // 3600}h ago"
        print(f"  {src:20s}  {ts.strftime('%Y-%m-%d %H:%M UTC'):>22s}  ({age_str})")
    print()

    # ── warnings ──────────────────────────────────────────────────────────

    last_self = None
    for src in SELF_SOURCES:
        if src in last_by_source:
            if last_self is None or last_by_source[src] > last_self:
                last_self = last_by_source[src]

    if last_self is None:
        warnings.append(
            "No self-reported signals found at all — agent may never have "
            "logged signals. Check that the agent's instructions include "
            "signal logging."
        )
    elif (now - last_self).days >= STALENESS_DAYS:
        warnings.append(
            f"No self-reported signals in {(now - last_self).days} days — "
            f"agent may not be logging. Threshold: {STALENESS_DAYS}d."
        )

    last_ext = None
    for src in EXTERNAL_SOURCES:
        if src in last_by_source:
            if last_ext is None or last_by_source[src] > last_ext:
                last_ext = last_by_source[src]

    if last_ext is None:
        warnings.append(
            "No reaction signals found — check that the reaction listener "
            "service is running (systemctl status autoevolve-reactions)."
        )
    elif (now - last_ext).days >= STALENESS_DAYS:
        warnings.append(
            f"No reaction signals in {(now - last_ext).days} days — "
            f"check listener service."
        )

    # Source imbalance
    has_recent_ext = any(s.get("source") in EXTERNAL_SOURCES for s in recent)
    has_recent_self = any(s.get("source") in SELF_SOURCES for s in recent)

    if has_recent_ext and not has_recent_self:
        warnings.append(
            "Reaction signals exist in the last 7 days but zero self-reported "
            "signals — the agent is likely not following signal logging "
            "instructions."
        )

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠  {w}")
    else:
        print("Status: HEALTHY — all signal sources active.")

    return len(warnings) == 0


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        signals_path = Path(sys.argv[1])
    elif os.environ.get("SIGNALS_PATH"):
        signals_path = Path(os.environ["SIGNALS_PATH"])
    else:
        print("Usage: python check.py /path/to/signals.jsonl", file=sys.stderr)
        print("   or: SIGNALS_PATH=/path/to/signals.jsonl python check.py", file=sys.stderr)
        sys.exit(2)

    if not signals_path.exists():
        print(f"Signals file not found: {signals_path}", file=sys.stderr)
        sys.exit(2)

    signals = load_signals(signals_path)
    healthy = report(signals)
    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
