# Generated by Django 4.0.2 on 2022-06-05 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_survey_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataentry',
            name='token',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
