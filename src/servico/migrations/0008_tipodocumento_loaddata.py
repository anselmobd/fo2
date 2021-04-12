# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_tipodocumento_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0008_tipodocumento_loaddata")


def delete_tipodocumento(apps, schema_editor):
    TipoDocumento = apps.get_model("servico", "TipoDocumento")
    TipoDocumento.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0007_tipodocumento_nome'),
    ]

    operations = [
        migrations.RunPython(
            load_tipodocumento_from_fixture, delete_tipodocumento),
    ]
