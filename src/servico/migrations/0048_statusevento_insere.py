# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


def insert(status_evento, status, evento, pre, acao, pos):
    status_pre=status.objects.get(codigo=pre) if pre else None
    status_pos=status.objects.get(codigo=pos) if pos else None
    status_evento(
        status_pre=status_pre,
        evento=evento.objects.get(codigo=acao),
        status_pos=status_pos,
    ).save()

def delete(status_evento, status, evento, pre, acao, pos):
    status_pre=status.objects.get(codigo=pre) if pre else None
    status_pos=status.objects.get(codigo=pos) if pos else None
    status_evento.objects.get(
        status_pre=status_pre,
        evento=evento.objects.get(codigo=acao),
        status_pos=status_pos,
    ).delete()


def init(apps, schema_editor):
    status = apps.get_model("servico", "Status")
    evento = apps.get_model("servico", "Evento")
    status_evento = apps.get_model("servico", "StatusEvento")
    return status, evento, status_evento


def do(apps, schema_editor):
    status, evento, status_evento = init(apps, schema_editor)
    insert(status_evento, status, evento, 'cancelado', 'reabertura', 'aberto')
    

def undo(apps, schema_editor):
    status, evento, status_evento = init(apps, schema_editor)
    delete(status_evento, status, evento, 'cancelado', 'reabertura', 'aberto')


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0047_remove_documento_status'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
