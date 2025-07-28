// API: Get all players (for analytics dashboard)
app.get("/players/all", (req, res) => {
  const query = "SELECT id, name, uid, credit, points FROM users";
  db.all(query, [], (err, rows) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: "Database error" });
    }
    // Map rows to frontend format
    const players = rows.map(row => ({
      id: row.id,
      name: row.name,
      rfid_number: row.uid,
      credit: row.credit,
      points: row.points,
      is_admin: row.name && (row.name.toLowerCase() === 'admin' || row.uid === 'ADMIN_UID')
    }));
    res.json(players);
  });
});
const express = require("express");
const cors = require("cors");
const mqtt = require("mqtt");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());

// SQLite Database setup
const dbPath = path.join(__dirname, '../../arpi.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database at:', dbPath);
  }
});

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

// API: Get player by RFID
app.get("/players/rfid/:rfid", (req, res) => {
  const rfid = req.params.rfid;
  
  const query = "SELECT id, name, uid, credit, points FROM users WHERE uid = ?";
  
  db.get(query, [rfid], (err, row) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: "Database error" });
    }
    
    if (!row) {
      return res.status(404).json({ error: "RFID not registered" });
    }
    
    // Return player data with is_admin flag (you can modify this logic as needed)
    const playerData = {
      id: row.id,
      name: row.name,
      uid: row.uid,
      rfid_number: row.uid, // Add this for frontend compatibility
      credit: row.credit,
      points: row.points,
      is_admin: row.name.toLowerCase() === 'admin' || row.uid === 'ADMIN_UID' // Modify this condition as needed
    };
    
    console.log(`[DB] Player found: ${row.name} (${row.uid})`);
    res.json(playerData);
  });
});

// API: Register new RFID or check if it exists
app.post("/rfid-register", (req, res) => {
  const { rfid, name } = req.body;

  if (!rfid || !name) {
    return res.status(400).json({ error: "Missing RFID or name parameter" });
  }

  // Check if the RFID already exists in the database
  const checkQuery = "SELECT id FROM users WHERE uid = ?";
  db.get(checkQuery, [rfid], (err, row) => {
    if (err) {
      console.error("Database error:", err);
      return res.status(500).json({ error: "Database error" });
    }

    if (row) {
      return res.status(400).json({ error: "RFID already registered" });
    }

    // If RFID doesn't exist, register it
    const insertQuery = "INSERT INTO users (uid, name, credit, points) VALUES (?, ?, 0, 0)";
    db.run(insertQuery, [rfid, name], function (err) {
      if (err) {
        console.error("Database error:", err);
        return res.status(500).json({ error: "Database error" });
      }

      console.log(`[DB] Registered new RFID: ${rfid} for user: ${name}`);
      res.json({ success: true, message: "RFID registered successfully", userId: this.lastID });
    });
  });
});

// API: Deduct points from player
app.post("/players/deduct_points/", (req, res) => {
  const { rfid_number, points } = req.query;
  
  if (!rfid_number || !points) {
    return res.status(400).json({ error: "Missing rfid_number or points parameter" });
  }
  
  const pointsToDeduct = parseInt(points);
  if (isNaN(pointsToDeduct) || pointsToDeduct <= 0) {
    return res.status(400).json({ error: "Invalid points value" });
  }
  
  // First, check current points
  const checkQuery = "SELECT points FROM users WHERE uid = ?";
  db.get(checkQuery, [rfid_number], (err, row) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: "Database error" });
    }
    
    if (!row) {
      return res.status(404).json({ error: "Player not found" });
    }
    
    if (row.points < pointsToDeduct) {
      return res.status(400).json({ error: "Insufficient points" });
    }
    
    // Deduct points
    const updateQuery = "UPDATE users SET points = points - ? WHERE uid = ?";
    db.run(updateQuery, [pointsToDeduct, rfid_number], function(err) {
      if (err) {
        console.error('Database error:', err);
        return res.status(500).json({ error: "Database error" });
      }
      
      const newPoints = row.points - pointsToDeduct;
      console.log(`[DB] Deducted ${pointsToDeduct} points from ${rfid_number}. New balance: ${newPoints}`);
      res.json({ success: true, new_points: newPoints });
    });
  });
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
  console.log("  GET  /players/rfid/:rfid - Get player data by RFID");
  console.log("  POST /players/deduct_points/ - Deduct points from player");
});
