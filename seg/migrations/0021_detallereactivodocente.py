# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-04 12:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0020_auto_20200926_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetalleReactivoDocente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('texto', models.TextField(blank=True, null=True, verbose_name='texto')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='detallereactivodocente/%Y/%m/%d', verbose_name='archivo')),
                ('valorporcentual', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='valorporcentual')),
                ('activo', models.NullBooleanField(verbose_name='activo')),
                ('atributo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.AtributoReactivo', verbose_name='atributo')),
                ('reactivo', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='seg.ReactivoDocente', verbose_name='reactivo')),
            ],
            options={
                'verbose_name': 'DetalleReactivoDocente',
                'verbose_name_plural': 'DetalleReactivoDocentes',
            },
        ),
    ]