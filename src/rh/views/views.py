import datetime
from pprint import pprint

from django.db import connections
from django.shortcuts import render

from utils.functions import strdmy2date

import rh.models


def limpa_data_futura(lista, campo):
    for item in lista:
        if item[campo] > datetime.datetime.now().date():
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


def fotos_2019_04_01_1o_cafe(request):
    context = {'titulo': '1º Café com RH de 2019'}
    return render(request, 'rh/fotos_2019_04_01_1o_cafe.html', context)


def fotos_2019_03_lorena(request):
    context = {'titulo': 'Funcionária Lorena homenageada'}
    return render(request, 'rh/fotos_2019_03_lorena.html', context)


def fotos_2019_05_24_bianca(request):
    context = {'titulo': 'Funcionária Bianca Vasques homenageada'}
    return render(request, 'rh/fotos_2019_05_24_bianca.html', context)


def fotos_2019_06_14_adriana_leo(request):
    context = {'titulo': 'Funcionários Adriana Martins e Leonardo Andrade '
                         'homenageados'}
    return render(request, 'rh/fotos_2019_06_14_adriana_leo.html', context)


def fotos_2019_07_12_brigadistas_2019(request):
    context = {'titulo': 'Aos brigadistas 2019'}
    return render(
        request, 'rh/fotos_2019_07_12_brigadistas_2019.html', context)


def media_2019_04_09_dicas(request):
    context = {'titulo': 'Dicas de comportamento no ambiente de trabalho'}
    return render(request, 'rh/media_2019_04_09_dicas.html', context)


def media_2019_07_16_sobre_amizade(request):
    context = {'titulo': 'Poesia com Rapadura- Falando sobre amizade'}
    return render(request, 'rh/media_2019_07_16_sobre_amizade.html', context)


def media_2019_08_01_25_anos(request):
    context = {'titulo': '25 anos de empresa de Rosângela e Denilson'}
    return render(request, 'rh/media_2019_08_01_25_anos.html', context)


def principal(request):
    return render(request, 'rh/principal.html')


def index(request):
    pensamentos = []
    dicas = [
      {
        'data': strdmy2date('02/12/2020'),
        'chamada': 'Utilize a máscara corretamente',
        'link': '/media/rh/dicas/2020/12/02-mascara.png',
      },
      {
        'data': strdmy2date('10/02/2020'),
        'chamada': 'Zap com moderação',
        'link': '/media/rh/dicas/2020/02/10-whatsapp.jpg',
      },
      {
        'data': strdmy2date('07/11/2018'),
        'chamada': 'Inspire Pessoas',
        'link': '/media/rh/dicas/2018-11-07_inspire_pessoas.jpg',
      },
      {
        'data': strdmy2date('22/10/2018'),
        'chamada': 'Se colocar no lugar do outro',
        'link': '/media/rh/dicas/2018-10-22_no_lugar_do_outro.jpg',
      },
      {
        'data': strdmy2date('09/10/2018'),
        'chamada': 'Sem coroa',
        'link': '/media/rh/dicas/2018-10-09_lider.png',
      },
      {
        'data': strdmy2date('02/10/2018'),
        'chamada': 'Alta performance com suas equipes',
        'link': '/media/rh/dica_2018-10-02_alta_performance_equipe.jpg',
      },
      {
        'data': strdmy2date('18/09/2018'),
        'chamada': 'Pessoas de sucesso',
        'link': '/media/rh/dica_2018-09-18_pessoas-de-sucesso.png',
      },
      {
        'data': strdmy2date('05/09/2018'),
        'chamada': 'Concentre-se e desconecte-se!',
        'link': '/media/rh/2018-09-Desconecte.pdf',
      },
      {
        'data': strdmy2date('04/09/2018'),
        'chamada': 'Farmácia interna',
        'link': '/media/rh/Dica-da-Semana-2018-09-04-farmacia_interna.jpg',
      },
      {
        'data': strdmy2date('13/08/2018'),
        'chamada': 'Inspire pessoas',
        'link': '/media/rh/Dica-da-Semana-2018-08-13.jpg',
      },
      {
        'data': strdmy2date('06/08/2018'),
        'chamada': 'No lugar do outro',
        'link': '/media/rh/Dica-da-Semana-2018-08-06.jpg',
      },
      {
        'data': strdmy2date('30/07/2018'),
        'chamada': 'Desenvolvimento da equipe',
        'link': '/media/rh/dica_2018-07-30_desenvolvimento_da_equipe.png',
      },
      {
        'data': strdmy2date('25/06/2018'),
        'chamada': 'Mudança',
        'link': '/media/rh/Dica-da-Semana-2018-06-25.jpg',
      },
      {
        'data': strdmy2date('11/06/2018'),
        'chamada': 'Pequenas Gentilezas',
        'link': '/media/rh/Dica-da-Semana-2018-06-11.jpg',
      },
      {
        'data': strdmy2date('14/05/2018'),
        'chamada': 'Arrisca',
        'link': '/media/rh/DUOMO-2018-05-14-Pensamento.jpg',
      },
      {
        'data': strdmy2date('04/05/2018'),
        'chamada': 'Custa R$ 0,00',
        'link': '/media/rh/DUOMO-2018-05-04-Dica.jpg',
      },
      {
        'data': strdmy2date('23/02/2018'),
        'chamada': '3 dicas essenciais',
        'link': '/media/rh/DUOMO-23-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('22/02/2018'),
        'chamada': 'Haja com confiança e seja confiável',
        'link': '/media/rh/DUOMO-22-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('21/02/2018'),
        'chamada': 'Seja proativo',
        'link': '/media/rh/DUOMO-21-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('20/02/2018'),
        'chamada': 'Melhore a comunicação',
        'link': '/media/rh/DUOMO-20-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('19/02/2018'),
        'chamada': 'Como administrar conflitos',
        'link': '/media/rh/DUOMO-19-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('07/02/2018'),
        'chamada': 'Movidos pela motivação',
        'link': '/media/rh/DUOMO-07-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('06/02/2018'),
        'chamada': 'Evolução das alas',
        'link': '/media/rh/DUOMO-06-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('05/02/2018'),
        'chamada': 'O quesito da harmonia',
        'link': '/media/rh/DUOMO-05-02-Dica-da-Semana.jpg',
      },
      {
        'data': strdmy2date('02/02/2018'),
        'chamada': 'A arte de se reinventar',
        'link': '/media/rh/DUOMO-02-02-Dica-da-Semana.jpg',
      },
    ]
    limpa_data_futura(dicas, 'data')
    links = [
        {'chamada': 'Escola do Trabalhador',
         'descricao':
            'O Ministério do Trabalho tem cursos '
            'gratuitos em várias áreas,<br />basta se '
            'inscrever e fazer os cursos on line.',
         'link': 'http://escolatrabalho.gov.br/'},
    ]
    rota2020 = [
        {'data': strdmy2date('12/03/2020'),
         'chamada': 'Reuniões Produtivas',
         'link': '/rh/campanhas/2020-03-12'},
        {'data': strdmy2date('11/02/2020'),
         'chamada': 'Premiação 2020',
         'link': '/rh/campanhas/2020-02-11'},
        {'data': strdmy2date('27/01/2020'),
         'chamada': 'Qualidade e Produtividade',
         'link': '/media/rh/campanhas/2020/'
                 '01/27/qualidade_e_produtividade.pdf'},
        {'data': strdmy2date('22/01/2020'),
         'chamada': 'Transformar juntos',
         'link': '/rh/campanhas/2020-01-22'},
        {'data': strdmy2date('13/01/2020'),
         'chamada': 'Inovar é Transformar',
         'link': '/media/rh/campanhas/2020/01/13/duomo-rota-sucesso-001.jpg'},
        {'data': strdmy2date('08/01/2020'),
         'chamada': 'Em 2020, vamos embarcar numa viagem rumo ao SUCESSO!',
         'descricao':
            'Nessa viagem, iremos carimbar o nosso passaporte com os<br />'
            'carimbos da Inovação, Produtividade, Desenvolvimento,<br />'
            'Experiência, Transformação, União e Excelência.<br />'
            'Vai ser demais!<br />'
            'Juntos vamos fazer essa incrível Rota do Sucesso!',
         'link': '/media/rh/campanhas/2020/01/08/duomo-rota-sucesso-w650.jpg'},
    ]
    context = {
        'dicas': dicas,
        'links': links,
        'pensamentos': pensamentos,
        'rota2020': rota2020,
        }
    return render(request, 'rh/index.html', context)


def comunicados(request, id):
    if id == '2020-07-29':
        context = {'titulo': 'Tecelagem - Pagamentos'}
        return render(
            request, 'rh/comunicados/2020-07-29-pagamentos.html', context)


def eventos(request, id):
    if id == '2020-03-17':
        context = {'titulo': 'Fotos - SIPAT 2020'}
        return render(request, 'rh/eventos/2020-03-17-sipat.html', context)
    elif id == '2020-06-24':
        context = {'titulo': 'Festa junina 2020!'}
        return render(request, 'rh/eventos/2020-06-24-junina.html', context)
    elif id == '2020-07-20':
        context = {'titulo': 'Dia do amigo 2020!'}
        return render(
            request, 'rh/eventos/2020-07-20-dia-do-amigo.html', context)


def datas(request, data):
    if data == 'lista':
        context = {'titulo': 'Datas comemorativas'}
        return render(request, 'rh/datas.html', context)
    elif data == '2019-12-natal':
        context = {'titulo': '2019 - Feliz Natal!'}
        return render(request, 'rh/datas/2019-12-natal.html', context)
    elif data == '2019-12-retrospectiva':
        context = {'titulo': 'Retrospectiva 2019!'}
        return render(request, 'rh/datas/2019-12-retrospectiva.html', context)
    elif data == '2020-02-carnaval':
        context = {'titulo': 'Carnaval 2020!'}
        return render(request, 'rh/datas/2020-02-carnaval.html', context)
    elif data == '2020-03-04-mulher':
        context = {'titulo': 'Dia da mulher - 2020'}
        return render(request, 'rh/datas/2020-03-04-mulher.html', context)
    elif data == '2020-04-29':
        context = {'titulo': 'Dia do Trabalhador - 2020'}
        return render(
            request, 'rh/datas/2020-04-29-dia_trabalhador.html', context)
    elif data == '2020-05-08':
        context = {'titulo': 'Dia das mães - 2020'}
        return render(
            request, 'rh/datas/2020-05-08-dia-das-maes.html', context)
    elif data == '2020-08-09':
        context = {'titulo': 'Dia dos Pais 2020!'}
        return render(
            request, 'rh/datas/2020-08-09-dia-dos-pais.html', context)
    elif data == '2021':
        context = {'titulo': 'Feliz 2021!'}
        return render(
            request, 'rh/datas/2021-virada.html', context)


def v2018_dia_rosa_fotos(request):
    context = {'titulo': 'Fotos - Dia Rosa 2018'}
    return render(request, 'rh/2018_dia_rosa_fotos.html', context)


def v2018_dia_rosa_videos(request):
    context = {'titulo': 'Vídeos - Dia Rosa 2018'}
    return render(request, 'rh/2018_dia_rosa_videos.html', context)


def divulga_atitudes_crise(request):
    context = {'titulo': 'Atitudes que um líder deve ter em momentos de crise'}
    return render(request, 'rh/divulga_atitudes_crise.html', context)
