# Generated by Django 3.0.2 on 2020-03-02 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0002_auto_20200302_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_main_image',
            field=models.ImageField(blank=True, null=True, upload_to='main_image/', verbose_name='تصویر'),
        ),
    ]
