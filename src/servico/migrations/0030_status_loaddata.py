# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_status_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "0030_status_loaddata")


def delete_status(apps, schema_editor):
    status = apps.get_model("servico", "Status")
    status.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0029_status_table_name'),
    ]

    operations = [
        migrations.RunPython(
            load_status_from_fixture, delete_status),
    ]
