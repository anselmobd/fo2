# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


def insert(evento, nome, codigo, ordem, edita_nivel, edita_equipe, edita_descricao):
    evento(
        nome=nome,
        codigo=codigo,
        ordem=ordem,
        edita_nivel=edita_nivel,
        edita_equipe=edita_equipe,
        edita_descricao=edita_descricao,
    ).save()

def delete(evento, nome, codigo, ordem, edita_nivel, edita_equipe, edita_descricao):
    evento.objects.get(
        nome=nome,
        codigo=codigo,
        ordem=ordem,
        edita_nivel=edita_nivel,
        edita_equipe=edita_equipe,
        edita_descricao=edita_descricao,
    ).delete()


def init(apps, schema_editor):
    return apps.get_model("servico", "Evento")


def do(apps, schema_editor):
    evento = init(apps, schema_editor)
    insert(evento, 'Reinício', 'reinicio', 65, True, True, True)
    

def undo(apps, schema_editor):
    evento = init(apps, schema_editor)
    delete(evento, 'Reinício', 'reinicio', 65, True, True, True)


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0054_usuariofuncao_table_name'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
