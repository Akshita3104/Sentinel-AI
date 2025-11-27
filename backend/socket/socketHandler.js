module.exports = (io) => {
  io.on('connection', (socket) => {
    console.log('Frontend CONNECTED:', socket.id);

    socket.emit('initial_blocked_ips', global.blockedIPs);
    socket.emit('capture-status', {
      isCapturing: global.isCapturing,
      packetCount: global.packetCount,
      packetsPerSecond: 0,
      totalBytes: 0,
      duration: 0
    });

    socket.on('disconnect', () => {
      console.log('Frontend disconnected');
    });
  });
};