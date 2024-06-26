# Generated by Django 4.2.5 on 2024-03-22 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp_viewer', '0004_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='disabilities',
        ),
        migrations.AddField(
            model_name='opportunity',
            name='disability_inclusive',
            field=models.ManyToManyField(to='webapp_viewer.disability'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='disabilities',
            field=models.ManyToManyField(blank=True, to='webapp_viewer.disability'),
        ),
    ]
