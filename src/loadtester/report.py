from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class TierReportRow:
    timestamp_start: str
    tier_name: str
    protocol: str
    target_mbps: float
    achieved_mbps: float
    latency_ms_avg: float
    jitter_ms: float
    packet_loss_pct: float
    cpu_pct_avg: float
    mem_pct_avg: float


class CsvReporter:
    def __init__(self, path: Path):
        self.path = path
        self.rows: List[TierReportRow] = []

    def add(self, row: TierReportRow):
        self.rows.append(row)

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp_start",
                "tier_name",
                "protocol",
                "target_mbps",
                "achieved_mbps",
                "latency_ms_avg",
                "jitter_ms",
                "packet_loss_pct",
                "cpu_pct_avg",
                "mem_pct_avg",
            ])
            for r in self.rows:
                writer.writerow([
                    r.timestamp_start,
                    r.tier_name,
                    r.protocol,
                    f"{r.target_mbps:.2f}",
                    f"{r.achieved_mbps:.2f}",
                    f"{r.latency_ms_avg:.2f}",
                    f"{r.jitter_ms:.2f}",
                    f"{r.packet_loss_pct:.2f}",
                    f"{r.cpu_pct_avg:.2f}",
                    f"{r.mem_pct_avg:.2f}",
                ])


__all__ = ["TierReportRow", "CsvReporter"]
