# Generated by Django 4.1.6 on 2023-02-18 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plantmon', '0002_alter_device_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
