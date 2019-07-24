from pprint import pprint

from django.db import connections
from django.db.models import Exists, OuterRef
from django.http import JsonResponse

from utils.views import totalize_data
from base.views import O2BaseGetView

import comercial.models
import lotes.models


class AProduzir(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(AProduzir, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/a_produzir.html'
        self.title_name = 'A produzir por modelo'

    def mount_context(self):
        cursor = connections['so'].cursor()

        data = []

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.exclude(multiplicador=0)
        metas = metas.exclude(venda_mensal=0)
        metas = metas.values()

        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                }
                data.append(data_row)
            data_row['meta_giro'] = row['meta_giro']
            data_row['meta_estoque'] = row['meta_estoque']
            data_row['meta'] = row['meta_giro'] + row['meta_estoque']
            data_row['total_op'] = 0
            data_row['total_op|CLASS'] = 'total_op-{}'.format(row['modelo'])

        data = sorted(data, key=lambda i: -i['meta'])

        totalize_data(data, {
            'sum': ['meta_giro', 'meta_estoque', 'meta', 'total_op'],
            'count': [],
            'descr': {'modelo': 'Totais:'}
        })
        data[-1]['|STYLE'] = 'font-weight: bold;'
        data[-1]['total_op|CLASS'] = 'total_op__total'

        self.context.update({
            'headers': ['Modelo', 'Meta de giro', 'Meta de estoque',
                        'Meta total', 'OPs'],
            'fields': ['modelo', 'meta_giro', 'meta_estoque',
                       'meta', 'total_op'],
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })


def op_producao_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {}

    try:
        data_op = lotes.models.busca_op(
            cursor, modelo=modelo, tipo='v', tipo_alt='p',
            situacao='a', posicao='p')

        if len(data_op) == 0:
            total_op = 0
        else:
            totalize_data(data_op, {
                'sum': ['QTD_AP'],
                'count': [],
                'descr': {'OP': 'T:'},
            })
            total_op = data_op[-1]['QTD_AP']

    except lotes.models.SolicitaLote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar OP',
        })
        return JsonResponse(data, safe=False)

    data = {
        'result': 'OK',
        'total_op': total_op,
    }
    return JsonResponse(data, safe=False)
