# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-23 21:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0042_servicoevento_numero_to_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicoevento',
            name='documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='servico.Documento'),
        ),
    ]
