# Generated by Django 4.0.2 on 2022-04-25 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_survey'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_name', models.CharField(max_length=200)),
                ('tab_name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('timestamp', models.DateTimeField()),
                ('token', models.CharField(blank=True, max_length=200, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='survey',
            name='token',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]
