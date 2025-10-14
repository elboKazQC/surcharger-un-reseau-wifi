"""Serveur de réception UDP/TCP pour mesurer trafic réellement reçu.

UDP: Attend des paquets avec optionnel numéro de séquence 8 octets (big-endian).
TCP: Compte octets agrégés toutes les N secondes.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import sys


@dataclass
class IntervalStats:
    ts: datetime
    udp_packets: int
    udp_bytes: int
    udp_loss_est: int
    tcp_bytes: int


class Receiver:
    def __init__(self, udp_port: int, tcp_port: int | None, interval: int, output: str | None):
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.interval = interval
        self.output = output
        self.udp_packets = 0
        self.udp_bytes = 0
        self.udp_last_seq: int | None = None
        self.udp_loss = 0
        self.tcp_bytes = 0
        self.stats: list[IntervalStats] = []

    async def start(self):
        loop = asyncio.get_running_loop()
        # UDP
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self._UDPProtocol(self), ("0.0.0.0", self.udp_port)
        )
        # TCP
        if self.tcp_port:
            server = await asyncio.start_server(self._handle_tcp, host="0.0.0.0", port=self.tcp_port)
        else:
            server = None
        print(f"[Receiver] UDP port {self.udp_port} | TCP port {self.tcp_port or '-'} | interval {self.interval}s")
        try:
            while True:
                await asyncio.sleep(self.interval)
                self._snapshot()
        except asyncio.CancelledError:
            pass
        finally:
            transport.close()
            if server:
                server.close()
                await server.wait_closed()
            self._write()

    class _UDPProtocol(asyncio.DatagramProtocol):
        def __init__(self, outer: 'Receiver'):
            self.outer = outer

        def datagram_received(self, data: bytes, addr):
            self.outer.udp_packets += 1
            self.outer.udp_bytes += len(data)
            if len(data) >= 8:
                seq = int.from_bytes(data[:8], 'big', signed=False)
                if self.outer.udp_last_seq is not None and seq > self.outer.udp_last_seq + 1:
                    self.outer.udp_loss += (seq - self.outer.udp_last_seq - 1)
                self.outer.udp_last_seq = seq

    async def _handle_tcp(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break
                self.tcp_bytes += len(data)
        finally:
            writer.close()
            await writer.wait_closed()

    def _snapshot(self):
        stats = IntervalStats(
            ts=datetime.utcnow(),
            udp_packets=self.udp_packets,
            udp_bytes=self.udp_bytes,
            udp_loss_est=self.udp_loss,
            tcp_bytes=self.tcp_bytes,
        )
        self.stats.append(stats)
        mbps_udp = (self.udp_bytes * 8 / 1_000_000) / max(self.interval, 1)
        mbps_tcp = (self.tcp_bytes * 8 / 1_000_000) / max(self.interval, 1)
        print(
            f"[Interval] UDP packets={self.udp_packets} bytes={self.udp_bytes} loss_est={self.udp_loss} "
            f"rate={mbps_udp:.2f} Mbps | TCP bytes={self.tcp_bytes} rate={mbps_tcp:.2f} Mbps"
        )
        # reset counters interval
        self.udp_packets = 0
        self.udp_bytes = 0
        self.udp_loss = 0
        self.tcp_bytes = 0

    def _write(self):
        if not self.output:
            return
        path = Path(self.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "udp_packets", "udp_bytes", "udp_loss_est", "tcp_bytes"])
            for s in self.stats:
                w.writerow([s.ts.isoformat(), s.udp_packets, s.udp_bytes, s.udp_loss_est, s.tcp_bytes])
        print(f"[Receiver] Rapport écrit: {path}")


def parse_args():
    p = argparse.ArgumentParser(description="Récepteur TCP/UDP mesure trafic")
    p.add_argument("--udp-port", type=int, default=5202)
    p.add_argument("--tcp-port", type=int)
    p.add_argument("--interval", type=int, default=5)
    p.add_argument("--output", help="Fichier CSV de sortie")
    return p.parse_args()


def main():
    args = parse_args()
    recv = Receiver(args.udp_port, args.tcp_port, args.interval, args.output)
    try:
        asyncio.run(recv.start())
    except KeyboardInterrupt:
        print("\nInterruption utilisateur, arrêt.")


if __name__ == "__main__":  # pragma: no cover
    main()
