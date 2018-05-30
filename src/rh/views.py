from datetime import datetime

from django.shortcuts import render


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
    context = {
        'dicas': dicas,
        'pensamentos': pensamentos,
        }
    return render(request, 'rh/index.html', context)


def campanhas(request):
    context = {'titulo': 'Campanhas'}
    return render(request, 'rh/campanhas.html', context)


def datas(request):
    context = {'titulo': 'Datas comemorativas'}
    return render(request, 'rh/datas.html', context)
