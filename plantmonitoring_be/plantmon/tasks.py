from paho.mqtt import client as mqtt_client
from django.conf import settings
from celery import shared_task
import json
import time


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n" % rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.username_pw_set(settings.HIVEMQ_BROKER_USERNAME, settings.HIVEMQ_BROKER_PASSWORD)
    client.tls_set(tls_version=mqtt_client.ssl.PROTOCOL_TLS)
    client.connect(settings.HIVEMQ_BROKER_ADDRESS, int(settings.HIVEMQ_BROKER_PORT))
    return client


def publish_message(payload, topic):
    client = connect_mqtt()
    client.loop_start()
    print("wait for setup")
    time.sleep(5)
    result = client.publish(topic, json.dumps(payload))
    status = result[0]
    if status == 0:
        print("Sent command")
    else:
        print(f"Failed to send message to topic {topic}")
    client.disconnect()


@shared_task
def manual_watering(device_id):
    payload = {
        'device': device_id,
        'command': 'water'
    }
    publish_message(payload, settings.COMMANDS_TOPIC)


@shared_task
def update_watering_mode(data):
    payload = {
        'device': data.get('device_id'),
        'command': 'update',
        'watering_mode': data.get('watering_mode'),
        'time_interval': data.get('time_interval')
    }
    publish_message(payload, settings.COMMANDS_TOPIC)
