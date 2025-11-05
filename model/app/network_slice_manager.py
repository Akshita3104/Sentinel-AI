# network_slice_manager.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json

class NetworkSliceManager:
    def __init__(self, sdn_controller):
        self.sdn_controller = sdn_controller
        self.logger = logging.getLogger(__name__)
        
        # 5G Network Slice Definitions
        self.slices = {
            'eMBB': {
                'name': 'Enhanced Mobile Broadband',
                'bandwidth': '1Gbps',
                'latency': '20ms',
                'reliability': '99.9%',
                'priority': 3,
                'current_status': 'active',
                'threat_level': 0,
                'isolated_ips': set(),
                'traffic_patterns': []
            },
            'URLLC': {
                'name': 'Ultra-Reliable Low Latency Communications',
                'bandwidth': '100Mbps',
                'latency': '1ms',
                'reliability': '99.999%',
                'priority': 1,
                'current_status': 'active',
                'threat_level': 0,
                'isolated_ips': set(),
                'traffic_patterns': []
            },
            'mMTC': {
                'name': 'Massive Machine Type Communications',
                'bandwidth': '10Mbps',
                'latency': '100ms',
                'reliability': '99%',
                'priority': 2,
                'current_status': 'active',
                'threat_level': 0,
                'isolated_ips': set(),
                'traffic_patterns': []
            }
        }
        
        # Healing policies
        self.healing_policies = {
            'isolation_threshold': 3,
            'restoration_delay': 300,  # 5 minutes
            'max_isolation_time': 1800,  # 30 minutes
            'threat_decay_rate': 0.1
        }
    
    async def autonomous_slice_monitoring(self):
        """Continuously monitor all network slices"""
        self.logger.info("🔍 Starting autonomous slice monitoring")
        
        while True:
            try:
                for slice_id, slice_info in self.slices.items():
                    await self.monitor_slice_health(slice_id)
                    await self.check_slice_restoration(slice_id)
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Slice monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def monitor_slice_health(self, slice_id: str):
        """Monitor individual slice health and performance"""
        slice_info = self.slices[slice_id]
        
        # Simulate real-time slice metrics (replace with actual SDN queries)
        current_metrics = {
            'active_flows': len(slice_info['traffic_patterns']),
            'bandwidth_usage': f"{slice_info['threat_level'] * 10}%",
            'latency': slice_info['latency'],
            'packet_loss': slice_info['threat_level'] * 0.1
        }
        
        # Decay threat level over time
        slice_info['threat_level'] *= (1 - self.healing_policies['threat_decay_rate'])
        
        # Check for anomalies
        if current_metrics['packet_loss'] > 1 or slice_info['threat_level'] > 1:
            self.logger.warning(f"⚠️ Potential issue in slice {slice_id}: {current_metrics}")
    
    async def check_slice_restoration(self, slice_id: str):
        """Check if isolated slice can be restored"""
        slice_info = self.slices[slice_id]
        
        if slice_info['current_status'] == 'isolated':
            isolation_time = (datetime.now() - slice_info.get('isolation_time', datetime.now())).seconds
            
            if isolation_time > self.healing_policies['restoration_delay'] and slice_info['threat_level'] < 1:
                await self.restore_slice(slice_id)
            elif isolation_time > self.healing_policies['max_isolation_time']:
                await self.force_restore_slice(slice_id)
    
    async def isolate_slice(self, slice_id: str, reason: str):
        """Isolate network slice"""
        slice_info = self.slices[slice_id]
        
        if slice_info['current_status'] == 'isolated':
            return
        
        self.logger.warning(f"🛑 Isolating slice {slice_id}: {reason}")
        
        slice_info['current_status'] = 'isolated'
        slice_info['isolation_time'] = datetime.now()
        
        # Install isolation rules via SDN
        isolation_rules = [
            {
                'priority': 65535,
                'match': {'dl_vlan': {'eMBB': 100, 'URLLC': 200, 'mMTC': 300}[slice_id]},
                'actions': [{'type': 'DROP'}]
            }
        ]
        
        for rule in isolation_rules:
            self.sdn_controller.install_flow_rule(1, rule)
    
    async def restore_slice(self, slice_id: str):
        """Restore isolated network slice"""
        slice_info = self.slices[slice_id]
        
        self.logger.info(f"✅ Restoring slice {slice_id}")
        
        slice_info['current_status'] = 'active'
        slice_info['threat_level'] = 0
        slice_info['isolated_ips'].clear()
        
        # Remove isolation rules
        removal_rules = [
            {
                'command': 'DELETE',
                'match': {'dl_vlan': {'eMBB': 100, 'URLLC': 200, 'mMTC': 300}[slice_id]}
            }
        ]
        
        for rule in removal_rules:
            self.sdn_controller.remove_flow_rule(1, rule)
    
    async def force_restore_slice(self, slice_id: str):
        """Force restore slice after max isolation time"""
        self.logger.warning(f"⚠️ Force restoring slice {slice_id} after max isolation time")
        await self.restore_slice(slice_id)
    
    async def handle_slice_threat(self, slice_id: str, threat_info: Dict):
        """Handle detected threat in specific slice"""
        if slice_id not in self.slices:
            return
        
        slice_info = self.slices[slice_id]
        slice_info['threat_level'] += threat_info.get('confidence', 0.5)
        
        # Isolate suspicious IP
        if 'src_ip' in threat_info:
            slice_info['isolated_ips'].add(threat_info['src_ip'])
        
        # Record traffic pattern
        slice_info['traffic_patterns'].append({
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat_info.get('threat_type', 'unknown'),
            'confidence': threat_info.get('confidence', 0),
            'src_ip': threat_info.get('src_ip', 'unknown')
        })
        
        self.logger.warning(f"🚨 Threat handled in slice {slice_id}: threat_level={slice_info['threat_level']}")
        
        # Trigger immediate isolation if threshold exceeded
        if slice_info['threat_level'] >= self.healing_policies['isolation_threshold']:
            await self.isolate_slice(slice_id, f"Threat threshold exceeded: {slice_info['threat_level']}")
    
    def get_slice_status(self) -> Dict:
        """Get current status of all network slices"""
        status = {}
        
        for slice_id, slice_info in self.slices.items():
            status[slice_id] = {
                'name': slice_info['name'],
                'status': slice_info['current_status'],
                'threat_level': slice_info['threat_level'],
                'isolated_ips_count': len(slice_info['isolated_ips']),
                'recent_threats': len([p for p in slice_info['traffic_patterns'] 
                                    if (datetime.now() - datetime.fromisoformat(p['timestamp'])).seconds < 300])
            }
        
        return status
    
    async def dynamic_service_restoration(self):
        """Dynamically restore services based on network conditions"""
        self.logger.info("🔄 Starting dynamic service restoration")
        
        while True:
            try:
                for slice_id, slice_info in self.slices.items():
                    if slice_info['current_status'] == 'isolated':
                        # Check if services can be partially restored
                        if slice_info['threat_level'] < 2:
                            await self.partial_service_restoration(slice_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Service restoration error: {e}")
                await asyncio.sleep(60)
    
    async def partial_service_restoration(self, slice_id: str):
        """Partially restore services in isolated slice"""
        slice_info = self.slices[slice_id]
        
        self.logger.info(f"🔄 Partial restoration for slice {slice_id}")
        
        # Allow limited traffic for critical services
        partial_rules = [
            {
                'priority': 20000,
                'match': {'dl_vlan': {'eMBB': 100, 'URLLC': 200, 'mMTC': 300}[slice_id], 'nw_proto': 6, 'tp_dst': 443},  # HTTPS
                'actions': [{'type': 'OUTPUT', 'port': 'NORMAL'}]
            }
        ]
        
        for rule in partial_rules:
            self.sdn_controller.install_flow_rule(1, rule)