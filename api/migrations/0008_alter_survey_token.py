# Generated by Django 4.0.2 on 2022-05-02 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_studyparticipant_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='token',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]