# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-14 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0040_auto_20201113_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalleestudianteexamen',
            name='emparejamiento',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
