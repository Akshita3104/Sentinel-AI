const express = require('express');
const router = express.Router();
const { emitBlockedIP, unblockIP, getBlockedIPs } = require('../controllers/blockController');

router.get('/blocked-ips', getBlockedIPs);
router.post('/emit-blocked-ip', emitBlockedIP);
router.post('/unblock', unblockIP);

module.exports = router;