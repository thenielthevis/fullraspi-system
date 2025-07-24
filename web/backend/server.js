const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const mqtt = require("mqtt");

const app = express();
app.use(cors());
app.use(express.json());

// const db = new sqlite3.Database("data.db");
const mqttClient = mqtt.connect("mqtt://192.168.1.28:1883");

// --- MQTT LISTENERS ---
mqttClient.on("connect", () => {
  console.log("MQTT connected");
  mqttClient.subscribe("esp32/coin");
  mqttClient.subscribe("esp32/rfid");
});

mqttClient.on("message", (topic, message) => {
  console.log(`[${topic}] ${message.toString()}`);
  // Store or process messages as needed
});

// --- API ROUTES ---
// app.get("/coins", (req, res) => {
//   db.all("SELECT * FROM coins", [], (err, rows) => {
//     if (err) return res.status(500).json({ error: err.message });
//     res.json(rows);
//   });
// });

app.post("/send-command", (req, res) => {
  const { topic, message } = req.body;
  mqttClient.publish(topic, message);
  res.json({ status: "sent" });
});

app.listen(3001, () => console.log("Server running on port 3001"));
