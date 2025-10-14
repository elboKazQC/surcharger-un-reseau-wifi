from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.progress import Progress, TimeElapsedColumn, BarColumn, TextColumn

from .config import FullConfig, TierConfig
from .generator import generate_traffic, TrafficStats
from .iperf import run_iperf
from .metrics import run_ping, sample_resources
from .report import CsvReporter, TierReportRow


class LoadTestRunner:
    def __init__(self, cfg: FullConfig, dry_run: bool = False, internal_only: bool = False):
        self.cfg = cfg
        self.dry_run = dry_run
        self.internal_only = internal_only

    async def run(self) -> CsvReporter:
        report_path = Path(self.cfg.global_.output_dir) / (
            "report_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S") + ".csv"
        )
        reporter = CsvReporter(report_path)

        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            for tier in self.cfg.tiers:
                task_id = progress.add_task(f"[cyan]Tier {tier.name}", total=tier.duration_s)
                if self.dry_run:
                    progress.advance(task_id, tier.duration_s)
                    reporter.add(
                        TierReportRow(
                            timestamp_start=datetime.utcnow().isoformat(),
                            tier_name=tier.name,
                            protocol=tier.protocol,
                            target_mbps=tier.target_bandwidth_mbps,
                            achieved_mbps=0.0,
                            latency_ms_avg=0.0,
                            jitter_ms=0.0,
                            packet_loss_pct=0.0,
                            cpu_pct_avg=0.0,
                            mem_pct_avg=0.0,
                        )
                    )
                    continue
                # run ping concurrently with traffic and resource sampling
                ping_task = asyncio.create_task(run_ping(self.cfg.global_.ping_host, count=4))
                res_task = asyncio.create_task(sample_resources(interval=1.0, duration=tier.duration_s))

                # Try iperf
                achieved_mbps = 0.0
                jitter_ms = 0.0
                packet_loss_pct = 0.0
                if self.cfg.global_.use_iperf_if_available and not self.internal_only:
                    iperf_result = await run_iperf(
                        self.cfg.global_.target_host, tier.duration_s, tier.protocol, tier.connections
                    )
                    if iperf_result:
                        achieved_mbps = iperf_result.mbps
                        jitter_ms = iperf_result.jitter_ms or 0.0
                        packet_loss_pct = iperf_result.packet_loss_pct or 0.0
                if achieved_mbps == 0.0:  # fallback internal
                    traffic_task = asyncio.create_task(
                        generate_traffic(
                            tier.protocol,
                            self.cfg.global_.target_host,
                            5201 if tier.protocol == "TCP" else 5202,
                            tier.packet_size,
                            tier.target_bandwidth_mbps,
                            tier.connections,
                            tier.duration_s,
                        )
                    )
                else:
                    traffic_task = asyncio.create_task(asyncio.sleep(tier.duration_s))

                start_time = datetime.utcnow().isoformat()
                # progress update loop
                for _ in range(tier.duration_s):
                    await asyncio.sleep(1)
                    progress.advance(task_id, 1)

                traffic_stats: TrafficStats | None = None
                if achieved_mbps == 0.0:
                    traffic_stats = await traffic_task
                    if traffic_stats:
                        achieved_mbps = traffic_stats.mbps
                else:
                    await traffic_task
                ping_res = await ping_task
                res_sample = await res_task

                reporter.add(
                    TierReportRow(
                        timestamp_start=start_time,
                        tier_name=tier.name,
                        protocol=tier.protocol,
                        target_mbps=tier.target_bandwidth_mbps,
                        achieved_mbps=achieved_mbps,
                        latency_ms_avg=ping_res.avg_latency_ms,
                        jitter_ms=jitter_ms or ping_res.jitter_ms,
                        packet_loss_pct=packet_loss_pct or ping_res.packet_loss_pct,
                        cpu_pct_avg=res_sample.cpu_pct,
                        mem_pct_avg=res_sample.mem_pct,
                    )
                )

        reporter.write()
        return reporter


__all__ = ["LoadTestRunner"]
