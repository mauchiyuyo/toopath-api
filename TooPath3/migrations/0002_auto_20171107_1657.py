# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-07 15:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TooPath3', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='ip_address',
            field=models.GenericIPAddressField(null=True),
        ),
    ]
