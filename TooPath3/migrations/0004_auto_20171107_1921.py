# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-07 18:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TooPath3', '0003_tracks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tracks',
            new_name='Track',
        ),
        migrations.RenameModel(
            old_name='RouteLocation',
            new_name='TrackLocation',
        ),
        migrations.AlterModelTable(
            name='tracklocation',
            table='track_locations',
        ),
    ]
