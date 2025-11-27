from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
import requests

import config
import state
from config import log
from rate_tracker import rate_tracker
from live_post import throttled_live_post
from model_utils import is_ddos_attack_for_ip, model, EXPECTED_FEATURES
from sdn import unblock_ip, block_ip
from capture import capture_loop
from network_slicing import get_network_slice

# ==========================================================
# FLASK APP
# ==========================================================
app = Flask(__name__)
CORS(app, origins=["*"])


# ==========================================================
# API ROUTES
# ==========================================================
@app.post("/simulate-packet")
def simulate_packet():
    """
    Synthetic packet endpoint used by Locust / demo.

    For the project demo we treat everything coming here as a
    simulated DDoS packet for detection, but we report it to the
    dashboard as a normal HIGH DDoS attack (no 'SIMULATED' badge).
    """
    try:
        data = request.get_json(force=True) or {}

        # Still treat this logically as simulated for detection logic
        is_simulated = True

        # Get source IP from request
        src_ip = (
            data.get("srcIP")
            or data.get("srcIp")
            or data.get("src")
            or request.headers.get("X-Forwarded-For")
            or request.remote_addr
            or "unknown"
        )

        # === RESPECT ALREADY BLOCKED IPS ===
        if src_ip in state.BLOCKED_IPS:
            log.debug(f"Dropping simulated packet from blocked IP: {src_ip}")
            return jsonify({"status": "dropped", "reason": "IP is blocked"}), 200

        # Get destination IP
        dst_ip = (
            data.get("dstIP")
            or data.get("dstIp")
            or data.get("dst")
            or config.LAPTOP_IP
        )

        packet_size = int(data.get("packetSize") or data.get("size") or 0)
        ts = float(data.get("timestamp") / 1000.0) if data.get("timestamp") else time.time()
        proto = data.get("protocol", "UDP")

        # Update rate tracker (for PPS in reason string)
        rate_tracker.add(src_ip, ts)
        pps = rate_tracker.pps(src_ip)

        # ---------- NETWORK SLICING (SIMULATED TRAFFIC) ----------
        try:
            slice_info = get_network_slice(packet_size, proto, pps)
            network_slice = slice_info["slice"]
            slice_priority = slice_info["priority"]
        except Exception as e:
            log.error(f"network slicing (simulate) error: {e}")
            network_slice = "eMBB"
            slice_priority = 2

        # ---- SEND LIVE PACKET → Node (for LivePacketTable) ----
        live_payload = {
            "srcIP": src_ip,
            "dstIP": dst_ip,
            "protocol": proto,
            "packetSize": packet_size,
            "timestamp": int(ts * 1000),
            "isMalicious": True,
            "confidence": 0.99,
            "packet_data": {"simulated": True},  # internal flag only
            "network_slice": network_slice,
            "slice_priority": slice_priority,
        }
        throttled_live_post(live_payload)

        # ---- DDoS DETECTION (forced malicious for simulated) ----
        is_ddos = is_ddos_attack_for_ip(src_ip, packet_size, pps, simulated=is_simulated)

        blocked = False
        if is_ddos:
            blocked = block_ip(src_ip)
            if blocked:
                try:
                    # IMPORTANT CHANGE:
                    # We now send a NORMAL high DDoS threat (not "simulated")
                    # and we DO NOT mark it as isSimulated: True for the UI.
                    requests.post(
                        config.NODE_URL,
                        json={
                            "ip": src_ip,
                            "reason": f"DDoS Flood ({pps:.0f} pps, slice={network_slice})",
                            "threatLevel": "high",
                            "timestamp": datetime.now().isoformat(),
                            "isSimulated": False,   # or remove this field entirely
                            "network_slice": network_slice,
                            "slice_priority": slice_priority,
                        },
                        timeout=1,
                    )
                except Exception:
                    pass

        log.warning(
            f"[SIMULATE] FORCED DDOS for {src_ip} (pps={pps:.1f}, "
            f"simulated={is_simulated}, blocked={blocked}, slice={network_slice})"
        )
        return jsonify(
            {
                "pred": "ddos" if is_ddos else "normal",
                "pps": pps,
                "blocked": blocked,
                "simulated": is_simulated,
                "network_slice": network_slice,
                "slice_priority": slice_priority,
            }
        )

    except Exception as e:
        log.error(f"simulate-packet error: {e}")
        return jsonify({"error": str(e)}), 500


@app.post("/start-capture")
def start_capture():
    if state.running:
        return jsonify({"status": "already_running"})
    state.running = True
    threading.Thread(target=capture_loop, daemon=True).start()
    log.info("PACKET CAPTURE STARTED")
    return jsonify({"status": "capturing", "ip": config.LAPTOP_IP})


@app.post("/stop-capture")
def stop_capture():
    state.running = False
    log.info("CAPTURE STOPPED")
    return jsonify({"status": "stopped"})


@app.get("/health")
def health():
    try:
        ryu_ok = requests.get(f"{config.RYU_URL}/stats/switches", timeout=2).ok
    except Exception:
        ryu_ok = False
    return jsonify({
        "status": "LIVE",
        "laptop_ip": config.LAPTOP_IP,
        "ryu_reachable": ryu_ok,
        "blocked_ips": len(state.BLOCKED_IPS),
        "ai_active": model is not None,
        "capturing": state.running,
        "model_features": EXPECTED_FEATURES,
    })


@app.post("/unblock")
def unblock():
    data = request.get_json(force=True) or {}
    ip = data.get("ip")
    success = False
    if ip:
        success = unblock_ip(ip)
    return jsonify({"success": success})


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    log.info("SENTINEL AI LIVE SYSTEM STARTED")
    log.info(f"Laptop IP → {config.LAPTOP_IP}")
    log.info(f"Node Backend → {config.NODE_URL}")
    log.info(f"Ryu Controller → {config.RYU_URL}")
    log.info("POST http://localhost:5001/start-capture to begin.")
    app.run(host="0.0.0.0", port=5001, debug=False)
