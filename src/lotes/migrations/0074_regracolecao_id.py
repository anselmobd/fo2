from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations, models

from lotes.models import RegraColecao as RegraColecaoModel


def do(apps, schema_editor):
    for id, code in enumerate(RegraColecaoModel.objects.all()):
       code.id = id + 1
       code.save()


def undo(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0073_regracolecao_id'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
