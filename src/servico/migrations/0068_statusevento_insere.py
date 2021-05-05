# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


_INS = True
_DEL = False

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


_ACAO = {
    _DEL: delete,
    _INS: insert,
}
_MOVES = {
    _DEL: [
        ['iniciado', 'cancelamento', 'cancelado'],  
    ],
    _INS: [
        ['iniciado', 'interrompe', 'aberto'],  
        ['terminado', 'reabertura', 'aberto'],  
    ],
}

def exec(apps, exec_do):
    status = apps.get_model("servico", "Status")
    evento = apps.get_model("servico", "Evento")
    status_evento = apps.get_model("servico", "StatusEvento")

    for do in _MOVES:
        acao = do if exec_do else not do
        for move in _MOVES[do]:
            _ACAO[acao](status_evento, status, evento, *move)
        

def do(apps, schema_editor):
    exec(apps, _INS)


def undo(apps, schema_editor):
    exec(apps, _DEL)
    

class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0067_evento_insere'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
