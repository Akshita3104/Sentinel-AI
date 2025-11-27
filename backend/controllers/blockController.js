const io = (req) => req.app.get('io');
const LAPTOP_IP = global.LAPTOP_IP;

module.exports.getBlockedIPs = (req, res) => {
  res.json(global.blockedIPs);
};

module.exports.emitBlockedIP = (req, res) => {
  const { ip, confidence = 99, reason = 'DDoS Flood' } = req.body;
  if (!ip) return res.status(400).json({ error: 'No IP provided' });

  const block = {
    ip,
    timestamp: new Date().toISOString(),
    reason,
    threatLevel: confidence > 90 ? 'high' : 'medium',
    mitigation: 'SDN DROP Rule'
  };

  if (!global.blockedIPs.find(b => b.ip === ip)) {
    global.blockedIPs.push(block);
    global.maliciousPackets.push({
      id: Date.now(),
      timestamp: Date.now(),
      srcIP: ip,
      dstIP: LAPTOP_IP,
      protocol: 'UDP',
      packetSize: 1024,
      action: 'Blocked',
      prediction: 'ddos'
    });
  }

  const socket = io(req);
  socket.emit('ip_blocked', block);
  socket.emit('update_blocked_ips', global.blockedIPs);
  socket.emit('detection-result', {
    ip,
    is_ddos: true,
    confidence: confidence / 100,
    prediction: 'ddos',
    abuseScore: confidence,
    threat_level: confidence > 90 ? 'HIGH' : 'MEDIUM'
  });

  console.log(`Blocked IP emitted: ${ip}`);
  res.json({ success: true });
};

module.exports.unblockIP = (req, res) => {
  const { ip } = req.body;
  global.blockedIPs = global.blockedIPs.filter(b => b.ip !== ip);
  io(req).emit('update_blocked_ips', global.blockedIPs);
  io(req).emit('unblocked_ip', { ip });
  console.log(`Unblocked IP: ${ip}`);
  res.json({ success: true });
};