# Generated by Django 4.0.8 on 2025-04-15 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phishingtool', '0005_remove_phishingemailtemplate_redirect_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailactivity',
            name='attachment_downloaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailactivity',
            name='attachment_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emailactivity',
            name='submission_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emailactivity',
            name='submitted_data',
            field=models.BooleanField(default=False),
        ),
    ]
