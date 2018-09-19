from pprint import pprint
from datetime import datetime

from django.shortcuts import render

from utils.functions import inc_month


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


def aniversariantes(request, ano, mes):
    intmes = int(mes)
    intano = int(ano)
    mes = '{:02}'.format(intmes)
    datames = datetime(intano, intmes, 1)

    aniversariantes = [
        ['03/08', 'Simone da Silva Saraiva', 'Recursos Humanos'],
        ['03/08', 'Veronica Cordeiro Bezerra dos Santos', 'Tecelagem'],
        ['06/08', 'Carlos Alberto de Sousa Carvalho Junior', 'Expedição'],
        ['06/08', 'Jonas Martins', 'Tecelagem'],
        ['07/08', 'Jorge Marcelo de Almeida Gargaglione', 'Vendas'],
        ['07/08', 'Pedro José Nascimento de Oliveira', 'Jovem Aprendiz'],
        ['09/08', 'Luzia Vieira da Silva Araujo', 'Tecelagem'],
        ['09/08', 'Sonia Maria do Nascimento Reis', 'Producao'],
        ['10/08', 'Maria Aparecida Tiburcio', 'Tecelagem'],
        ['11/08', 'Tamires Fernanda dos Santos Marins', 'Expedição'],
        ['12/08', 'Douglas dos Santos Alves', 'Facilites'],
        ['13/08', 'Fabiana Abreu de Jesus', 'Tecelagem'],
        ['14/08', 'Adriana Maria de Souza Monteiro', 'Pcp'],
        ['15/08', 'Andreza Silva de Brito', 'Embalagem/Tecelagem'],
        ['15/08', 'Claudia Teixeira da Silva Avelino',
            'Desenvolvimento de Produtos'],
        ['17/08', 'Leiliane Maria da Silva', 'Embalagem/Tecelagem'],
        ['17/08', 'Regina Maria Sandra dos Santos', 'Tecelagem'],
        ['18/08', 'Patricia de Oliveira', 'Embalagem/Produção'],
        ['18/08', 'Valquiria Evangelista da Silva', 'Financeiro'],
        ['19/08', 'Erika Cristina Arigony Antonio', 'Tecelagem'],
        ['20/08', 'Fabiana Vasques Gonçalves', 'Expedição'],
        ['21/08', 'Fabiola Segundo da Motta Teixeira', 'Qualidade'],
        ['21/08', 'Maria da Gloria Miranda da Cruz', 'Producao'],
        ['25/08', 'Lorraine Cristine Martins de Andrade', 'Recursos Humanos'],
        ['26/08', 'Suelen Claudino Vicente', 'Tecelagem'],
        ['27/08', 'Arnaldo Silva da Costa', 'Logística'],
        ['27/08', 'Milena Thuane da Silva Conceição', 'Qualidade'],
        ['27/08', 'Veronica Cristina de Carvalho Soares',
            'Embalagem/Tecelagem'],
        ['28/08', 'Maria Lucia de Jesus Alves', 'Producao'],
        ['28/08', 'Roberta Gomes da Silva', 'Tecelagem'],
        ['30/08', 'Afonso Henriques de Magalhães Pereira',
            'Desenvolvimento de Produtos'],
        ['01/09', 'Viviane Pecanha Oliveira ', 'Assist de Expedição'],
        ['02/09', 'Rosilene Moura dos Santos ', 'Lider de Tecelagem'],
        ['03/09', 'Simone Lima da Cruz ', 'Costureira'],
        ['05/09', 'Sandra Duarte Tavares Reis Pinto ', 'Costureira'],
        ['05/09', 'Zilda Martins Costa ', 'Costureira'],
        ['07/09', 'Lucilene Santos de Lima ', 'Costureira'],
        ['09/09', 'Diéssica da Silva Manso ', 'Auxiliar Producao'],
        ['10/09', 'Tania Mara da Silva do Nascimento ', 'Costureira'],
        ['12/09', 'Alessandro dos Santos Duarte ', 'Assist. de Produção'],
        ['12/09', 'David Cosme Barrozo ', 'Assist. de Produção'],
        ['12/09', 'Ruth Barbosa de Lacerda ', 'Costureira'],
        ['13/09', 'Valeria Cristina da Silva Cunha ', 'Costureira'],
        ['14/09', 'Leonardo Andrade de Paula ', 'Assist. de Produção'],
        ['16/09', 'Fabiana Lacerda Jesuino ', 'Assist. de Produção'],
        ['16/09', 'Neuzeane Brando Carvalho ', 'Costureira'],
        ['16/09', 'Érica Leandro da Silva ', 'Assist. de Produção'],
        ['17/09', 'Cassio Flor Pereira ', 'Assist. de Produção'],
        ['18/09', 'Jucelino Cupertino Avelino ', 'Assist. de Manut. Predial'],
        ['20/09', 'Edinete dos Anjos da Silva ', 'Costureira'],
        ['20/09', 'Tania Regina Gomes da Silva ', 'Costureira'],
        ['20/09', 'Vanessa Cristina Moura dos Santos ', 'Costureira'],
        ['21/09', 'Bruna Vieira Coelho ', 'Assist. de Produção'],
        ['21/09',
         'Carlos Roberto de Souza da Silva ', 'Téc de Manutenção Eletrônica'],
        ['22/09', 'Ohana Karla da Silva Vinhas ', 'Assistente Financeiro'],
        ['23/09', 'Adriana da Silva Almirante ', 'Assist. de Produção'],
        ['25/09', 'Silvia Maria Duarte de Souza ', 'Costureira'],
        ['26/09', 'Giselle Rodrigues dos Santos ', 'Analista  de Produto'],
        ['26/09', 'Maristela Constantino da Silva Duque ', 'Costureira'],
        ['26/09',
         'Vanessa Fernanda Rodrigues de Miranda do Couto Bandeira ',
         'Lider de Facilites'],
        ['27/09', 'Bersange Galdino da Silva ', 'Gerente Industrial'],
        ['27/09', 'Fábio Fernandes de Oliveira ', 'Analista Contábil'],
        ['27/09', 'Raquel Damiana Santanna Ferreira ', 'Encarregada'],
        ['28/09', 'Brenna dos Santos Queiroz Bueno ', 'Auxiliar Producao'],
        ['28/09', 'Flavia da Silva Queiroz Bueno ', 'Assist. de Produção'],
        ['29/09', 'Aline Machado Borges ', 'Aux. de Serv. Gerais'],
        ['29/09', 'Fabiana Cristina da Silva ', 'Costureira'],
        ['30/09', 'Valesca Nunes de Freitas ', 'Assist. de Produção'],
    ]

    anteriormes = inc_month(datames, -1)
    intmesant = anteriormes.month
    mesant = '{:02}'.format(intmesant)
    temmesant = False
    for pessoa in aniversariantes:
        if pessoa[0][-2:] == mesant:
            temmesant = True
            break
    if not temmesant:
        intmesant = None

    posteriosmes = inc_month(datames, 1)
    intmespos = posteriosmes.month
    mespos = '{:02}'.format(intmespos)
    temmespos = False
    for pessoa in aniversariantes:
        if pessoa[0][-2:] == mespos:
            temmespos = True
            break
    if not temmespos:
        intmespos = None

    context = {
        'datames': datames,
        'intmesant': intmesant,
        'intanoant': anteriormes.year,
        'intmespos': intmespos,
        'intanopos': posteriosmes.year,
        'aniversariantes': [
            pessoa for pessoa in aniversariantes
            if pessoa[0][-2:] == mes],
        }
    return render(request, 'rh/aniversariantes.html', context)
