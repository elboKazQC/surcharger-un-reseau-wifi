from __future__ import annotations

import argparse
import asyncio
import logging
from .config import load_config
from .runner import LoadTestRunner


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Wifi network load tester")
    p.add_argument("--config", required=True, help="YAML configuration file")
    p.add_argument("--dry-run", action="store_true", help="Only show what would run")
    p.add_argument("--output", help="Override output directory")
    p.add_argument(
        "--internal-only", action="store_true", help="Ignore iperf3 even if available"
    )
    p.add_argument(
        "--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    cfg = load_config(args.config)
    if args.output:
        cfg.global_.output_dir = args.output
    runner = LoadTestRunner(cfg, dry_run=bool(args.dry_run), internal_only=args.internal_only)
    reporter = asyncio.run(runner.run())
    print(f"Rapport écrit: {reporter.path}")


if __name__ == "__main__":  # pragma: no cover
    main()
