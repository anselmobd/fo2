# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_popgrupoassunto_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0042_popgrupoassunto_loaddata")


def delete_popgrupoassunto(apps, schema_editor):
    PopGrupoAssunto = apps.get_model("geral", "PopGrupoAssunto ")
    PopGrupoAssunto.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0041_popgrupoassunto_ordem'),
    ]

    operations = [
        migrations.RunPython(
            load_popgrupoassunto_from_fixture, delete_popgrupoassunto),
    ]
