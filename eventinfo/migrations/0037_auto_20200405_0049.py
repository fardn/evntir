# Generated by Django 3.0.2 on 2020-04-04 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0036_auto_20200405_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='guest_image',
            field=models.ImageField(default='profiles/avatar/00.png', upload_to='profiles/avatar/', verbose_name='تصویر'),
        ),
    ]
