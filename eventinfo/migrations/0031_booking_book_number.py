# Generated by Django 3.0.2 on 2020-04-02 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0030_remove_booking_book_time_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='book_number',
            field=models.IntegerField(default=123, verbose_name='شماره سفارش'),
            preserve_default=False,
        ),
    ]