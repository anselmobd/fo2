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
        ['03/08', 'RECURSOS HUMANOS', 'SIMONE DA SILVA SARAIVA'],
        ['03/08', 'TECELAGEM', 'VERONICA CORDEIRO BEZERRA DOS SANTOS'],
        ['06/08', 'EXPEDIÇÃO', 'CARLOS ALBERTO DE SOUSA CARVALHO JUNIOR'],
        ['06/08', 'TECELAGEM', 'JONAS MARTINS'],
        ['07/08', 'VENDAS', 'JORGE MARCELO DE ALMEIDA GARGAGLIONE'],
        ['07/08', 'JOVEM APRENDIZ', 'PEDRO JOSÉ NASCIMENTO DE OLIVEIRA'],
        ['09/08', 'TECELAGEM', 'LUZIA VIEIRA DA SILVA ARAUJO'],
        ['09/08', 'PRODUCAO', 'SONIA MARIA DO NASCIMENTO REIS'],
        ['10/08', 'TECELAGEM', 'MARIA APARECIDA TIBURCIO'],
        ['11/08', 'EXPEDIÇÃO', 'TAMIRES FERNANDA DOS SANTOS MARINS'],
        ['12/08', 'FACILITES', 'DOUGLAS DOS SANTOS ALVES'],
        ['13/08', 'TECELAGEM', 'FABIANA ABREU DE JESUS'],
        ['14/08', 'PCP', 'ADRIANA MARIA DE SOUZA MONTEIRO'],
        ['15/08', 'EMBALAGEM/TECELAGEM', 'ANDREZA SILVA DE BRITO'],
        ['15/08', 'DESENVOLVIMENTO DE PRODUTOS',
         'CLAUDIA TEIXEIRA DA SILVA AVELINO'],
        ['17/08', 'EMBALAGEM/TECELAGEM', 'LEILIANE MARIA DA SILVA'],
        ['17/08', 'TECELAGEM', 'REGINA MARIA SANDRA DOS SANTOS'],
        ['18/08', 'EMBALAGEM/PRODUÇÃO', 'PATRICIA DE OLIVEIRA'],
        ['18/08', 'FINANCEIRO', 'VALQUIRIA EVANGELISTA DA SILVA'],
        ['19/08', 'TECELAGEM', 'ERIKA CRISTINA ARIGONY ANTONIO'],
        ['20/08', 'EXPEDIÇÃO', 'FABIANA VASQUES GONÇALVES'],
        ['21/08', 'QUALIDADE', 'FABIOLA SEGUNDO DA MOTTA TEIXEIRA'],
        ['21/08', 'PRODUCAO', 'MARIA DA GLORIA MIRANDA DA CRUZ'],
        ['25/08', 'RECURSOS HUMANOS', 'LORRAINE CRISTINE MARTINS DE ANDRADE'],
        ['26/08', 'TECELAGEM', 'SUELEN CLAUDINO VICENTE'],
        ['27/08', 'LOGÍSTICA', 'ARNALDO SILVA DA COSTA'],
        ['27/08', 'QUALIDADE', 'MILENA THUANE DA SILVA CONCEIÇÃO'],
        ['27/08', 'EMBALAGEM/TECELAGEM',
         'VERONICA CRISTINA DE CARVALHO SOARES'],
        ['28/08', 'PRODUCAO', 'MARIA LUCIA DE JESUS ALVES'],
        ['28/08', 'TECELAGEM', 'ROBERTA GOMES DA SILVA'],
        ['30/08', 'DESENVOLVIMENTO DE PRODUTOS',
         'AFONSO HENRIQUES DE MAGALHÃES PEREIRA'],
    ]
    context = {}
    context = {
        'titulo': 'Aniversariantes do mês de Agosto de 2018',
        'aniversariantes': aniversariantes,
        }
    return render(request, 'rh/aniversariantes.html', context)
