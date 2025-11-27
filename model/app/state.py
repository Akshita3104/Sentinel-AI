from typing import Set

# Shared mutable state across modules

BLOCKED_IPS: Set[str] = set()

# Any IPs added here will ALWAYS be treated as malicious (for Locust / demo)
FORCE_MALICIOUS_IPS: Set[str] = set()

# Global capture flag
running: bool = False
