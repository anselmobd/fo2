# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_evento_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0036_evento_loaddata")


def delete_evento(apps, schema_editor):
    evento = apps.get_model("servico", "Evento")
    evento.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0035_evento_exclui_acoes'),
    ]

    operations = [
        migrations.RunPython(
            load_evento_from_fixture, delete_evento),
    ]
