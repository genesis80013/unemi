# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-30 15:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0025_bateriaestudiante'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bateriaestudiante',
            options={'verbose_name': 'BateriaEstudiante', 'verbose_name_plural': 'BateriaEstudiantes'},
        ),
    ]