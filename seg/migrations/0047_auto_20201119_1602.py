# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-19 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0046_auto_20201119_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='impugnacionexamen',
            name='emparejamiento',
        ),
        migrations.AddField(
            model_name='impugnacionexamen',
            name='descripcion',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
