# this is a python code to SIMULATE a sensor node (like Raspberry Pi) publishing data to AWS IoT Core using MQTT over TLS
# it supports multiple sensor types and generates random data for each type

import time
import json
import ssl
import random
import threading
import paho.mqtt.client as mqtt
import os
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("sensor")

# Environment variables
CERTS_DIR = os.getenv("CERTS_DIR", "./certs")
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "aws.iot.ap-south-1.amazonaws.com")
SENSOR_TYPE = os.getenv("SENSOR_TYPE", "temperature").lower()
FREQ = int(os.getenv("FREQ", 5))
RANGE = os.getenv("RANGE", None)  # "min,max"
LOCATION = os.getenv("LOCATION", "default").lower()
ID = os.getenv("ID", "rpi").lower()

# File paths
CA_CERT = os.path.join(CERTS_DIR, "rootCA.pem")
CERT_FILE = os.path.join(CERTS_DIR, "device-certificate.pem.crt")
KEY_FILE = os.path.join(CERTS_DIR, "device-private.pem.key")

# Derived identifiers
DEVICE_ID = f"{ID}-{SENSOR_TYPE}"

# Topics
STATUS_TOPIC = f"myhome/status/{LOCATION}/{SENSOR_TYPE}"
TELEMETRY_TOPIC = f"myhome/telemetry/{LOCATION}/{SENSOR_TYPE}"
ALL_DEVICES_TOPIC = "myhome/all-devices"

# One-time registry publish guard
_registry_published = False

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    global _registry_published
    logger.info("Connected with result code %s", str(rc))
    # Publish device online status once on successful connection
    status_payload = {"deviceId": DEVICE_ID, "status": "online", "location": LOCATION, "timestamp": int(time.time())}
    client.publish(STATUS_TOPIC, json.dumps(status_payload), qos=1, retain=True)

    # Publish registry info once per process boot
    if not _registry_published:
        registry_payload = {
            "deviceId": DEVICE_ID,
            "location": LOCATION,
            "topics": [STATUS_TOPIC, TELEMETRY_TOPIC],
            "timestamp": int(time.time()),
        }
        client.publish(ALL_DEVICES_TOPIC, json.dumps(registry_payload), qos=1, retain=False)
        logger.info("Published registry: %s", registry_payload)
        _registry_published = True

# MQTT client
client = mqtt.Client(client_id=DEVICE_ID)
client.on_connect = on_connect
client.enable_logger(logger)

# Set LWT offline retained message (include timestamp and location)
lwt_payload = json.dumps({"deviceId": DEVICE_ID, "status": "offline", "location": LOCATION, "timestamp": int(time.time())})
client.will_set(STATUS_TOPIC, payload=lwt_payload, qos=1, retain=True)

client.tls_set(
    ca_certs=CA_CERT,
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(False)

client.connect(AWS_IOT_ENDPOINT, 8883, 60)

# ---------- Sensor Generators ----------
def generate_temperature():
    min_v, max_v = (20.0, 35.0)
    if RANGE:
        min_v, max_v = map(float, RANGE.split(","))
    return round(random.uniform(min_v, max_v), 2)

def generate_humidity():
    min_v, max_v = (30, 90)
    if RANGE:
        min_v, max_v = map(int, RANGE.split(","))
    return random.randint(min_v, max_v)

def generate_motion():
    return random.choice([True, False])

def generate_door():
    return random.choice(["open", "closed"])

def generate_energy():
    min_v, max_v = (0.1, 5.0)
    if RANGE:
        min_v, max_v = map(float, RANGE.split(","))
    return round(random.uniform(min_v, max_v), 3)

def generate_light():
    min_v, max_v = (100, 1000)
    if RANGE:
        min_v, max_v = map(int, RANGE.split(","))
    return random.randint(min_v, max_v)

SENSOR_FUNCTIONS = {
    "temperature": generate_temperature,
    "humidity": generate_humidity,
    "motion": generate_motion,
    "door": generate_door,
    "energy": generate_energy,
    "light": generate_light
}

# ---------- Telemetry Loop ----------
def telemetry_sender(sensor_type):
    generator = SENSOR_FUNCTIONS.get(sensor_type)
    if not generator:
        logger.error("Unknown sensor type: %s", sensor_type)
        return

    while True:
        payload = {
            "deviceId": DEVICE_ID,
            "sensor": sensor_type,
            "value": generator(),
            "timestamp": int(time.time()),
            "location": LOCATION,
        }
        logger.info("Publishing to %s: %s", TELEMETRY_TOPIC, payload)
        client.publish(TELEMETRY_TOPIC, json.dumps(payload), qos=1, retain=False)
        time.sleep(FREQ)

# ---------- Main ----------
def main():
    logger.info(
        "Starting telemetry sender for sensor_type=%s, device_id=%s, location=%s, freq=%s",
        SENSOR_TYPE,
        DEVICE_ID,
        LOCATION,
        FREQ,
    )
    sender_thread = threading.Thread(target=telemetry_sender, args=(SENSOR_TYPE,), daemon=True)
    sender_thread.start()
    client.loop_forever()

if __name__ == "__main__":
    main()
