# Generated by Django 3.0.2 on 2020-03-22 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0016_auto_20200321_2029'),
    ]

    operations = [
        migrations.CreateModel(
            name='Time_Slots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_start_date', models.DateTimeField(verbose_name='تاریخ و ساعت شروع')),
                ('event_end_date', models.DateTimeField(verbose_name='تاریخ و ساعت پایان')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventinfo.Event', verbose_name='شناسه رویداد')),
            ],
            options={
                'verbose_name': 'سانس',
                'verbose_name_plural': 'سانس',
            },
        ),
    ]
