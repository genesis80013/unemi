# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-02 18:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0003_formatoreactivo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formatoreactivo',
            old_name='cantidadopcionesmax',
            new_name='opcionesmax',
        ),
        migrations.RenameField(
            model_name='formatoreactivo',
            old_name='cantidadopcionesmin',
            new_name='opcionesmin',
        ),
        migrations.RenameField(
            model_name='formatoreactivo',
            old_name='cantidadrespuestasmax',
            new_name='respuestasmax',
        ),
        migrations.RenameField(
            model_name='formatoreactivo',
            old_name='cantidadrespuestasmin',
            new_name='respuestasmin',
        ),
    ]
