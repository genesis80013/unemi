# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-18 18:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0017_auto_20200907_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignaciondocentereactivo',
            name='asignacion',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.AsignacionGrupoCoordinador', verbose_name='asignacion'),
        ),
    ]
