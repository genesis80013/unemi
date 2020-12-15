# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-03 17:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0004_auto_20200802_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtributoReactivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('nombre', models.CharField(default='', max_length=255, verbose_name='Nombre')),
                ('detalle', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Detalle')),
                ('estuvisible', models.NullBooleanField(default=True, verbose_name='Visible estudiante')),
                ('profvisible', models.NullBooleanField(default=True, verbose_name='Visible profesor')),
                ('estado', models.NullBooleanField(default=True, verbose_name='Estado')),
                ('formatoreactivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seg.FormatoReactivo', verbose_name='Plantilla Reactivo')),
            ],
            options={
                'verbose_name': 'Atributo',
                'ordering': ['formatoreactivo', 'id'],
                'verbose_name_plural': 'Atributos',
            },
        ),
    ]
