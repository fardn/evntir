# Generated by Django 3.0.2 on 2020-03-22 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0018_auto_20200322_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_type', models.IntegerField(choices=[(0, 'رایگان'), (1, 'پولی'), (2, 'حمایتی')], verbose_name='جنسیت')),
                ('ticket_title', models.CharField(max_length=50, verbose_name='عنوان')),
                ('ticket_description', models.TextField(blank=True, null=True, verbose_name='توضیحات بلیت')),
                ('ticket_count', models.IntegerField(verbose_name='تعداد بلیت')),
                ('ticket_price', models.IntegerField(verbose_name='قیمت بلیت')),
                ('ticket_order_start_date', models.DateTimeField(blank=True, null=True, verbose_name='ساعت شروع فروش بلیت')),
                ('ticket_order_end_date', models.DateTimeField(blank=True, null=True, verbose_name='ساعت پایان فروش بلیت')),
                ('ticket_sold', models.IntegerField(default=0, verbose_name='بلیت\u200cهای فروخته شده')),
                ('ticket_is_passed', models.BooleanField(default=False, verbose_name='رویداد گذشته')),
                ('ticket_is_canceled', models.BooleanField(default=False, verbose_name='بلیت لفو شده')),
                ('ticket_time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventinfo.Time_Slots', verbose_name='سانس')),
            ],
            options={
                'verbose_name': 'بلیت',
                'verbose_name_plural': 'بلیت',
            },
        ),
    ]
