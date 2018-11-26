# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-23 18:57
from __future__ import unicode_literals

from django.db import migrations, models


def load_tipo_imagem_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0002_fo2_tipo_imagem_loaddata")


def delete_tipo_imagem(apps, schema_editor):
    TipoImagem = apps.get_model("base", "TipoImagem")
    TipoImagem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            load_tipo_imagem_from_fixture, delete_tipo_imagem),
    ]
