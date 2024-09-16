# Generated by Django 4.2.5 on 2024-03-08 17:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('webapp_viewer', '0002_organization_awards_organization_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='images',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='opportunity_images/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opportunity',
            name='location',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]