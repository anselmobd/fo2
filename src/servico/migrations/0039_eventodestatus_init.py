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

def init(apps, schema_editor):
    status = apps.get_model("servico", "Status")
    evento = apps.get_model("servico", "Evento")
    status_evento = apps.get_model("servico", "StatusEvento")

    insert(status_evento, status, evento, None, 'requisicao', 'aberto')

    insert(status_evento, status, evento, 'aberto', 'cancelamento', 'cancelado')
    insert(status_evento, status, evento, 'iniciado', 'cancelamento', 'cancelado')

    insert(status_evento, status, evento, 'aberto', 'comentario', None)
    insert(status_evento, status, evento, 'iniciado', 'comentario', None)
    insert(status_evento, status, evento, 'terminado', 'comentario', None)

    insert(status_evento, status, evento, 'aberto', 'inicio', 'iniciado')
    
    insert(status_evento, status, evento, 'iniciado', 'alteracao', None)
    
    insert(status_evento, status, evento, 'iniciado', 'termino', 'terminado')

    insert(status_evento, status, evento, 'terminado', 'reabertura', 'iniciado')
    insert(status_evento, status, evento, 'fechado', 'reabertura', 'iniciado')
    
    insert(status_evento, status, evento, 'terminado', 'aceito', 'fechado')


def undo(apps, schema_editor):
    status_evento = apps.get_model("servico", "StatusEvento")
    status_evento.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0038_statusevento_table_name'),
    ]

    operations = [
        migrations.RunPython(
            init, undo),
    ]
