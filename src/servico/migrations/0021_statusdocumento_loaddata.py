# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_statusdocumento_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0021_statusdocumento_loaddata")


def delete_statusdocumento(apps, schema_editor):
    statusdocumento = apps.get_model("servico", "StatusDocumento")
    statusdocumento.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0020_statusdocumento'),
    ]

    operations = [
        migrations.RunPython(
            load_statusdocumento_from_fixture, delete_statusdocumento),
    ]
