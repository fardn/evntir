# Generated by Django 3.0.2 on 2020-04-10 10:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventinfo', '0043_remove_event_bookmarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='bookmarks',
            field=models.ManyToManyField(blank=True, related_name='bookmarks', through='eventinfo.EventBookmarks', to=settings.AUTH_USER_MODEL),
        ),
    ]
