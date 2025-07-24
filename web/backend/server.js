const express = require("express");
const cors = require("cors");
const mqtt = require("mqtt");

const app = express();
app.use(cors());
app.use(express.json());

// MQTT Client
const mqttClient = mqtt.connect("mqtt://192.168.1.28:1883", {
  clientId: `web-server-${Math.random().toString(16).substr(2, 8)}`,
  reconnectPeriod: 1000,
  keepalive: 60
});

// Storage for pending requests
let pendingRfidRequest = null;
let pendingCoinRequest = null;
let coinDetectionActive = false; // Track if coin detection is active

mqttClient.on("connect", () => {
  console.log("MQTT connected to broker");
  mqttClient.subscribe("esp32/data");
});

mqttClient.on("message", (topic, message) => {
  try {
    const packet = JSON.parse(message.toString());
    const type = packet.type;
    const data = packet.data;

    console.log(packet);
    
    if (type === "RFID" && pendingRfidRequest) {
      console.log(`[RFID] UID received: ${data}`);
      pendingRfidRequest.json({ success: true, uid: data });
      pendingRfidRequest = null;
    }
    
    if (type === "COIN" && coinDetectionActive) {
      console.log(`[COIN] Detected: ${data}`);
      // Check if it's a valid coin insertion
      if (data === 1 || data === "1" || data === "detected" || data === "INSERTED") {
        // Send response to the current pending request if there is one
        if (pendingCoinRequest) {
          pendingCoinRequest.json({ success: true, message: "Coin detected", timestamp: new Date().toISOString() });
          pendingCoinRequest = null;
        }
        // Note: Coin detection stays active for future insertions
        console.log("[COIN] Coin detection remains active for future insertions");
      }
    }
  } catch (error) {
    // Ignore parse errors
  }
});

// API: Start RFID scan and wait for result
app.post("/rfid-scan", (req, res) => {
  if (pendingRfidRequest) {
    return res.status(400).json({ error: "RFID scan already in progress" });
  }
  
  if (!mqttClient.connected) {
    return res.status(503).json({ error: "MQTT not connected" });
  }
  
  // Start RFID scanning
  mqttClient.publish("esp32/control/esp1", JSON.stringify({ status: "START_RFID" }));
  console.log("[API] RFID scan started");
  
  // Store the response object to reply when RFID data arrives
  pendingRfidRequest = res;
  
  // Timeout after 30 seconds
  setTimeout(() => {
    if (pendingRfidRequest === res) {
      pendingRfidRequest = null;
      res.status(408).json({ error: "RFID scan timeout" });
    }
  }, 30000);
});

// API: Start coin acceptor and wait for coin
app.post("/coin-wait", (req, res) => {
  if (!mqttClient.connected) {
    return res.status(503).json({ error: "MQTT not connected" });
  }
  
  // If coin detection is not active, start it
  if (!coinDetectionActive) {
    mqttClient.publish("esp32/control/esp2", JSON.stringify({ "status" : "START_COIN" }));
    coinDetectionActive = true;
    console.log("[API] Coin acceptor started and will remain active");
  }
  
  // If there's already a pending request, reject this one
  if (pendingCoinRequest) {
    return res.status(400).json({ error: "Already waiting for coin - only one request at a time" });
  }
  
  console.log("[API] Waiting for next coin insertion");
  
  // Store the response object to reply when coin is detected
  pendingCoinRequest = res;
  
  // Timeout after 60 seconds for this specific request
  setTimeout(() => {
    if (pendingCoinRequest === res) {
      pendingCoinRequest = null;
      res.status(408).json({ error: "Coin detection timeout - but coin acceptor remains active" });
    }
  }, 60000);
});

// API: Stop coin acceptor
app.post("/coin-stop", (req, res) => {
  if (!mqttClient.connected) {
    return res.status(503).json({ error: "MQTT not connected" });
  }
  
  // Stop coin detection
  mqttClient.publish("esp32/control/esp2", JSON.stringify({ "status" : "STOP_COIN" }));
  coinDetectionActive = false;
  
  // Cancel any pending request
  if (pendingCoinRequest) {
    pendingCoinRequest.status(200).json({ message: "Coin detection stopped" });
    pendingCoinRequest = null;
  }
  
  console.log("[API] Coin acceptor stopped");
  res.json({ success: true, message: "Coin acceptor stopped" });
});

// Simple status check
app.get("/status", (req, res) => {
  res.json({ 
    mqtt_connected: mqttClient.connected,
    rfid_scanning: pendingRfidRequest !== null,
    coin_waiting: pendingCoinRequest !== null,
    coin_detection_active: coinDetectionActive
  });
});

app.listen(3001, () => {
  console.log("Server running on port 3001");
  console.log("API endpoints:");
  console.log("  POST /rfid-scan  - Start RFID scan, returns UID when scanned");
  console.log("  POST /coin-wait  - Wait for coin insertion (keeps coin acceptor active)");
  console.log("  POST /coin-stop  - Stop coin acceptor");
  console.log("  GET  /status     - Check server status");
});
