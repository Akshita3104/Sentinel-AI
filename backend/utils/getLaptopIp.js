const os = require('os');

function getLaptopIp() {
  try {
    const ifaces = os.networkInterfaces();
    for (const iface of Object.values(ifaces)) {
      for (const info of iface) {
        if (info.family === 'IPv4' && !info.internal) {
          return info.address;
        }
      }
    }
  } catch (e) {
    console.error('Failed to detect IP:', e);
  }
  return '127.0.0.1';
}

module.exports = getLaptopIp;