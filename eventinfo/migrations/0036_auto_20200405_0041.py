# Generated by Django 3.0.2 on 2020-04-04 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventinfo', '0035_auto_20200404_0309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='guest_image',
            field=models.ImageField(default='main_image/users/avatar/00.png', upload_to='main_image/profiles/avatar/', verbose_name='تصویر'),
        ),
    ]