# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def load_posicaocargaalteracao_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0018_posicaocargaalteracao_loaddata")


def delete_posicaocargaalteracao(apps, schema_editor):
    PosicaoCargaAlteracao = apps.get_model(
        "logistica", "PosicaoCargaAlteracao")
    PosicaoCargaAlteracao.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0017_posicaocargaalteracao'),
    ]

    operations = [
        migrations.RunPython(
            load_posicaocargaalteracao_from_fixture,
            delete_posicaocargaalteracao),
    ]
