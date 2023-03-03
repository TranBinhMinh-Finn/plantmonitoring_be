from plantmon.models import CustomUser, Device, DeviceReadings
from rest_framework import serializers
from django.contrib.auth.hashers import make_password


class UserDetailSerializer(serializers.ModelSerializer):
    devices = serializers.PrimaryKeyRelatedField(many=True, queryset=Device.objects.all())

    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'email', 'devices']


class DeviceReadingsSerializer(serializers.ModelSerializer):
    device = serializers.ReadOnlyField(source='device.device_id')

    class Meta:
        model = DeviceReadings
        fields = ['device', 'temperature', 'humidity', 'brightness', 'timestamp']


class DeviceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Device
        fields = ['device_id', 'name', 'owner']


class UserAuthSerializer(serializers.ModelSerializer):
    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'password', 'email']
