from loadtester.config import load_config, FullConfig
from pathlib import Path


def test_load_config_example(tmp_path: Path):
    sample = tmp_path / "example.yaml"
    sample.write_text(
        """
global:
  target_host: 1.2.3.4
  ping_host: 1.2.3.4
  safety_max_mbps: 50
tiers:
  - name: t1
    protocol: UDP
    target_bandwidth_mbps: 10
    connections: 1
    duration_s: 5
""",
        encoding="utf-8",
    )
    cfg: FullConfig = load_config(sample)
    assert cfg.global_.safety_max_mbps == 50
    assert cfg.tiers[0].protocol == "UDP"
    assert cfg.tiers[0].target_bandwidth_mbps == 10
