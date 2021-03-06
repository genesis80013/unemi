# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-13 09:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0037_auto_20201111_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grupoexamenestudiante',
            options={'ordering': ['estudiante__inscripcion__persona__apellido1', 'estudiante__inscripcion__persona__apellido2', 'estudiante__inscripcion__persona__nombres'], 'verbose_name': 'GrupoExamenEstudiante', 'verbose_name_plural': 'GrupoExamenEstudiantes'},
        ),
        migrations.AddField(
            model_name='grupoexamen',
            name='activo',
            field=models.NullBooleanField(default=True, verbose_name='activo'),
        ),
    ]
