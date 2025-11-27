const express = require('express');
const router = express.Router();
const { receiveLivePacket } = require('../controllers/packetController');

router.post('/live-packet', receiveLivePacket);

module.exports = router;