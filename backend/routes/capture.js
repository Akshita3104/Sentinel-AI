const express = require('express');
const router = express.Router();
const { startCapture, stopCapture } = require('../controllers/captureController');

router.post('/start-capture', startCapture);
router.post('/stop-capture', stopCapture);

module.exports = router;