from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.table_defs import TableDefsHpS
from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms.por_celula import PorCelulaForm
from lotes.queries.producao.por_celula import *


class PorCelula(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PorCelula, self).__init__(*args, **kwargs)
        self.Form_class = PorCelulaForm
        self.template_name = 'lotes/por_celula.html'
        self.title_name = 'Produção por célula/estágio'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if not self.data_ate:
            self.data_ate = self.data_de
        
        divisao = self.celula.divisao_producao if self.celula else None

        dados = por_celula_query(
            self.cursor,
            self.data_de,
            self.data_ate,
            divisao,
            self.estagio.codigo_estagio,
        )

        if not dados:
            self.context.update({
                'msg_erro': 'Nenhuma produção encontrada',
            })
            return

        group = ['data']
        totalize_grouped_data(dados, {
            'group': group,
            'sum': ['lotes', 'qtd', 'perda'],
            'descr': {'data': 'Total do dia:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['lotes', 'qtd', 'perda'],
            'global_descr':  {'data': 'Total geral:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        TableDefsHpS({
            'data': "Data",
            'op': "OP",
            'cliente': "Cliente",
            'ref': "Referência",
            'lotes': ["Lotes", 'r'],
            'qtd': ["Produzido", 'r'],
            'perda': ["Perda", 'r'],
        }).hfs_dict_context(
            self.context,
            update={
                'group': group,
                'dados': dados,
            }
        )
