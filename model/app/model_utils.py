import logging
import joblib
import numpy as np  # kept for future use if needed

import config
import state

log = logging.getLogger("SENTINEL")

# === LOAD ML MODEL + PRINT EXPECTED FEATURES ===
model = None
try:
    model = joblib.load(config.MODEL_PATH)
    log.info("ML MODEL LOADED → AI DETECTION ACTIVE")
    log.info(f"   → Model expects {model.n_features_in_} features")
    if hasattr(model, "feature_names_in_"):
        log.info(f"   → Feature names: {list(model.feature_names_in_)}")
except Exception as e:
    log.warning(f"NO ML MODEL FOUND → fallback rule ({e})")

EXPECTED_FEATURES = model.n_features_in_ if model else 0


def build_features(pkt_size: int, pps: float) -> list:
    """
    Build feature vector exactly as in your original code.
    """
    base = [
        1,                # packet_count (dummy)
        pps,              # packets per second
        pkt_size / 100,   # avg packet size (scaled)
        0.5,              # protocol entropy (dummy)
        0.3,              # src-port entropy (dummy)
        10.0,             # flow duration (dummy)
        1,                # SYN flag (dummy)
        1,                # ACK flag (dummy)
        1                 # is_tcp (dummy)
    ]
    if len(base) > EXPECTED_FEATURES:
        return base[:EXPECTED_FEATURES]
    elif len(base) < EXPECTED_FEATURES:
        return base + [0.0] * (EXPECTED_FEATURES - len(base))
    return base


def is_ddos_attack(pkt_size: int, pps: float) -> bool:
    """
    Same logic as before: use ML if available, otherwise fallback PPS > 50.
    """
    if model:
        try:
            feats = build_features(pkt_size, pps)
            pred = model.predict([feats])[0]
            prob = model.predict_proba([feats])[0].max()
            return pred == 1 and prob > 0.7
        except Exception as e:
            log.error(f"ML predict error: {e}")
            return False
    else:
        # Simple fallback: treat > 50 pps as DDoS
        return pps > 50


def is_ddos_attack_for_ip(src_ip: str, pkt_size: int, pps: float, simulated: bool = False) -> bool:
    """
    Wrapper that lets us mark Locust / simulated traffic as always malicious.
    Behavior is identical to your original function.
    """
    # Any simulated traffic is always treated as malicious
    if simulated:
        return True

    # Any IP in FORCE_MALICIOUS_IPS is always malicious
    if src_ip in state.FORCE_MALICIOUS_IPS:
        return True

    # Otherwise, defer to ML / fallback
    return is_ddos_attack(pkt_size, pps)
