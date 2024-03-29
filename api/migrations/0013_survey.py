# Generated by Django 4.0.2 on 2022-12-01 21:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_rename_survey_surveyresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_key', models.CharField(default=uuid.uuid4, editable=False, max_length=63, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('participants', models.ManyToManyField(to='api.StudyParticipant')),
            ],
        ),
    ]
