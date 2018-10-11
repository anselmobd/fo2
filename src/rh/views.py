from pprint import pprint
from datetime import datetime

from django.db import connections
from django.shortcuts import render

from utils.functions import inc_month

import rh.models


def limpa_data_futura(lista, campo):
    for item in lista:
        if item[campo] > datetime.now().date():
            item[campo] = None


def fotos(request):
    context = {'titulo': 'Fotos - SIPAT 2018'}
    return render(request, 'rh/fotos.html', context)


def videos(request):
    context = {'titulo': 'Vídeos - SIPAT 2018'}
    return render(request, 'rh/videos.html', context)


def fotos_homenagem20180614(request):
    context = {'titulo': 'Fotos - Homenagem a Thiago e Silvio'}
    return render(request, 'rh/fotos_homenagem20180614.html', context)


def fotos_brigadista2018(request):
    context = {'titulo': 'Fotos - Brigadistas 2018'}
    return render(request, 'rh/fotos_brigadista2018.html', context)


def videos_brigadista2018(request):
    context = {'titulo': 'Vídeos - Brigadistas 2018'}
    return render(request, 'rh/videos_brigadista2018.html', context)


def fotos_20180720_dia_do_amigo(request):
    context = {'titulo': 'Fotos - Dia do amigo 2018'}
    return render(request, 'rh/20180720_dia_do_amigo.html', context)


def index(request):
    pensamentos = [
      {
        'data': datetime.strptime('14/05/2018', '%d/%m/%Y').date(),
        'chamada': 'Arrisca',
        'link': '/media/rh/DUOMO-2018-05-14-Pensamento.jpg',
      },
      {
        'data': datetime.strptime('04/05/2018', '%d/%m/%Y').date(),
        'chamada': 'Custa R$ 0,00',
        'link': '/media/rh/DUOMO-2018-05-04-Dica.jpg',
      },
    ]
    dicas = [
      {
        'data': datetime.strptime('09/10/2018', '%d/%m/%Y').date(),
        'chamada': 'Sem coroa',
        'link': '/media/rh/dicas/2018-10-09_lider.png',
      },
      {
        'data': datetime.strptime('02/10/2018', '%d/%m/%Y').date(),
        'chamada': 'Alta performance com suas equipes',
        'link': '/media/rh/dica_2018-10-02_alta_performance_equipe.jpg',
      },
      {
        'data': datetime.strptime('18/09/2018', '%d/%m/%Y').date(),
        'chamada': 'Pessoas de sucesso',
        'link': '/media/rh/dica_2018-09-18_pessoas-de-sucesso.png',
      },
      {
        'data': datetime.strptime('04/09/2018', '%d/%m/%Y').date(),
        'chamada': 'Farmácia interna',
        'link': '/media/rh/Dica-da-Semana-2018-09-04-farmacia_interna.jpg',
      },
      {
        'data': datetime.strptime('13/08/2018', '%d/%m/%Y').date(),
        'chamada': 'Inspire pessoas',
        'link': '/media/rh/Dica-da-Semana-2018-08-13.jpg',
      },
      {
        'data': datetime.strptime('06/08/2018', '%d/%m/%Y').date(),
        'chamada': 'No lugar do outro',
        'link': '/media/rh/Dica-da-Semana-2018-08-06.jpg',
      },
      {
        'data': datetime.strptime('30/07/2018', '%d/%m/%Y').date(),
        'chamada': 'Desenvolvimento da equipe',
        'link': '/media/rh/dica_2018-07-30_desenvolvimento_da_equipe.png',
      },
      {
        'data': datetime.strptime('25/06/2018', '%d/%m/%Y').date(),
        'chamada': 'Mudança',
        'link': '/media/rh/Dica-da-Semana-2018-06-25.jpg',
      },
      {
        'data': datetime.strptime('11/06/2018', '%d/%m/%Y').date(),
        'chamada': 'Pequenas Gentilezas',
        'link': '/media/rh/Dica-da-Semana-2018-06-11.jpg',
      },
      {
        'data': datetime.strptime('23/02/2018', '%d/%m/%Y').date(),
        'chamada': '3 dicas essenciais',
        'link': '/media/rh/DUOMO-23-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('22/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Haja com confiança e seja confiável',
        'link': '/media/rh/DUOMO-22-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('21/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Seja proativo',
        'link': '/media/rh/DUOMO-21-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('20/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Melhore a comunicação',
        'link': '/media/rh/DUOMO-20-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('19/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Como administrar conflitos',
        'link': '/media/rh/DUOMO-19-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('07/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Movidos pela motivação',
        'link': '/media/rh/DUOMO-07-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('06/02/2018', '%d/%m/%Y').date(),
        'chamada': 'Evolução das alas',
        'link': '/media/rh/DUOMO-06-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('05/02/2018', '%d/%m/%Y').date(),
        'chamada': 'O quesito da harmonia',
        'link': '/media/rh/DUOMO-05-02-Dica-da-Semana.jpg',
      },
      {
        'data': datetime.strptime('02/02/2018', '%d/%m/%Y').date(),
        'chamada': 'A arte de se reinventar',
        'link': '/media/rh/DUOMO-02-02-Dica-da-Semana.jpg',
      },
    ]
    limpa_data_futura(dicas, 'data')
    links = [
        {'chamada': 'Escola do Trabalhador',
         'descricao': 'O Ministério do Trabalho tem cursos gratuitos em '
            'várias áreas, basta se inscrever e fazer os cursos on line.',
         'link': 'http://escolatrabalho.gov.br/'},
    ]
    context = {
        'dicas': dicas,
        'links': links,
        'pensamentos': pensamentos,
        }
    return render(request, 'rh/index.html', context)


def campanhas(request):
    context = {'titulo': 'Campanhas'}
    return render(request, 'rh/campanhas.html', context)


def datas(request):
    context = {'titulo': 'Datas comemorativas'}
    return render(request, 'rh/datas.html', context)


def mensagens(request):
    context = {'titulo': 'Mensagens'}
    return render(request, 'rh/mensagens.html', context)


def aniversariantes(request, *args, **kwargs):
    if 'mes' in kwargs:
        intmes = int(kwargs['mes'])
        intano = int(kwargs['ano'])
    else:
        now = datetime.now()
        intano = now.year
        intmes = now.month
    mes = '{:02}'.format(intmes)
    datames = datetime(intano, intmes, 1)

    aniversariantes = [
        ['27/08', 'Arnaldo Silva da Costa', 'Logística'],
        ['03/10', 'Anselmo Blanco Dominguez', 'TI'],
    ]

    anteriormes = inc_month(datames, -1)
    intmesant = anteriormes.month

    posteriosmes = inc_month(datames, 1)
    intmespos = posteriosmes.month

    pcursor = connections['persona'].cursor()
    data = rh.models.aniversariantes(pcursor, intmes)

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
    return render(request, 'rh/aniversariantes.html', context)
