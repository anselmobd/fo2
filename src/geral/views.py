import yaml

from django.shortcuts import render, redirect
from django.db import connections
from django.views import View

from fo2.models import rows_to_dict_list

from .models import Painel, InformacaoModulo


def index(request):
    context = {}
    return render(request, 'geral/index.html', context)


def deposito(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          d.CODIGO_DEPOSITO COD
        , d.DESCRICAO DESCR
        , d.TIP_PROPRIEDADE_DEPOSITO PROP
        , d.CNPJ9
        , d.CNPJ4
        , d.CNPJ2
        , CASE WHEN d.CNPJ9 = 0 THEN ' '
          ELSE coalesce(coalesce(f.NOME_FANTASIA, f.NOME_FORNECEDOR), '#')
          END FORN
        FROM BASI_205 d
        LEFT JOIN SUPR_010 f
          ON f.FORNECEDOR9 = d.CNPJ9
         AND f.FORNECEDOR4 = d.CNPJ4
         AND f.FORNECEDOR2 = d.CNPJ2
        ORDER BY
          d.CODIGO_DEPOSITO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    propriedades = {
        1: 'Próprio',
        2: 'Em terceiros',
        3: 'De terceiros',
    }
    for row in data:
        if row['FORN'] == ' ':
            row['CNPJ'] = ''
        else:
            row['CNPJ'] = \
                '{CNPJ9:09}/{CNPJ4:04}-{CNPJ2:02} - {FORN}'.format(**row)
        if row['PROP'] in propriedades:
            row['PROP'] = '{} - {}'.format(
                row['PROP'], propriedades[row['PROP']])
    context = {
        'titulo': 'Depósitos',
        'headers': ('Depósito', 'Descrição', 'Propriedade', 'Terceiro'),
        'fields': ('COD', 'DESCR', 'PROP', 'CNPJ'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


def estagio(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          e.CODIGO_ESTAGIO EST
        , e.DESCRICAO DESCR
        , CASE WHEN e.CODIGO_DEPOSITO = 0 THEN ' '
          ELSE e.CODIGO_DEPOSITO || '-' || d.DESCRICAO
          END DEP
        , e.LEED_TIME LT
        FROM MQOP_005 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.CODIGO_DEPOSITO
        ORDER BY
          e.CODIGO_ESTAGIO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    context = {
        'titulo': 'Estágios',
        'headers': ('Estágio', 'Descrição', 'Lead time', 'Depósito'),
        'fields': ('EST', 'DESCR', 'LT', 'DEP'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


class PainelView(View):

    def get(self, request, *args, **kwargs):
        if 'painel' in kwargs:
            if len(kwargs['painel']) == 0:
                return redirect('apoio_ao_erp')

        cursor = connections['so'].cursor()
        painel = Painel.objects.filter(slug=kwargs['painel'])
        if len(painel) == 0:
            return redirect('apoio_ao_erp')

        layout = painel[0].layout
        config = yaml.load(layout)
        for modulo in config['dados']:
            modulo['dados'] = InformacaoModulo.objects.filter(
                painel_modulo__nome=modulo['modulo']
            ).order_by('-data')

        context = {
            'titulo': painel[0].nome,
            'config': config,
            }
        return render(
            request, 'geral/{}.html'.format(config['template']), context)
