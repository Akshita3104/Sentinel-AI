const express = require('express');
const router = express.Router();

router.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    ip: global.LAPTOP_IP, 
    time: new Date().toISOString() 
  });
});

module.exports = router;