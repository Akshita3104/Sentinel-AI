# ==========================================================
# model/app.py — SENTINEL AI (Wi-Fi Capture + Stable Connection)
# ==========================================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import threading
import asyncio
import pyshark
import joblib
import numpy as np
from datetime import datetime
import socket
import time

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins

# === LOGGING SETUP ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SENTINEL")

# === AUTO-DETECT LAPTOP IP ===
def get_laptop_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

LAPTOP_IP = get_laptop_ip()
log.info(f"LAPTOP IP AUTO DETECTED → {LAPTOP_IP}")

# ==========================================================
# CONFIGURATION (UPDATE IF NEEDED)
# ==========================================================
# VM → RYU Controller IP
RYU_URL = "http://192.168.56.101:8080"

# 💡 Use laptop's IP (from ipconfig or detected above)
NODE_HOST = "localhost"
NODE_URL = f"http://{NODE_HOST}:3000/api/emit-blocked-ip"
NODE_LIVEPACKET = f"http://{NODE_HOST}:3000/api/live-packet"

MODEL_PATH = "models/randomforest_dummy.pkl"
BLOCKED_IPS = set()
running = False
capture = None

# === LOAD ML MODEL ===
try:
    model = joblib.load(MODEL_PATH)
    log.info("ML MODEL LOADED → AI DETECTION ACTIVE ✅")
except Exception as e:
    model = None
    log.warning(f"⚠️ NO ML MODEL FOUND → Using fallback rule ({e})")

# ==========================================================
# RYU CONTROLLER: BLOCK IP
# ==========================================================
def block_ip(ip):
    if ip in BLOCKED_IPS:
        return True
    url = f"{RYU_URL}/stats/flowentry/add"
    rule = {
        "dpid": "0000000000000001",
        "priority": 60000,
        "match": {"ipv4_src": ip},
        "actions": []
    }
    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            BLOCKED_IPS.add(ip)
            log.warning(f"🚫 BLOCKED {ip} → SDN DROP RULE ADDED")
            return True
    except Exception as e:
        log.error(f"RYU CONTROLLER UNREACHABLE: {e}")
    return False

# ==========================================================
# ML / FALLBACK DETECTOR
# ==========================================================
def is_ddos_attack(pkt_size, pps):
    if model:
        features = [1, pps, pkt_size/100, 0.1, pps*0.8, pps,
                    0.01, 0.001, 0.05, 0.001, 1, 0, 0, 0, 0, 1, 0]
        pred = model.predict([features])[0]
        prob = model.predict_proba([features])[0].max()
        return pred == 1 and prob > 0.7
    else:
        # Simple fallback threshold rule
        return pps > 50

# ==========================================================
# CAPTURE LOOP — FIXED FOR WINDOWS WIFI INTERFACE
# ==========================================================
def capture_loop():
    global capture, running
    log.info(f"📡 STARTING PACKET CAPTURE on Wi-Fi → Host filter: {LAPTOP_IP}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # ⚙️ Use the Wi-Fi interface — replace if needed (use 'Wi-Fi', 'Wi-Fi 2', etc.)
        capture = pyshark.LiveCapture(
            interface="Wi-Fi",
            bpf_filter=f"dst host {LAPTOP_IP}"
        )
    except Exception as e:
        log.error(f"❌ Pyshark initialization failed: {e}")
        running = False
        return

    packet_count = 0
    start_time = time.time()

    for pkt in capture.sniff_continuously():
        if not running:
            break
        try:
            if not hasattr(pkt, 'ip'):
                continue

            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
            size = int(pkt.length)
            protocol = pkt.highest_layer

            packet_count += 1
            elapsed = time.time() - start_time
            pps = packet_count / elapsed if elapsed > 0 else 0

            # ==========================================
            # SEND LIVE PACKET TO NODE BACKEND
            # ==========================================
            try:
                requests.post(NODE_LIVEPACKET, json={
                    "srcIP": src_ip,
                    "dstIP": dst_ip,
                    "protocol": protocol,
                    "packetSize": size
                }, timeout=0.1)
            except Exception as e:
                log.debug(f"Live packet send failed: {e}")

            # ==========================================
            # DDoS DETECTION
            # ==========================================
            if is_ddos_attack(size, pps):
                if block_ip(src_ip):
                    try:
                        requests.post(NODE_URL, json={
                            "ip": src_ip,
                            "reason": f"DDoS Flood ({pps:.0f} pps)",
                            "threatLevel": "high",
                            "timestamp": datetime.now().isoformat()
                        }, timeout=1)
                    except Exception as e:
                        log.debug(f"Notify Node failed: {e}")

        except Exception:
            continue

# ==========================================================
# API ROUTES
# ==========================================================
@app.post("/start-capture")
def start_capture():
    global running, capture
    if running:
        return jsonify({"status": "already_running"})
    try:
        running = True
        threading.Thread(target=capture_loop, daemon=True).start()
        log.info("✅ PACKET CAPTURE STARTED")
        return jsonify({"status": "capturing", "ip": LAPTOP_IP})
    except Exception as e:
        running = False
        log.error(f"❌ Failed to start capture: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.post("/stop-capture")
def stop_capture():
    global running
    running = False
    if capture:
        try:
            capture.close()
        except:
            pass
    log.info("🛑 CAPTURE STOPPED")
    return jsonify({"status": "stopped"})


@app.get("/health")
def health():
    try:
        ryu_ok = requests.get(f"{RYU_URL}/stats/switches", timeout=2).ok
    except:
        ryu_ok = False
    return jsonify({
        "status": "LIVE",
        "laptop_ip": LAPTOP_IP,
        "ryu_reachable": ryu_ok,
        "blocked_ips": len(BLOCKED_IPS),
        "ai_active": model is not None,
        "capturing": running
    })


@app.post("/unblock")
def unblock():
    ip = request.json.get("ip")
    if ip and ip in BLOCKED_IPS:
        try:
            requests.post(f"{RYU_URL}/stats/flowentry/delete", json={
                "dpid": "0000000000000001",
                "match": {"ipv4_src": ip}
            }, timeout=3)
            BLOCKED_IPS.discard(ip)
            log.info(f"✅ UNBLOCKED {ip}")
        except Exception as e:
            log.error(f"Failed to unblock {ip}: {e}")
    return jsonify({"success": True})

# ==========================================================
# MAIN ENTRY
# ==========================================================
if __name__ == "__main__":
    log.info("🚀 SENTINEL AI LIVE SYSTEM STARTED")
    log.info(f"Laptop IP → {LAPTOP_IP}")
    log.info(f"Node Backend → {NODE_URL}")
    log.info(f"Ryu Controller → {RYU_URL}")
    log.info("Use: POST http://localhost:5001/start-capture to begin.")
    app.run(host="0.0.0.0", port=5001, debug=False)
