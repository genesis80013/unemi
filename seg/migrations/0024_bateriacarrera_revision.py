# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-26 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0023_auto_20201022_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='bateriacarrera',
            name='revision',
            field=models.NullBooleanField(default=False, verbose_name='revision'),
        ),
    ]
