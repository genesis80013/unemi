# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-19 15:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0044_auto_20201118_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpugnacionExamen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('emparejamiento', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha', models.DateTimeField(blank=True, null=True, verbose_name='fecha')),
                ('examen', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.CronogramaExamen', verbose_name='examen')),
                ('grupoexamenestudiante', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.GrupoExamenEstudiante', verbose_name='grupoexamenestudiante')),
                ('periodo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.Periodo', verbose_name='periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImpugnaciónDetalle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('area', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ReactivoArea', verbose_name='area')),
                ('asignatura', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.AsignaturaMalla', verbose_name='asignatura')),
                ('reactivo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ReactivoDocente', verbose_name='reactivo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
