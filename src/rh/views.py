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


def aniversariantes(request):
    aniversariantes = [
        ['03/08', 'VERONICA CORDEIRO BEZERRA DOS SANTOS'],
        ['03/08', 'SIMONE DA SILVA SARAIVA'],
        ['06/08', 'CARLOS ALBERTO DE SOUSA CARVALHO JUNIOR'],
        ['06/08', 'JONAS MARTINS'],
        ['07/08', 'PEDRO JOSÉ NASCIMENTO DE OLIVEIRA'],
        ['07/08', 'JORGE MARCELO DE ALMEIDA GARGAGLIONE'],
        ['09/08', 'SONIA MARIA DO NASCIMENTO REIS'],
        ['09/08', 'LUZIA VIEIRA DA SILVA ARAUJO'],
        ['10/08', 'MARIA APARECIDA TIBURCIO'],
        ['11/08', 'TAMIRES FERNANDA DOS SANTOS MARINS'],
        ['12/08', 'DOUGLAS DOS SANTOS ALVES'],
        ['13/08', 'FABIANA ABREU DE JESUS'],
        ['14/08', 'ADRIANA MARIA DE SOUZA MONTEIRO'],
        ['15/08', 'ANDREZA SILVA DE BRITO'],
        ['15/08', 'CLAUDIA TEIXEIRA DA SILVA AVELINO'],
        ['17/08', 'LEILIANE MARIA DA SILVA'],
        ['17/08', 'REGINA MARIA SANDRA DOS SANTOS'],
        ['18/08', 'PATRICIA DE OLIVEIRA'],
        ['18/08', 'VALQUIRIA EVANGELISTA DA SILVA'],
        ['19/08', 'ERIKA CRISTINA ARIGONY ANTONIO'],
        ['20/08', 'FABIANA VASQUES GONÇALVES'],
        ['21/08', 'MARIA DA GLORIA MIRANDA DA CRUZ'],
        ['21/08', 'FABIOLA SEGUNDO DA MOTTA TEIXEIRA'],
        ['25/08', 'LORRAINE CRISTINE MARTINS DE ANDRADE'],
        ['26/08', 'SUELEN CLAUDINO VICENTE'],
        ['27/08', 'VERONICA CRISTINA DE CARVALHO SOARES'],
        ['27/08', 'MILENA THUANE DA SILVA CONCEIÇÃO'],
        ['28/08', 'MARIA LUCIA DE JESUS ALVES'],
        ['28/08', 'ROBERTA GOMES DA SILVA'],
        ['30/08', 'AFONSO HENRIQUES DE MAGALHÃES PEREIRA'],
    ]
    context = {}
    context = {
        'titulo': 'Aniversariantes do mês de Agosto de 2018',
        'aniversariantes': aniversariantes,
        }
    return render(request, 'rh/aniversariantes.html', context)
