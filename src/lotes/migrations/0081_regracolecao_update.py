# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


_DO = True
_UNDO = False
_INS = 1
_DEL = 2
_UPD = 3

def insert(regra, colecao, referencia, lotes_caixa):
    regra(
        colecao=colecao,
        referencia=referencia,
        lotes_caixa=lotes_caixa,
    ).save()


def delete(regra, colecao, referencia, _):
    regra.objects_referencia.get(
        colecao=colecao,
        referencia=referencia,
    ).delete()


def update(regra, colecao, referencia, lotes_caixa):
    r = regra.objects_referencia.get(
        colecao=colecao,
        referencia=referencia,
    )
    r.lotes_caixa=lotes_caixa
    r.save()


def unupdate(regra, colecao, referencia, _):
    update(regra, colecao, referencia, 0)


_ACAO = {
    _DO: {
        _INS: insert,
        _DEL: delete,
        _UPD: update,
    },
    _UNDO: {
        _INS: delete,
        _DEL: insert,
        _UPD: unupdate,
    },
}
_MOVES = {
    _DEL: [
    ],
    _INS: [
        [18, 'F', 3],
    ],
    _UPD: [
        [1, '', 4],  
        [2, '', 4],  
        [3, '', 4],  
        [4, '', 3],  
        [5, '', 2],  
        [6, '', 3],  
        [7, '', 3],  
        [8, '', 5],  
        [9, '', 3],  
        [10, '', 3],  
        [11, '', 3],  
        [12, '', 3],  
        [13, '', 4],  
        [14, '', 4],  
        [15, '', 4],  
        [16, '', 3],  
        [17, '', 3],  
        [18, '', 4],  
        [19, '', 3],  
        [45, '', 3],  
        [50, '', 3],  
        [55, '', 3],  
        [60, '', 3],  
        [65, '', 3],  
        [888, '', 0],  
    ],
}


def exec(apps, do):
    regra = apps.get_model("lotes", "RegraColecao")

    for move in _MOVES:
        for values in _MOVES[move]:
            _ACAO[do][move](regra, *values)
        

def do(apps, schema_editor):
    exec(apps, _DO)


def undo(apps, schema_editor):
    exec(apps, _UNDO)
    

class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0080_regracolecao_referencia'),
    ]

    operations = [
        migrations.RunPython(
            do, undo),
    ]
