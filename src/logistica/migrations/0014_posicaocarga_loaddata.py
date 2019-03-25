# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def load_posicaocarga_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0014_posicaocarga_loaddata")


def delete_posicaocarga(apps, schema_editor):
    PosicaoCarga = apps.get_model("logistica", "PosicaoCarga")
    PosicaoCarga.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0013_posicaocarga'),
    ]

    operations = [
        migrations.RunPython(
            load_posicaocarga_from_fixture, delete_posicaocarga),
    ]
