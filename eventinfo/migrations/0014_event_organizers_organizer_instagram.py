# Generated by Django 3.0.2 on 2020-03-19 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0013_auto_20200320_0152'),
    ]

    operations = [
        migrations.AddField(
            model_name='event_organizers',
            name='organizer_instagram',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='اینستاگرام'),
        ),
    ]