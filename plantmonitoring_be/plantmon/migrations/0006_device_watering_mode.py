# Generated by Django 4.1.6 on 2023-03-03 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plantmon', '0005_alter_devicereadings_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='watering_mode',
            field=models.CharField(choices=[('MAN', 'Manual'), ('TIM', 'Timed'), ('ADT', 'Adaptive')], default='MAN', max_length=3),
        ),
    ]