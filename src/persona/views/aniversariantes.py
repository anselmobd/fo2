import datetime

from django.shortcuts import render

from fo2.connections import db_cursor

from utils.functions import inc_month

import persona.queries as queries


def aniversariantes(request, *args, **kwargs):
    if 'mes' in kwargs:
        intmes = int(kwargs['mes'])
        intano = int(kwargs['ano'])
    else:
        now = datetime.datetime.now()
        intano = now.year
        intmes = now.month
    mes = '{:02}'.format(intmes)
    datames = datetime.datetime(intano, intmes, 1)

    aniversariantes = [
        ['27/08', 'Arnaldo Silva da Costa', 'Logística'],
        ['03/10', 'Anselmo Blanco Dominguez', 'TI'],
        ['17/02', 'Antonio Ricardo Maganhães Moraes', 'Diretor'],
    ]

    anteriormes = inc_month(datames, -1)
    intmesant = anteriormes.month

    posteriosmes = inc_month(datames, 1)
    intmespos = posteriosmes.month

    pcursor = db_cursor('persona', request)
    data = queries.aniversariantes(pcursor, intmes)

    aniver_db = []
    for row in data:
        aniver_db.append(
           ['{:02d}/{:02d}'.format(int(row['dia']), int(row['mes'])),
            row['nome'], row['setor']],
        )

    insere_pessoa = [
        pessoa for pessoa in aniversariantes if pessoa[0][-2:] == mes]

    for pessoa in insere_pessoa:
        for i, row in enumerate(aniver_db):
            if row[0] >= pessoa[0] and row[1] > pessoa[1]:
                aniver_db.insert(i, pessoa)
                break

    context = {
        'datames': datames,
        'intmesant': intmesant,
        'intanoant': anteriormes.year,
        'intmespos': intmespos,
        'intanopos': posteriosmes.year,
        'aniversariantes': aniver_db,
        }
    return render(request, 'persona/aniversariantes.html', context)
