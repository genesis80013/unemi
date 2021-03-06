# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-22 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0022_auto_20201019_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bateria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('cronograma', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.CronogramaPlanificacionExamen', verbose_name='cronograma')),
                ('periodo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.Periodo', verbose_name='periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BateriaCarrera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('bateria', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.Bateria', verbose_name='bateria')),
                ('carrera', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.GrupoCarreraExamen', verbose_name='carrera')),
                ('malla', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.GrupoCarreraMallaExamen', verbose_name='malla')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bateriaexamencomplexivo',
            name='carrera',
        ),
        migrations.AddField(
            model_name='bateriaexamencomplexivo',
            name='bateriacarrera',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.BateriaCarrera', verbose_name='bateriacarrera'),
        ),
    ]
