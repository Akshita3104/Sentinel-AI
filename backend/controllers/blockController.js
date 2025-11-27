const axios = require("axios");

const io = (req) => req.app.get("io");
const LAPTOP_IP = global.LAPTOP_IP || "127.0.0.1";

// Point this to your Flask app
const FLASK_URL = process.env.FLASK_URL || "http://localhost:5001";

// --------------------------------------------------
// GET BLOCKED IPs
// --------------------------------------------------
module.exports.getBlockedIPs = (req, res) => {
  res.json(global.blockedIPs);
};

// --------------------------------------------------
// EMIT / REGISTER A BLOCKED IP (called by Flask)
// --------------------------------------------------
module.exports.emitBlockedIP = (req, res) => {
  const {
    ip,
    confidence = 99,
    reason = "DDoS Flood",
    threatLevel,
    timestamp,
    isSimulated,
    network_slice,
    slice_priority,
  } = req.body;

  if (!ip) return res.status(400).json({ error: "No IP provided" });

  // Prefer threatLevel from Flask if provided, else derive from confidence
  const level =
    threatLevel ||
    (confidence > 90 ? "high" : "medium");

  const block = {
    ip,
    timestamp: timestamp || new Date().toISOString(),
    reason,
    threatLevel: level,
    mitigation: "SDN DROP Rule",
    isSimulated: !!isSimulated,
    network_slice: network_slice || "eMBB",
    slice_priority: slice_priority ?? 2,
  };

  if (!global.blockedIPs.find((b) => b.ip === ip)) {
    global.blockedIPs.push(block);

    // Also push into maliciousPackets for history
    global.maliciousPackets.push({
      id: Date.now(),
      timestamp: Date.now(),
      srcIP: ip,
      dstIP: LAPTOP_IP,
      protocol: "UDP",
      packetSize: 1024,
      action: "Blocked",
      prediction: "ddos",
      isSimulated: !!isSimulated,
      network_slice: block.network_slice,
      slice_priority: block.slice_priority,
    });
  }

  const socket = io(req);
  socket.emit("ip_blocked", block);
  socket.emit("update_blocked_ips", global.blockedIPs);
  socket.emit("detection-result", {
    ip,
    is_ddos: true,
    confidence: confidence / 100,
    prediction: "ddos",
    abuseScore: confidence,
    threat_level: level.toUpperCase(),
  });

  console.log(`Blocked IP emitted: ${ip}`);
  res.json({ success: true });
};

// --------------------------------------------------
// UNBLOCK IP – coordinated with Flask + Ryu
// --------------------------------------------------
module.exports.unblockIP = async (req, res) => {
  const { ip } = req.body;
  if (!ip) {
    return res.status(400).json({ error: "No IP provided" });
  }

  try {
    // 1) Ask Flask to unblock (which also talks to Ryu)
    const flaskRes = await axios.post(
      `${FLASK_URL}/unblock`,
      { ip },
      { timeout: 3000 }
    );

    const { success } = flaskRes.data || {};

    if (!success) {
      console.error(`Flask reported failure unblocking IP ${ip}`);
      return res
        .status(500)
        .json({ success: false, error: "Failed to unblock in SDN/Flask" });
    }

    // 2) Only if Flask says "success", update Node in-memory state + UI
    global.blockedIPs = global.blockedIPs.filter((b) => b.ip !== ip);

    const socket = io(req);
    socket.emit("update_blocked_ips", global.blockedIPs);
    socket.emit("unblocked_ip", { ip });

    console.log(`Unblocked IP (Node + Flask + Ryu): ${ip}`);
    return res.json({ success: true });
  } catch (err) {
    console.error(`Error calling Flask /unblock for IP ${ip}:`, err.message || err);
    return res
      .status(500)
      .json({ success: false, error: "Flask /unblock unreachable or failed" });
  }
};
