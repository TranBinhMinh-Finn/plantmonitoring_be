# Generated by Django 4.1.6 on 2023-03-04 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plantmon', '0006_device_watering_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='time_interval',
            field=models.IntegerField(default=5),
        ),
    ]
