# Generated by Django 3.0.2 on 2020-03-22 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0017_time_slots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_end_date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_start_date',
        ),
    ]