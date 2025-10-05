"""
Network utilities: detect Bluetooth PAN IP (bnep0) and fallbacks.
"""
import logging
from typing import Optional
import socket
import netifaces

logger = logging.getLogger("net_utils")

def get_bluetooth_pan_ip(interface: str = "bnep0") -> Optional[str]:
    """
    Return IPv4 address of Bluetooth PAN interface if present.
    Requires netifaces (pip install netifaces).
    """
    try:
        if interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ip = addrs[netifaces.AF_INET][0].get("addr")
                logger.info("Bluetooth PAN IP detected: %s on %s", ip, interface)
                return ip
    except Exception:
        logger.exception("Failed to get bluetooth pan ip")
    return None

def get_best_bind_ip(prefer_bluetooth=True) -> str:
    """
    Return best IP for binding the Flask app:
    1. Bluetooth PAN if available
    2. Wi-Fi (wlan0) if available
    3. 0.0.0.0 (all interfaces)
    """
    if prefer_bluetooth:
        bt = get_bluetooth_pan_ip()
        if bt:
            return bt
    # attempt wlan0
    for iface in ("wlan0", "eth0"):
        try:
            if iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    ip = addrs[netifaces.AF_INET][0].get("addr")
                    if ip:
                        logger.info("Using interface %s IP %s", iface, ip)
                        return ip
        except Exception:
            continue
    logger.info("No interface-specific IP found — defaulting to 0.0.0.0")
    return "0.0.0.0"
