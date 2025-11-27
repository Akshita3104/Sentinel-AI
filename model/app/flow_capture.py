# flow_capture.py
# model/app/flow_capture.py
import asyncio
import pyshark
import logging
from typing import Optional
import threading

# ✅ Add these three lines below ↓↓↓
pyshark.tshark.tshark.get_tshark_path.cache_clear()
pyshark.tshark.tshark.TSHARK_PATH_OVERRIDE = r"C:\Program Files\Wireshark\tshark.exe"
logging.info("✅ TShark path set to C:\\Program Files\\Wireshark\\tshark.exe")

class FlowCapture:
    def __init__(self, interface: str, ml_engine):
        self.interface = interface
        self.ml_engine = ml_engine
        self.capture: Optional[pyshark.LiveCapture] = None
        self.loop = None
        self.thread = None
        self.blocked_ips = set()
        self._update_filter()

    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self._run_async_capture, daemon=True)
        self.thread.start()

    def _run_async_capture(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.capture_loop())
        except Exception as e:
            logging.error(f"Capture loop crashed: {e}")
        finally:
            if self.loop:
                self.loop.close()

    def _update_filter(self):
        """Update the BPF filter to exclude blocked IPs"""
        if hasattr(self.ml_engine, 'mitigation_engine'):
            blocked = getattr(self.ml_engine.mitigation_engine, 'blocked_ips', {})
            if blocked:
                blocked_ips = ' or '.join([f'ip.src != {ip}' for ip in blocked.keys()])
                self.bpf_filter = f'ip and ({blocked_ips})'
            else:
                self.bpf_filter = 'ip'
        else:
            self.bpf_filter = 'ip'
        
        logging.info(f"Updated capture filter: {self.bpf_filter}")
        return self.bpf_filter

    async def capture_loop(self):
        logging.info(f"Started real live capture on {self.interface}")
        try:
            self._update_filter()
            self.capture = pyshark.LiveCapture(
                interface=self.interface,
                bpf_filter=self.bpf_filter,
                use_json=True,
                include_raw=True
            )
            async for packet in self.capture.sniff_continuously():
                try:
                    if hasattr(packet, 'ip'):
                        # Double-check if IP was blocked after capture started
                        src_ip = packet.ip.src
                        if hasattr(self.ml_engine, 'mitigation_engine'):
                            if self.ml_engine.mitigation_engine.is_ip_blocked(src_ip):
                                logging.debug(f"Dropping packet from blocked IP: {src_ip}")
                                # Update the filter to block this IP in future captures
                                self._update_filter()
                                continue
                        self.ml_engine.process_packet(packet)
                except Exception as e:
                    logging.debug(f"Packet processing error: {e}")
        except Exception as e:
            logging.error(f"Capture error: {e}")
        finally:
            if self.capture:
                self.capture.close()
