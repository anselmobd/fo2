# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


def insert(
        evento, nome, codigo, ordem,
        edita_classificacao, edita_equipe, edita_descricao,
        nivel_op_minimo):
    evento(
        nome=nome,
        codigo=codigo,
        ordem=ordem,
        edita_classificacao=edita_classificacao,
        edita_equipe=edita_equipe,
        edita_descricao=edita_descricao,
        nivel_op_minimo=nivel_op_minimo,
    ).save()

def delete(
        evento, nome, codigo, ordem,
        edita_classificacao, edita_equipe, edita_descricao,
        nivel_op_minimo):
    evento.objects.get(
        nome=nome,
        codigo=codigo,
        ordem=ordem,
        edita_classificacao=edita_classificacao,
        edita_equipe=edita_equipe,
        edita_descricao=edita_descricao,
        nivel_op_minimo=nivel_op_minimo,
    ).delete()


def init(apps, schema_editor):
    return apps.get_model("servico", "Evento")


def do(apps, schema_editor):
    evento = init(apps, schema_editor)
    insert(evento, 'Interrompe', 'interrompe', 35, False, False, True, 1)
    

def undo(apps, schema_editor):
    evento = init(apps, schema_editor)
    delete(evento, 'Interrompe', 'interrompe', 35, False, False, True, 1)


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0066_funcaoexercida_redefine'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
