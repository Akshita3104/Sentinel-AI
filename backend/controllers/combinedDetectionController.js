// combinedDetectionController.js
const axios = require('axios');
const os = require('os');
require('dotenv').config();
const { blockIP } = require('./ipDetectionController'); // Import blockIP for mitigation

// Optimized clients with connection pooling
const mlClient = axios.create({
  baseURL: process.env.ML_MODEL_URL?.replace('/predict', '') || 'http://localhost:5001',
  timeout: 3000,
  headers: { 'Content-Type': 'application/json', 'Connection': 'keep-alive' },
  httpAgent: new (require('http').Agent)({ 
    keepAlive: true, 
    maxSockets: 20, 
    maxFreeSockets: 10,
    timeout: 3000,
    keepAliveMsecs: 1000
  })
});

// ML Model health check
let mlModelHealthy = false;
const checkMLHealth = async () => {
  try {
    const response = await mlClient.get('/health', { timeout: 2000 });
    mlModelHealthy = response.status === 200;
    if (mlModelHealthy) {
      console.log('ML Model is healthy and responding');
    }
    return mlModelHealthy;
  } catch (error) {
    mlModelHealthy = false;
    console.log('ML Model health check failed:', error.message);
    return false;
  }
};

// Check ML health every 10 seconds
setInterval(checkMLHealth, 10000);
checkMLHealth(); // Initial check

const abuseClient = axios.create({
  baseURL: process.env.ABUSEIPDB_URL?.replace('/check', '') || 'https://api.abuseipdb.com/api/v2',
  timeout: 200,
  headers: { 
    'Key': process.env.ABUSEIPDB_API_KEY,
    'Accept': 'application/json',
    'Connection': 'keep-alive'
  },
  httpsAgent: new (require('https').Agent)({ 
    keepAlive: true, 
    maxSockets: 10,
    maxFreeSockets: 5,
    timeout: 200,
    keepAliveMsecs: 500
  })
});

// Response cache for ultra-fast repeated requests
const responseCache = new Map();
const CACHE_TTL = 10000; // 10 seconds

// Get system's local IP (destination IP)
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const [name, nets] of Object.entries(interfaces)) {
    const nameL = name.toLowerCase();
    const isEthernet = nameL.includes('ethernet');
    const isWiFi = nameL.includes('wi-fi') || nameL.includes('wifi') || nameL.includes('wlan');
    if ((isEthernet || isWiFi) && nets) {
      for (const net of nets) {
        if (net.family === 'IPv4' && !net.internal) {
          return net.address;
        }
      }
    }
  }
  return '127.0.0.1';
}

const THREAT_THRESHOLD = 0.7;
const ABUSE_THRESHOLD = 50;

function calculateVariance(traffic) {
  const mean = traffic.reduce((a, b) => a + b, 0) / traffic.length;
  return traffic.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / traffic.length;
}

function calculateBandwidth(traffic, packet_data) {
  const avgTraffic = traffic.reduce((a, b) => a + b, 0) / traffic.length;
  const packetSize = packet_data?.avg_packet_size || 1500;
  return (avgTraffic * packetSize) / (1000 * 1000); // Convert to Mbps
}

function generateMaliciousPacketData(ip, network_slice, finalResponse) {
  return [
    {
      srcIP: ip,
      dstIP: getLocalIP(),
      protocol: 'TCP',
      size: Math.floor(Math.random() * 1000) + 500,
      timestamp: Date.now()
    }
  ];
}

const detectDDoSCombined = async (req, res) => {
  const startTime = Date.now();
  const { traffic, ip, packet_data, network_slice } = req.body;
  const cacheKey = `${ip}:${traffic.join(',')}`;

  // Check cache
  const cached = responseCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return res.json(cached.data);
  }

  // Validate input
  if (!Array.isArray(traffic) || traffic.length === 0) {
    return res.status(400).json({ error: 'Invalid traffic data' });
  }
  if (!ip) {
    return res.status(400).json({ error: 'IP required' });
  }

  const io = req.app.get('io');

  let mlData = null;
  if (mlModelHealthy) {
    try {
      const response = await mlClient.post('/predict', {
        traffic,
        ip_address: ip,
        packet_data: packet_data || {},
        network_slice: network_slice || 'eMBB'
      });
      mlData = response.data;
    } catch (error) {
      console.error('ML model request failed:', error.message);
    }
  }

  // Fallback if ML unavailable
  if (!mlData) {
    const avgTraffic = traffic.reduce((a, b) => a + b, 0) / traffic.length;
    const variance = calculateVariance(traffic);
    const bandwidth = calculateBandwidth(traffic, packet_data);
    const fallbackScore = (avgTraffic / 1000 + variance / 100 + bandwidth) / 3;
    mlData = {
      prediction: fallbackScore > 0.7 ? 'ddos' : 'normal',
      confidence: Math.min(0.99, fallbackScore),
      threat_level: fallbackScore > 0.85 ? 'HIGH' : fallbackScore > 0.6 ? 'MEDIUM' : 'LOW'
    };
  }

  // Get AbuseIPDB score
  let abuseScore = 0;
  try {
    const abuseResponse = await abuseClient.get('/check', {
      params: { ipAddress: ip, maxAgeInDays: 90 }
    });
    abuseScore = abuseResponse.data.data.abuseConfidenceScore || 0;
  } catch (error) {
    console.error('AbuseIPDB failed:', error.message);
  }

  // Combine scores
  const mlThreatScore = (mlData.prediction === 'ddos' ? 1.0 : mlData.prediction === 'suspicious' ? 0.6 : 0) * (mlData.confidence || 0.7);
  const abuseThreatScore = abuseScore > ABUSE_THRESHOLD ? 0.8 : abuseScore > 30 ? 0.4 : 0;
  const combinedScore = (mlThreatScore * 0.7) + (abuseThreatScore * 0.3);

  const isMalicious = combinedScore >= THREAT_THRESHOLD;

  // === Mitigation: Block Source IP ===
  if (isMalicious) {
    try {
      await blockIP(ip, `DDoS detected (score: ${combinedScore.toFixed(2)})`);
      console.log(`BLOCKED source IP: ${ip}`);
    } catch (err) {
      console.error('Failed to block IP:', err.message);
    }
  }

  // === Build Binary Response ===
  const finalResponse = {
    prediction: isMalicious ? 'malicious' : 'normal',
    confidence: Math.min(0.99, combinedScore),
    isMalicious,
    source_ip: ip,
    destination_ip: getLocalIP(),
    abuseScore,
    ml_model_used: !!mlData,
    threat_score: combinedScore.toFixed(3),
    message: isMalicious 
      ? `Malicious traffic from ${ip} blocked` 
      : `Normal traffic from ${ip}`,
    network_slice: network_slice || 'eMBB',
    timestamp: new Date().toISOString(),
    response_time: Date.now() - startTime
  };

  // === Add network analysis ===
  if (traffic.length > 0) {
    finalResponse.network_analysis = {
      max_traffic: Math.max(...traffic),
      avg_traffic: traffic.reduce((a, b) => a + b, 0) / traffic.length,
      traffic_variance: calculateVariance(traffic),
      bandwidth_mbps: calculateBandwidth(traffic, packet_data),
      packet_rate: packet_data?.packet_rate || 0
    };
  }

  // === WebSocket Real-Time Alert ===
  if (io) {
    io.emit('detection-result', {
      ...finalResponse,
      maliciousPackets: isMalicious ? generateMaliciousPacketData(ip, network_slice, finalResponse) : []
    });

    io.emit('detection-log', {
      type: isMalicious ? 'error' : 'success',
      message: `${isMalicious ? 'MALICIOUS' : 'NORMAL'} [${ip}] → ${getLocalIP()} | Score: ${combinedScore.toFixed(2)}`,
      timestamp: new Date().toISOString()
    });
  }

  // === Cache & Respond ===
  responseCache.set(cacheKey, { data: finalResponse, timestamp: Date.now() });
  res.json(finalResponse);
};

module.exports = { 
  detectDDoSCombined, 
  generateMaliciousPacketData, 
  checkMLHealth,
  getLocalIP 
};