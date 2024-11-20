import paho.mqtt.client as mqtt
from config.config import BROKER, PORT
import logging
import log

class MQTTClient:
    def __init__(self, client_name, broker_address, on_message_callback, port=1883):
        self.client_name = client_name
        self.broker_address = broker_address
        self.port = port
        self.on_message_callback = on_message_callback
        self.topics = []

        self.client = mqtt.Client(client_name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker")
            topics = []
            for topic in self.topics:
                _t = (topic, 0)
                topics.append(_t)
            client.subscribe(topics)  # Subscribe to a topic when connected
        else:
            logging.info("Connection failed")

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        topic = message.topic
        self.on_message_callback(topic, payload)

    def connect(self):
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()

    def publish(self, topic, message):
        self.client.publish(topic, message)

# Define a callback function to be executed when a message is received
def do_something(topic, message):
    logging.info(f"Received message '{message}' on topic '{topic}'")
    # Add your custom logic here

if __name__ == "__main__":
    client = MQTTClient("TannedCung", BROKER, on_message_callback=do_something, port=PORT)

    client.connect()

    # # Publish a message
    client.publish("/bluetooth/list_songs", "Song 4, Song 5, Song 6")
    logging.info(f"[INFO]: published to /bluetooth/list_songs")

    # Keep the program running (you can add your own logic here)
    while True:
        pass
