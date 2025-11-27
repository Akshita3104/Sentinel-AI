import logging
import socket

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SENTINEL")

# === AUTO-DETECT LAPTOP IP ===
def get_laptop_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

LAPTOP_IP = get_laptop_ip()
log.info(f"LAPTOP IP AUTO DETECTED → {LAPTOP_IP}")

# ==========================================================
# CONFIGURATION
# ==========================================================
# NOTE: update this IP if your Mininet VM IP changes
RYU_URL = "http://192.168.56.101:8080"

# Node backend lives on the same Windows laptop as this Flask app
NODE_HOST       = "localhost"
NODE_URL        = f"http://{NODE_HOST}:3000/api/emit-blocked-ip"
NODE_LIVEPACKET = f"http://{NODE_HOST}:3000/api/live-packet"

MODEL_PATH = "../models/randomforest_enhanced.pkl"

# === PROTOCOL NUMBER → NAME MAPPING ===
PROTOCOL_MAP = {
    1:  "ICMP",
    2:  "IGMP",
    6:  "TCP",
    17: "UDP",
    89: "OSPF",
    41: "IPv6",
    50: "ESP",
    51: "AH",
    # Add more as needed
}
