"""Mode stress: escalade automatique jusqu'à critères d'arrêt.

Usage principal via script d'entrée `loadtester-stress`.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from .metrics import run_ping, sample_resources
from .generator import generate_traffic
from .iperf import run_iperf


@dataclass
class StressResult:
    level: int
    protocol: str
    target_mbps: float
    achieved_mbps: float
    latency_ms: float
    jitter_ms: float
    loss_pct: float
    cpu_pct: float
    mem_pct: float
    status: str  # OK | WARN | FAIL


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stress test automatique réseau")
    p.add_argument("--host", required=True, help="Hôte cible")
    p.add_argument("--ping-host", help="Hôte ping (défaut = host)")
    p.add_argument("--start-mbps", type=float, default=5)
    p.add_argument("--step-mbps", type=float, default=10)
    p.add_argument("--max-mbps", type=float, default=200)
    p.add_argument("--duration", type=int, default=15, help="Durée par palier (s)")
    p.add_argument("--protocol", choices=["UDP", "TCP", "BOTH"], default="UDP")
    p.add_argument("--connections", type=int, default=4)
    p.add_argument("--packet-size", type=int, default=1024)
    p.add_argument("--loss-threshold", type=float, default=10.0)
    p.add_argument("--latency-threshold", type=float, default=200.0)
    p.add_argument("--min-ratio", type=float, default=0.6, help="Achieved/Target minimal acceptable avant FAIL")
    p.add_argument("--output-dir", default="reports")
    p.add_argument("--no-iperf", action="store_true")
    p.add_argument("--log-level", default="INFO")
    return p.parse_args()


async def run_level(idx: int, proto: str, target: float, args) -> StressResult:
    duration = args.duration
    ping_task = asyncio.create_task(run_ping(args.ping_host or args.host, count=4))
    res_task = asyncio.create_task(sample_resources(1.0, duration))
    achieved = 0.0
    jitter = 0.0
    loss = 0.0
    if proto == "UDP" or proto == "TCP":
        if not args.no_iperf:
            iperf_res = await run_iperf(args.host, duration, proto, args.connections)
            if iperf_res:
                achieved = iperf_res.mbps
                if proto == "UDP":
                    jitter = iperf_res.jitter_ms or 0.0
                    loss = iperf_res.packet_loss_pct or 0.0
        if achieved == 0.0:
            # fallback interne
            stats = await generate_traffic(
                proto,
                args.host,
                5201 if proto == "TCP" else 5202,
                args.packet_size,
                target,
                args.connections,
                duration,
            )
            achieved = stats.mbps
    ping_res = await ping_task
    res_sample = await res_task
    jitter = jitter or ping_res.jitter_ms
    # Décision statut
    ratio = achieved / target if target > 0 else 0
    status = "OK"
    if (loss > args.loss_threshold or ping_res.avg_latency_ms > args.latency_threshold or ratio < args.min_ratio):
        status = "FAIL"
    elif (loss > args.loss_threshold * 0.5 or ping_res.avg_latency_ms > args.latency_threshold * 0.6 or ratio < (args.min_ratio + 0.15)):
        status = "WARN"
    return StressResult(
        level=idx,
        protocol=proto,
        target_mbps=target,
        achieved_mbps=achieved,
        latency_ms=ping_res.avg_latency_ms,
        jitter_ms=jitter,
        loss_pct=loss or ping_res.packet_loss_pct,
        cpu_pct=res_sample.cpu_pct,
        mem_pct=res_sample.mem_pct,
        status=status,
    )


async def stress(args) -> list[StressResult]:
    results: list[StressResult] = []
    level = 0
    current = args.start_mbps
    protocols = [args.protocol] if args.protocol != "BOTH" else ["UDP", "TCP"]
    while current <= args.max_mbps:
        for proto in protocols:
            level += 1
            logging.info("Palier %s %s %.1f Mbps", level, proto, current)
            r = await run_level(level, proto, current, args)
            results.append(r)
            logging.info("Résultat: %.1f/%.1f Mbps latency=%.1fms loss=%.2f%% status=%s", r.achieved_mbps, r.target_mbps, r.latency_ms, r.loss_pct, r.status)
            if r.status == "FAIL":
                logging.warning("Critère d'arrêt atteint (status FAIL). Fin.")
                return results
        current += args.step_mbps
    return results


def write_report(results: list[StressResult], output_dir: str) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / ("stress_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S") + ".csv")
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["level", "protocol", "target_mbps", "achieved_mbps", "latency_ms", "jitter_ms", "loss_pct", "cpu_pct", "mem_pct", "status"])
        for r in results:
            w.writerow([
                r.level,
                r.protocol,
                f"{r.target_mbps:.2f}",
                f"{r.achieved_mbps:.2f}",
                f"{r.latency_ms:.2f}",
                f"{r.jitter_ms:.2f}",
                f"{r.loss_pct:.2f}",
                f"{r.cpu_pct:.2f}",
                f"{r.mem_pct:.2f}",
                r.status,
            ])
    return path


def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="[%(levelname)s] %(message)s")
    args.ping_host = args.ping_host or args.host
    results = asyncio.run(stress(args))
    path = write_report(results, args.output_dir)
    print(f"Rapport stress écrit: {path}")
    # Résumé console
    worst = next((r for r in results if r.status == 'FAIL'), None)
    if worst:
        print(f"Arrêt sur FAIL niveau {worst.level} ({worst.protocol}) à {worst.target_mbps} Mbps")
    else:
        print("Aucun FAIL atteint (max atteint).")


if __name__ == "__main__":  # pragma: no cover
    main()
