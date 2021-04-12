# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_tipoevento_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0012_tipoevento_loaddata")


def delete_tipoevento(apps, schema_editor):
    tipoevento = apps.get_model("servico", "TipoEvento")
    tipoevento.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0011_tipoevento_ordem'),
    ]

    operations = [
        migrations.RunPython(
            load_tipoevento_from_fixture, delete_tipoevento),
    ]
