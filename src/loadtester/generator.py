from __future__ import annotations

import asyncio
import socket
import time
from dataclasses import dataclass
from typing import Literal, Optional


Protocol = Literal["UDP", "TCP"]


@dataclass
class TrafficStats:
    bytes_sent: int
    duration_s: float

    @property
    def mbps(self) -> float:
        if self.duration_s <= 0:
            return 0.0
        return (self.bytes_sent * 8 / 1_000_000) / self.duration_s


async def _send_udp(host: str, port: int, packet_size: int, target_bps: float, duration: float, sequence: bool = True):
    """Envoie UDP avec pacing approximatif.

    Si sequence=True, insère un numéro de séquence 8 octets big-endian au début
    du paquet permettant au récepteur d'estimer la perte.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    header_size = 8 if sequence and packet_size >= 8 else 0
    body_size = max(packet_size - header_size, 0)
    body = b"X" * body_size
    bytes_sent = 0
    start = time.time()
    pps = target_bps / max(packet_size * 8, 1)
    if pps <= 0:
        pps = 1
    interval = 1.0 / pps
    while True:
        now = time.time()
        if now - start >= duration:
            break
        if header_size:
            payload = seq.to_bytes(8, 'big', signed=False) + body
        else:
            payload = body if body_size else b"X"
        try:
            sock.sendto(payload, (host, port))
        except Exception:
            break
        bytes_sent += len(payload)
        seq += 1
        await asyncio.sleep(interval)
    return bytes_sent, time.time() - start


async def _send_tcp(host: str, port: int, packet_size: int, target_bps: float, duration: float):
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except Exception as e:
        # Indiquer échec en retournant 0 durée (géré plus haut)
        return 0, 0.0
    payload = b"X" * packet_size
    bytes_sent = 0
    start = time.time()
    # naive pacing using sleep to approach target_bps
    loop = asyncio.get_running_loop()
    while time.time() - start < duration:
        writer.write(payload)
        await writer.drain()
        bytes_sent += len(payload)
        elapsed = time.time() - start
        if elapsed > 0:
            current_bps = bytes_sent * 8 / elapsed
            if current_bps > target_bps:
                # back off a bit
                await asyncio.sleep(packet_size * 8 / target_bps)
    writer.close()
    await writer.wait_closed()
    return bytes_sent, time.time() - start


async def generate_traffic(
    protocol: Protocol,
    host: str,
    port: int,
    packet_size: int,
    target_bandwidth_mbps: float,
    connections: int,
    duration_s: float,
    udp_sequence: bool = True,
) -> TrafficStats:
    target_bps = target_bandwidth_mbps * 1_000_000
    per_conn_bps = target_bps / max(connections, 1)

    tasks = []
    for _ in range(connections):
        if protocol == "UDP":
            tasks.append(
                asyncio.create_task(
                    _send_udp(host, port, packet_size, per_conn_bps, duration_s, sequence=udp_sequence)
                )
            )
        else:
            tasks.append(
                asyncio.create_task(
                    _send_tcp(host, port, packet_size, per_conn_bps, duration_s)
                )
            )
    total_bytes = 0
    durations = []
    for t in tasks:
        try:
            b, d = await t
            total_bytes += b
            durations.append(d)
        except Exception:
            pass
    duration = max(durations) if durations else duration_s
    return TrafficStats(total_bytes, duration)


__all__ = ["generate_traffic", "TrafficStats"]
