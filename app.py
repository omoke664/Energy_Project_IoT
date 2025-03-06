import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["energy_db"]  # Your database name
collection = db["sensor_data"]  # Your collection name

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# MQTT Callback Functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("Received MQTT message:", data)
    collection.insert_one(data)  # Store in MongoDB

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

@app.route('/')
def home():
    return "Flask app running on Azure App Service!"

@app.route('/energy', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        collection.insert_one(data)
        return jsonify({"message": "Data stored successfully"}), 201
    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
