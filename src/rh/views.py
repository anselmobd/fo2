from datetime import datetime

from django.shortcuts import render


def limpa_data_futura(lista, campo):
    for item in lista:
        if item[campo] > datetime.now().date():
            item[campo] = None


def index(request):
    dicas = [
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
    context = {'dicas': dicas}
    return render(request, 'rh/index.html', context)


def campanhas(request):
    context = {'titulo': 'Campanhas'}
    return render(request, 'rh/campanhas.html', context)


def datas(request):
    context = {'titulo': 'Datas comemorativas'}
    return render(request, 'rh/datas.html', context)
