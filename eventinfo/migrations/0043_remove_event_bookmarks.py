# Generated by Django 3.0.2 on 2020-04-10 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0042_auto_20200410_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='bookmarks',
        ),
    ]
