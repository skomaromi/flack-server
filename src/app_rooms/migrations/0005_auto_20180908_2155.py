# Generated by Django 2.1 on 2018-09-08 21:55

import builtins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_rooms', '0004_room_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(default="unnamed", max_length=255),
            preserve_default=False,
        ),
    ]
