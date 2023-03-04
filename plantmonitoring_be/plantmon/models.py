from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid


class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)


class Device(models.Model):
    class WateringMode(models.TextChoices):
        MANUAL = 'MAN', _('Manual')
        TIMED = 'TIM', _('Timed')
        ADAPTIVE = 'ADT', _('Adaptive')
    device_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, related_name='devices', on_delete=models.CASCADE,)
    watering_mode = models.CharField(max_length=3,
                                     choices=WateringMode.choices,
                                     default=WateringMode.MANUAL)


class DeviceReadings(models.Model):
    device = models.ForeignKey(Device, related_name='readings',  on_delete=models.CASCADE,)
    temperature = models.FloatField()
    humidity = models.FloatField()
    brightness = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']
