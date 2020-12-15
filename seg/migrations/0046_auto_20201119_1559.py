# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-19 15:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0045_impugnacionexamen_impugnacióndetalle'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpugnacionDetalle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('area', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ReactivoArea', verbose_name='area')),
                ('asignatura', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.AsignaturaMalla', verbose_name='asignatura')),
                ('impugnacion', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ImpugnacionExamen', verbose_name='impugnacion')),
                ('reactivo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ReactivoDocente', verbose_name='reactivo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='impugnacióndetalle',
            name='area',
        ),
        migrations.RemoveField(
            model_name='impugnacióndetalle',
            name='asignatura',
        ),
        migrations.RemoveField(
            model_name='impugnacióndetalle',
            name='reactivo',
        ),
        migrations.DeleteModel(
            name='ImpugnaciónDetalle',
        ),
    ]
