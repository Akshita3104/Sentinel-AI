module.exports.receiveLivePacket = (req, res) => {
  const packet = req.body;
  global.packetCount++;

  req.app.get('io').emit('new_packet', packet);

  console.log(`[${global.packetCount}] Packet from ${packet.srcIP || 'unknown'} → ${packet.dstIP || 'unknown'}`);

  res.json({ ok: true });
};