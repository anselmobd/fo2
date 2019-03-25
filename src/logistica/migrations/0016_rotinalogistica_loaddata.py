# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def load_rotinalogistica_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0016_rotinalogistica_loaddata")


def delete_rotinalogistica(apps, schema_editor):
    RotinaLogistica = apps.get_model("logistica", "RotinaLogistica")
    RotinaLogistica.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0015_rotinalogistica'),
    ]

    operations = [
        migrations.RunPython(
            load_rotinalogistica_from_fixture, delete_rotinalogistica),
    ]
