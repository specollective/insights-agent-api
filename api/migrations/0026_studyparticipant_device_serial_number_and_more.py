# Generated by Django 4.0.2 on 2023-02-01 01:32

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_dataentry_idle_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyparticipant',
            name='device_serial_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='studyparticipant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]
