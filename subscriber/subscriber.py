import os
import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "state_estimation/results")

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://root:example@mongo:27017")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.state_estimation
collection = db.results

# MQTT Callback
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    collection.insert_one({"results": data})
    print("Inserted state estimation results into MongoDB.")

# MQTT Client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)
client.on_message = on_message

# Keep listening
print("Subscriber listening for messages...")
client.loop_forever()
