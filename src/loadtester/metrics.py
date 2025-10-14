from __future__ import annotations

import asyncio
import platform
import re
import statistics
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import psutil


@dataclass
class PingResult:
    avg_latency_ms: float
    jitter_ms: float
    packet_loss_pct: float


async def run_ping(host: str, count: int = 4, timeout: int = 4) -> PingResult:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    text = stdout.decode(errors="ignore")
    # Extract numbers
    latencies = [float(x) for x in re.findall(r"time[=<]([0-9.]+)ms", text)]
    if latencies:
        avg_latency = statistics.mean(latencies)
        jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0.0
    else:
        avg_latency = float("nan")
        jitter = float("nan")
    # Packet loss
    m = re.search(r"(\d+)%\s*loss", text)
    if not m:
        m = re.search(r"(\d+\.\d+)% packet loss", text)
    packet_loss = float(m.group(1)) if m else 0.0
    return PingResult(avg_latency, jitter, packet_loss)


@dataclass
class ResourceSample:
    cpu_pct: float
    mem_pct: float


async def sample_resources(interval: float, duration: float) -> ResourceSample:
    cpu_values = []
    mem_values = []
    start = time.time()
    while time.time() - start < duration:
        cpu_values.append(psutil.cpu_percent(interval=None))
        mem_values.append(psutil.virtual_memory().percent)
        await asyncio.sleep(interval)
    def avg(values):
        return sum(values) / len(values) if values else 0.0
    return ResourceSample(avg(cpu_values), avg(mem_values))


__all__ = ["PingResult", "run_ping", "ResourceSample", "sample_resources"]
