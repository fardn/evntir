# Generated by Django 3.0.2 on 2020-03-29 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0025_auto_20200329_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='ticket_status',
            field=models.IntegerField(blank=True, choices=[(1, 'بلیت فروشی آغاز نشده.'), (2, 'بلیت فروشی آغاز شده.'), (3, 'بلیت\u200cها تمام شد.'), (4, 'بلیت فروشی بسته شد.'), (5, 'رویداد به پایان رسیده'), (6, 'بلیت لغو شده'), (7, 'بلیت حذف شده')], null=True),
        ),
    ]