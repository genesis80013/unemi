# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-15 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg', '0041_auto_20201114_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='formatoreactivo',
            name='valiopciones',
            field=models.NullBooleanField(default=True, verbose_name='Vali opciones'),
        ),
    ]