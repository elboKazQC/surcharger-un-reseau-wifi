from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import List, Any, Dict


@dataclass
class GlobalConfig:
    target_host: str
    ping_host: str
    safety_max_mbps: float
    output_dir: str = "reports"
    use_iperf_if_available: bool = True


@dataclass
class TierConfig:
    name: str
    protocol: str  # UDP or TCP
    target_bandwidth_mbps: float
    connections: int
    duration_s: int
    packet_size: int = 512


@dataclass
class FullConfig:
    global_: GlobalConfig
    tiers: List[TierConfig]

    @property
    def total_max_bandwidth(self) -> float:
        return max((t.target_bandwidth_mbps for t in self.tiers), default=0)


def load_config(path: str | Path) -> FullConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    g = data.get("global", {})
    global_cfg = GlobalConfig(
        target_host=g["target_host"],
        ping_host=g.get("ping_host", g["target_host"]),
        safety_max_mbps=float(g.get("safety_max_mbps", 100)),
        output_dir=g.get("output_dir", "reports"),
        use_iperf_if_available=bool(g.get("use_iperf_if_available", True)),
    )
    tiers_raw: List[Dict[str, Any]] = data.get("tiers", [])
    tiers: List[TierConfig] = []
    for t in tiers_raw:
        tiers.append(
            TierConfig(
                name=t["name"],
                protocol=t["protocol"].upper(),
                target_bandwidth_mbps=float(t["target_bandwidth_mbps"]),
                connections=int(t.get("connections", 1)),
                duration_s=int(t.get("duration_s", 30)),
                packet_size=int(t.get("packet_size", 512)),
            )
        )
    cfg = FullConfig(global_cfg, tiers)
    # Safety validation per tier vs global safety limit
    for tier in cfg.tiers:
        if tier.target_bandwidth_mbps > cfg.global_.safety_max_mbps:
            raise ValueError(
                f"Tier {tier.name} bandwidth {tier.target_bandwidth_mbps} Mbps dépasse safety_max_mbps {cfg.global_.safety_max_mbps}"
            )
    return cfg


__all__ = ["GlobalConfig", "TierConfig", "FullConfig", "load_config"]
