# Generated by Django 3.0.2 on 2020-04-21 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0051_auto_20200419_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tickets',
            name='is_unlimited',
        ),
        migrations.AlterField(
            model_name='event',
            name='is_unlimited',
            field=models.BooleanField(default=False, verbose_name='تعداد نامحدود و رایگان'),
        ),
    ]
