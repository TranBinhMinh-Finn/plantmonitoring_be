from paho.mqtt import client as mqtt_client
from django.conf import settings
from plantmon.serializers import DeviceReadingsSerializer
from datetime import datetime
import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write("Connected to MQTT Broker!")
        else:
            self.stdout.write("Failed to connect, return code %d\n" % rc)

    def connect_mqtt(self) -> mqtt_client:
        client = mqtt_client.Client()
        client.on_connect = self.on_connect
        client.username_pw_set(settings.HIVEMQ_BROKER_USERNAME, settings.HIVEMQ_BROKER_PASSWORD)
        client.tls_set(tls_version=mqtt_client.ssl.PROTOCOL_TLS)
        client.connect(settings.HIVEMQ_BROKER_ADDRESS, int(settings.HIVEMQ_BROKER_PORT))
        return client

    def on_message(self, client, userdata, msg):
        self.stdout.write(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        payload = json.loads(msg.payload.decode())
        payload['timestamp'] = datetime.fromtimestamp(payload['timestamp'])
        serializer = DeviceReadingsSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()

    def consume_device_readings(self):
        client = self.connect_mqtt()
        client.subscribe(settings.HIVEMQ_BROKER_TOPIC)
        client.on_message = self.on_message
        client.loop_forever()

    """ Django command to run a consumer in the background"""
    def handle(self, *args, **kwargs):
        self.consume_device_readings()
