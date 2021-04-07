from pprint import pprint
from datetime import datetime

from django.urls import reverse
from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models
import comercial.queries as queries


class VendasPorModelo(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VendasPorModelo, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/vendas_por_modelo.html'
        self.title_name = 'Vendas por modelo'

    def mount_context_inicial(self):
        data = []
        zero_data_row = {'meta': ' ', 'data': ' '}
        zero_data_row.update({p['range']: 0 for p in self.periodos})
        total_data_row = zero_data_row.copy()

        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.order_by('-meta_estoque').values()
        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                    'modelo|TARGET': '_blank',
                    'modelo|LINK': reverse(
                        'comercial:define_meta__get',
                        args=[row['modelo']]),
                    **zero_data_row
                }
                data.append(data_row)
            data_row['meta'] = row['meta_estoque']
            data_row['data'] = row['data']

        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo'
            )
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        'modelo|TARGET': '_blank',
                        'modelo|LINK': reverse(
                            'comercial:define_meta__get',
                            args=[row['modelo']]),
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                total_data_row[periodo['range']] += row['qtd']
        self.context.update({
            'headers': ['Modelo', 'Meta de estoque', 'Data da meta',
                        *[p['descr'] for p in self.periodos]],
            'fields': ['modelo', 'meta', 'data',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style,
        })

    def mount_context(self):
        nfs = list(models.ModeloPassadoPeriodo.objects.filter(
            modelo_id=1).order_by('ordem').values())
        if len(nfs) == 0:
            self.context.update({
                'msg_erro': 'Nenhum período definido',
            })
            return
        self.data_nfs = list(nfs)

        self.periodos = []
        self.tot_peso = 0
        n_mes = 0
        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        self.style = {
            2: 'text-align: right;',
            3: 'text-align: left;',
        }
        for row in self.data_nfs:
            periodo = {
                'range': '{}:{}'.format(
                    n_mes+row['meses'], n_mes),
                'meses': row['meses'],
                'peso': row['peso'],
            }
            n_mes += row['meses']
            self.tot_peso += row['meses'] * row['peso']

            mes_fim = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            mes_ini = mes.strftime("%m/%Y")
            mes = dec_month(mes)
            if row['meses'] == 1:
                periodo['descr'] = mes_ini
            else:
                if mes_ini[-4:] == mes_fim[-4:]:
                    periodo['descr'] = '{} - {}'.format(mes_fim[:2], mes_ini)
                else:
                    periodo['descr'] = '{} - {}'.format(mes_fim, mes_ini)

            self.style[max(self.style.keys())+1] = 'text-align: right;'

            self.periodos.append(periodo)

        self.cursor = db_cursor_so(self.request)

        self.mount_context_inicial()
