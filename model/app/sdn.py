import logging
import requests

import config
import state

log = logging.getLogger("SENTINEL")


def block_ip(ip: str) -> bool:
    """
    Install a DROP flow in Ryu to block all IPv4 traffic from `ip`.
    Same behavior as your original block_ip.
    """
    if ip in state.BLOCKED_IPS:
        return True

    url = f"{config.RYU_URL}/stats/flowentry/add"

    rule = {
        "dpid": 1,
        "priority": 60000,
        "match": {
            "eth_type": 0x0800,
            "ipv4_src": ip
        },
        "actions": []  # empty actions => DROP
    }

    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            state.BLOCKED_IPS.add(ip)
            log.warning(f"BLOCKED {ip} → SDN DROP RULE ADDED")
            return True
        else:
            log.error(f"RYU flow add failed: {r.status_code} {r.text}")
    except Exception as e:
        log.error(f"RYU CONTROLLER UNREACHABLE: {e}")
    return False


def unblock_ip(ip: str) -> bool:
    """
    Remove the DROP flow for `ip` from Ryu.
    Only if Ryu successfully deletes the flow do we remove `ip`
    from BLOCKED_IPS and report success.
    """
    if not ip:
        return False

    url = f"{config.RYU_URL}/stats/flowentry/delete"

    rule = {
        "dpid": 1,
        "match": {
            "eth_type": 0x0800,
            "ipv4_src": ip
        }
    }

    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            log.info(f"UNBLOCKED {ip} → SDN DROP RULE REMOVED")
            if ip in state.BLOCKED_IPS:
                state.BLOCKED_IPS.discard(ip)
                log.info(f"UNBLOCKED {ip} LOCALLY → removed from BLOCKED_IPS")
            return True
        else:
            log.error(f"RYU flow delete failed: {r.status_code} {r.text}")
            return False
    except Exception as e:
        log.error(f"Failed to unblock {ip} in Ryu: {e}")
        return False
