# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-21 19:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0030_status_loaddata'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TipoEvento',
            new_name='Evento',
        ),
    ]
