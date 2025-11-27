module.exports = (req, res, next) => {
  if (req.method === "POST" && 
      (req.path === "/api/start-capture" || req.path === "/api/stop-capture")) {
    if (req.get("X-Simulated-Attack") === "true") {
      console.log("Ignoring simulated client request to start/stop capture");
      return res.status(200).json({ 
        success: false, 
        message: "Simulated clients cannot start/stop capture" 
      });
    }
  }
  next();
};