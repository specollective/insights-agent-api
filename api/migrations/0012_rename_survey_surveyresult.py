# Generated by Django 4.0.2 on 2022-12-01 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_remove_survey_age_remove_survey_education_level_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Survey',
            new_name='SurveyResult',
        ),
    ]
