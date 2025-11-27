const axios = require('axios');
const FLASK_URL = 'http://localhost:5001';
const io = (req) => req.app.get('io');

module.exports.startCapture = async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/start-capture`);
    global.isCapturing = true;
    io(req).emit('capture-started');
    console.log("Capture started via Flask");
    res.json({ success: true });
  } catch (err) {
    console.error('Error starting capture:', err.message);
    res.json({ success: false, error: err.message });
  }
};

module.exports.stopCapture = async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/stop-capture`);
    global.isCapturing = false;
    io(req).emit('capture-stopped');
    console.log("Capture stopped via Flask");
    res.json({ success: true });
  } catch (err) {
    console.error('Error stopping capture:', err.message);
    res.json({ success: false, error: err.message });
  }
};