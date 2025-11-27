// backend/index.js 
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
    methods: ["GET", "POST"],
    credentials: true
  },
  transports: ['websocket', 'polling']
});

// Make io globally available
app.set('io', io);

// Global state (you can later move to Redis for scaling)
global.blockedIPs = [];
global.maliciousPackets = [];
global.isCapturing = false;
global.packetCount = 0;
global.LAPTOP_IP = require('./utils/getLaptopIp')();

// ---------------- Middleware ----------------
app.use(cors({
  origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// Prevent simulated attacks from controlling capture
app.use(require('./middleware/simulatedClientGuard'));

// ---------------- Socket Handler ----------------
require('./socket/socketHandler')(io);

// ---------------- Routes ----------------
app.use('/api', require('./routes/health'));
app.use('/api', require('./routes/capture'));
app.use('/api', require('./routes/packet'));
app.use('/api', require('./routes/block'));

// ---------------- Start Server ----------------
const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log('\nSentinelAI Backend LIVE');
  console.log(`http://localhost:${PORT}`);
  console.log(`Health: http://localhost:${PORT}/api/health\n`);
});