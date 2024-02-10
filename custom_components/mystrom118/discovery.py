"""Discovery for MyStrom118 devices."""
from __future__ import annotations

import asyncio

from scapy.all import AsyncSniffer

from homeassistant.components import network
from homeassistant.core import HomeAssistant


def parse_status(status):
    """Parse MyStrom Status Byte."""
    return {
        "cloud_connected": bool(int(status[0])),
        "registered": bool(int(status[1])),
        "mesh_child": bool(int(status[2])),
    }


async def dissect(packet):
    """Parse Discovery Data."""
    raw = packet.load

    mac = "".join(packet[0].src.split(":"))  # Get MAC from Ethernet Layer
    ip = packet[1].src  # Get IPv4 from IP Layer

    device = raw[6]  # Get Device Type from Payload
    status = bin(raw[-1])[2:]  # Get Status Byte from Payload
    status = parse_status(status)  # Parse Status Byte

    return {"mac": mac.upper(), "ip": ip, "device": device, "status": status}


async def discover(hass: HomeAssistant, timeout: int):
    """Discover MyStrom118 Devices."""

    adapters = await network.async_get_adapters(hass)
    ifaces = [
        adapt["name"]
        for adapt in adapters
        if adapt["enabled"] is True and len(adapt["ipv4"]) > 0
    ]

    if len(ifaces) == 0:
        return []

    sniffer = AsyncSniffer(iface=ifaces, filter="udp and port 7979")
    sniffer.start()
    await asyncio.sleep(timeout)
    packets = sniffer.stop()

    discovered = {}
    for packet in packets:
        data = await dissect(packet)
        if data["mac"] not in discovered:
            discovered[data["mac"]] = data

    devices = list(discovered.values())
    return devices
