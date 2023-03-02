from paho.mqtt import client as mqtt_client
from django.conf import settings
from celery.signals import celeryd_after_setup
from plantmon.serializers import DeviceReadingsSerializer
from datetime import datetime
import json


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


@celeryd_after_setup.connect
def consume_device_metric(sender, instance, **kwargs):
    client = connect_mqtt()

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic", type(msg.payload.decode()))
        payload = json.loads(msg.payload.decode())
        payload['timestamp'] = datetime.fromtimestamp(payload['timestamp'])
        serializer = DeviceReadingsSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()

    client.subscribe(settings.HIVEMQ_BROKER_TOPIC)
    client.on_message = on_message
    client.loop_forever()
    
