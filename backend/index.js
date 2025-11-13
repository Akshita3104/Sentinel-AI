// backend/index.js - FINAL VERSION
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const axios = require('axios');
const os = require('os');

const app = express();
const server = http.createServer(app);

// ---------------- SOCKET.IO + CORS ----------------
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
    methods: ["GET", "POST"],
    credentials: true
  },
  transports: ['websocket', 'polling']
});

app.use(cors({
  origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// ---------------- CONFIG ----------------
const FLASK_URL = 'http://localhost:5001';   // Flask capture system
const LAPTOP_IP = '10.0.62.179';             // Detected Laptop IP (from Flask logs)

// ---------------- STATE ----------------
let blockedIPs = [];
let maliciousPackets = [];
let isCapturing = false;
let packetCount = 0;

// ---------------- HEALTH ----------------
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', ip: LAPTOP_IP, time: new Date().toISOString() });
});

// ---------------- CAPTURE CONTROL ----------------
app.post('/api/start-capture', async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/start-capture`);
    io.emit('capture-started');
    isCapturing = true;
    console.log("✅ Capture started via Flask");
    res.json({ success: true });
  } catch (err) {
    console.error('❌ Error starting capture:', err.message);
    res.json({ success: false, error: err.message });
  }
});

app.post('/api/stop-capture', async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/stop-capture`);
    io.emit('capture-stopped');
    isCapturing = false;
    console.log("🛑 Capture stopped via Flask");
    res.json({ success: true });
  } catch (err) {
    console.error('❌ Error stopping capture:', err.message);
    res.json({ success: false, error: err.message });
  }
});

// ---------------- LIVE PACKET STREAM ----------------
app.post('/api/live-packet', (req, res) => {
  const packet = req.body;
  packetCount++;

  io.emit('new_packet', packet);

  console.log(`📡 [${packetCount}] Packet from ${packet.srcIP || 'unknown'} → ${packet.dstIP || 'unknown'}`);

  res.json({ ok: true });
});

// ---------------- BLOCK MANAGEMENT ----------------
app.get('/api/blocked-ips', (req, res) => {
  res.json(blockedIPs);
});

app.post('/api/emit-blocked-ip', (req, res) => {
  const { ip, confidence = 99, reason = 'DDoS Flood' } = req.body;
  if (!ip) return res.status(400).json({ error: 'No IP provided' });

  const block = {
    ip,
    timestamp: new Date().toISOString(),
    reason,
    threatLevel: confidence > 90 ? 'high' : 'medium',
    mitigation: 'SDN DROP Rule'
  };

  if (!blockedIPs.find(b => b.ip === ip)) {
    blockedIPs.push(block);
    maliciousPackets.push({
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

  io.emit('ip_blocked', block);
  io.emit('update_blocked_ips', blockedIPs);
  io.emit('detection-result', {
    ip,
    is_ddos: true,
    confidence: confidence / 100,
    prediction: 'ddos',
    abuseScore: confidence,
    threat_level: confidence > 90 ? 'HIGH' : 'MEDIUM'
  });

  console.log(`🚫 Blocked IP emitted: ${ip}`);

  res.json({ success: true });
});

app.post('/api/unblock', (req, res) => {
  const { ip } = req.body;
  blockedIPs = blockedIPs.filter(b => b.ip !== ip);
  io.emit('update_blocked_ips', blockedIPs);
  io.emit('unblocked_ip', { ip });
  console.log(`♻️ Unblocked IP: ${ip}`);
  res.json({ success: true });
});

// ---------------- SOCKET EVENTS ----------------
io.on('connection', (socket) => {
  console.log('⚡ Frontend CONNECTED:', socket.id);

  socket.emit('initial_blocked_ips', blockedIPs);
  socket.emit('capture-status', {
    isCapturing,
    packetCount,
    packetsPerSecond: 0,
    totalBytes: 0,
    duration: 0
  });

  socket.on('disconnect', () => {
    console.log('❎ Frontend disconnected');
  });
});

// ---------------- SERVER START ----------------
const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log('\n🚀 SentinelAI Backend LIVE');
  console.log(`🌐 http://localhost:${PORT}`);
  console.log(`🩺 Health: http://localhost:${PORT}/api/health\n`);
});
