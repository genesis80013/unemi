# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-05 12:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0027_cronogramaexamen'),
    ]

    operations = [
        migrations.AddField(
            model_name='cronogramaexamen',
            name='activo',
            field=models.NullBooleanField(default=True, verbose_name='activo'),
        ),
    ]
