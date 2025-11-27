import time
import logging
from datetime import datetime

import requests
from scapy.all import sniff, IP  # <-- FAST capture

import config
import state
from config import PROTOCOL_MAP
from rate_tracker import rate_tracker
from live_post import throttled_live_post
from model_utils import is_ddos_attack_for_ip
from sdn import block_ip
from network_slicing import get_network_slice

log = logging.getLogger("SENTINEL")


def capture_loop():
    """
    Scapy capture loop (real traffic), same logic as your original function.
    Uses state.running as the flag.
    """
    log.info(f"STARTING FAST SCAPY CAPTURE on Wi-Fi → dst host {config.LAPTOP_IP}")

    def packet_handler(pkt):
        if not state.running:
            return
        if not pkt.haslayer(IP):
            return

        ip_layer = pkt[IP]
        src_ip   = ip_layer.src
        dst_ip   = ip_layer.dst
        size     = len(pkt)
        proto    = ip_layer.proto

        now = time.time()
        rate_tracker.add(src_ip, now)
        pps = rate_tracker.pps(src_ip)

        # ---------- PROTOCOL NAME ----------
        protocol_name = PROTOCOL_MAP.get(proto, f"Proto {proto}")

        # ---------- NETWORK SLICING (REAL TRAFFIC) ----------
        try:
            slice_info = get_network_slice(size, protocol_name, pps)
            network_slice = slice_info["slice"]
            slice_priority = slice_info["priority"]
        except Exception as e:
            log.error(f"network slicing error: {e}")
            network_slice = "eMBB"
            slice_priority = 2

        # ---------- LIVE PACKET (throttled) ----------
        throttled_live_post({
            "srcIP": src_ip,
            "dstIP": dst_ip,
            "protocol": protocol_name,        # "UDP", "TCP", etc.
            "packetSize": size,
            "timestamp": int(now * 1000),
            "network_slice": network_slice,   # slice for frontend
            "slice_priority": slice_priority
        })

        # ---------- DDoS DETECTION ----------
        if is_ddos_attack_for_ip(src_ip, size, pps, simulated=False):
            if block_ip(src_ip):
                try:
                    requests.post(
                        config.NODE_URL,
                        json={
                            "ip": src_ip,
                            "reason": f"DDoS Flood ({pps:.0f} pps, {protocol_name}, slice={network_slice})",
                            "threatLevel": "high",
                            "timestamp": datetime.now().isoformat(),
                            "isSimulated": False,
                            "network_slice": network_slice,
                            "slice_priority": slice_priority,
                        },
                        timeout=1,
                    )
                except Exception:
                    pass

    try:
        sniff(
            iface="Wi-Fi",
            filter=f"dst host {config.LAPTOP_IP}",
            prn=packet_handler,
            store=False,
            stop_filter=lambda x: not state.running,
        )
    except Exception as e:
        log.error(f"Scapy capture crashed: {e}")
    finally:
        state.running = False
        log.info("CAPTURE THREAD EXITED")
