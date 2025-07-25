#!/usr/bin/env python3
"""
mqtt_terminal.py - Interactive terminal that talks to the ESP32 "MQTT-CONTROLLED TESTER"

Type commands such as:
    STATUS
    START_RFID
    LED_RUN
    exit

and the script will publish the proper JSON payload the ESP32 expects.

Requires: pip install paho-mqtt
"""

import json
import sys
import time
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER_HOST = "192.168.1.28"
BROKER_PORT = 1883

TOPIC_CMDS  = "esp32/control"   # ESP32 subscribes here
TOPIC_WATCH = "esp32/#"         # Watch all ESP32 responses

# Add a global for a user callback
rfid_callback = None
coin_callback = None
touch_callback = None
proximity_callback = None
led_callback = None
ultrasonic_callback = None

def set_rfid_callback(cb):
    global rfid_callback
    rfid_callback = cb

def set_coin_callback(cb):
    global coin_callback
    coin_callback = cb

def set_touch_callback(cb):
    global touch_callback
    touch_callback = cb

def set_proximity_callback(cb):
    global proximity_callback
    proximity_callback = cb

def set_led_callback(cb):
    global led_callback
    led_callback = cb

def set_ultrasonic_callback(cb):
    global ultrasonic_callback
    ultrasonic_callback = cb

# MQTT Callbacks
def on_connect(client, _userdata, _flags, rc, _props=None):
    if rc == 0:
        print(f"[MQTT] Connected to {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_WATCH)
    else:
        print(f"[MQTT] Connection failed (rc={rc})")

def on_message(_client, _userdata, msg):
    try:
        payload = msg.payload.decode()
        packet = json.loads(payload)
        typ = packet.get("type", "RAW")
        if   typ == "LOG":      print(f"[LOG]    {packet['data']}")
        elif typ == "RFID":
            print(f"[RFID]   UID: {packet['data']}")
            if rfid_callback:
                rfid_callback(packet['data'])
        elif typ == "COIN":
            print(f"[COIN]   Raw packet: {packet}")
            print(f"[COIN]   Data: {packet['data']}")
            print(f"[COIN]   Data type: {type(packet['data'])}")
            
            # Only trigger callback if coin was actually inserted (data should indicate insertion)
            coin_inserted = False
            try:
                # Handle different possible data formats
                coin_data = packet['data']
                if coin_data == 1 or coin_data == "1" or coin_data is True or coin_data == "INSERTED" or coin_data == "detected":
                    coin_inserted = True
                    print(f"[COIN]   ✅ Valid coin insertion detected: {coin_data}")
                else:
                    print(f"[COIN]   ❌ Invalid coin data (not insertion): {coin_data}")
            except:
                print(f"[COIN]   ❌ Error parsing coin data: {packet.get('data', 'NO_DATA')}")
            
            if coin_inserted and coin_callback:
                print(f"[COIN]   🪙 Triggering coin callback")
                coin_callback()
            elif coin_callback:
                print(f"[COIN]   🚫 Coin callback NOT triggered - invalid data")
        elif typ == "TOUCH":
            print(f"[TOUCH]  Sensor index: {packet['data']}")
            if touch_callback:
                touch_callback(packet['data'])
        elif typ == "PROXIMITY":
            print(f"[PROXIMITY]  {packet}")
            if proximity_callback:
                proximity_callback(packet['data'])
        elif typ == "LED":      
            print(f"[LED]    {packet['data']}")
            if led_callback:
                led_callback(packet['data'])
        elif typ == "ULTRASONIC":
            print(f"[ULTRASONIC]  {packet}")
            if ultrasonic_callback:
                ultrasonic_callback(packet)
        elif typ == "SERVO":    print(f"[SERVO]  {packet['data']}")
        else:                   print(f"[{typ}]  {packet}")
    except Exception:
        print(f"[{msg.topic}] {msg.payload.decode()}")

# Send MQTT Command
def send_status_cmd(client, cmd: str, topic_override=None):
    payload = json.dumps({"status": cmd})
    topic = topic_override if topic_override else TOPIC_CMDS
    client.publish(topic, payload, qos=1)
    print(f"[? CMD] {payload} to {topic}")

def interactive_repl(client):
    help_msg = """
Available commands
------------------
  START_RFID     STOP_RFID
  START_TOUCH    STOP_TOUCH
  LED_RUN        SERVO_RUN
  exit           # quit
"""
    print(help_msg)
    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue
            if line.lower() == "exit":
                break
            send_status_cmd(client, line.upper())
        except (EOFError, KeyboardInterrupt):
            break

# Main Entry Point
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="PiControlClient")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    if len(sys.argv) > 1:
        send_status_cmd(client, sys.argv[1].upper())
        time.sleep(30)
    else:
        interactive_repl(client)

    client.loop_stop()
    client.disconnect()
    print("Bye!")

if __name__ == "__main__":
    main()
