# Generated by Django 5.1.7 on 2025-06-21 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EntryData', '0006_bus_data_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus_data',
            name='IN_Time',
            field=models.TimeField(default='00:00'),
        ),
    ]
