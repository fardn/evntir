# Generated by Django 3.0.2 on 2020-03-18 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0005_event_guests'),
    ]

    operations = [
        migrations.AddField(
            model_name='event_guests',
            name='event_id',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.PROTECT, to='eventinfo.Event'),
            preserve_default=False,
        ),
    ]
