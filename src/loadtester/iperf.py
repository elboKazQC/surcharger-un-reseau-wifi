from __future__ import annotations

import asyncio
import json
import shutil
from dataclasses import dataclass
from typing import Optional


@dataclass
class IperfResult:
    mbps: float
    jitter_ms: float | None = None
    packet_loss_pct: float | None = None


async def run_iperf(
    host: str,
    duration_s: int,
    protocol: str,
    connections: int,
) -> IperfResult | None:
    if not shutil.which("iperf3"):
        return None
    args = ["iperf3", "-c", host, "-J", "-t", str(duration_s), "-P", str(connections)]
    if protocol.upper() == "UDP":
        args.extend(["-u"])
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    out, _ = await proc.communicate()
    try:
        data = json.loads(out.decode(errors="ignore"))
        end = data.get("end", {})
        if protocol.upper() == "UDP":
            streams = end.get("streams", [])
            if streams:
                s0 = streams[0].get("udp", {})
                mbps = s0.get("bits_per_second", 0) / 1_000_000
                jitter_ms = s0.get("jitter_ms")
                lost_percent = s0.get("lost_percent")
                return IperfResult(mbps, jitter_ms, lost_percent)
        else:
            sum_received = end.get("sum_received", {})
            mbps = sum_received.get("bits_per_second", 0) / 1_000_000
            return IperfResult(mbps)
    except Exception:
        return None


__all__ = ["run_iperf", "IperfResult"]
