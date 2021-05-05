# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


_INS = True
_DEL = False

def zap(funcao_exercida, usuario_funcao):
    usuario_funcao.objects.all().delete()
    funcao_exercida.objects.all().delete()

def insert(funcao_exercida, usuario_funcao, nome, slug, nivel_operacional, independente):
    funcao_exercida(
        nome=nome,
        slug=slug,
        nivel_operacional=nivel_operacional,
        independente=independente,
    ).save()

def delete(funcao_exercida, usuario_funcao, nome, slug, nivel_operacional, independente):
    funcao_exercida.objects.get(
        nome=nome,
        slug=slug,
        nivel_operacional=nivel_operacional,
        independente=independente,
    ).delete()


_ACAO = {
    _DEL: delete,
    _INS: insert,
}
_MOVES = {
    _DEL: [
    ],
    _INS: [
        ['Auxiliar', 'auxiliar', 1, False],
        ['Executor', 'executor', 2, False],
        ['Chefe de equipe', 'chefe-de-equipe', 3, False],
        ['Supervisor de equipe', 'supervisor-de-equipe', 4, False],
        ['Supervisor geral', 'supervisor-geral', 5, True],
    ],
}

def exec(apps, exec_do, do_zap=False):
    funcao_exercida = apps.get_model("servico", "FuncaoExercida")
    usuario_funcao = apps.get_model("servico", "UsuarioFuncao")
    if do_zap:
        zap(funcao_exercida, usuario_funcao)
    for do in _MOVES:
        acao = do if exec_do else not do
        for move in _MOVES[do]:
            _ACAO[acao](funcao_exercida, usuario_funcao, *move)
        

def do(apps, schema_editor):
    exec(apps, _INS, do_zap=True)


def undo(apps, schema_editor):
    exec(apps, _DEL, do_zap=False)
    

class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0065_funcaoexercida_parte_to_independente'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
