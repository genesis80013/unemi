# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-07 19:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0007_auto_20200805_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignacioncoordinadordocente',
            name='tamaniobateria',
            field=models.IntegerField(blank=True, null=True, verbose_name='Tamanio bateria'),
        ),
    ]