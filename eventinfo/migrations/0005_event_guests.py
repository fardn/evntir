# Generated by Django 3.0.2 on 2020-03-18 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0004_guest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event_Guests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_guests', models.ManyToManyField(to='eventinfo.Guest')),
            ],
        ),
    ]
