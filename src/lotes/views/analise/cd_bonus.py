from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.row_field import PrepRows
from utils.table_defs import TableDefsHpS
from utils.views import group_rowspan, totalize_grouped_data

from lotes.forms.analise import CdBonusViewForm
from lotes.queries.analise.cd_bonus import cd_bonus_query


class CdBonusView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CdBonusView, self).__init__(*args, **kwargs)
        self.Form_class = CdBonusViewForm
        self.template_name = 'lotes/analise/cd_bonus.html'
        self.title_name = 'Análise - Produzido - CD (bônus)'
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.get_args2context = True
        self.form_class_has_initial = True
        self.get_args = ['data']

        self.table_defs = TableDefsHpS({
            'usuario': ["Usuário"],
            'ref': ["Referência"],
            'op': ["OP"],
            'ref_dest': ["Ref. destino"],
            'qtd': ["Quantidade", 'r'],
        })

    def monta_dados_dest(self, dest):
        dados_dest = [
            row
            for row in self.dados
            if row['dest'] == dest
        ]
        group = ['usuario']
        if dados_dest:
            totalize_grouped_data(dados_dest, {
                'group': group,
                'sum': ['qtd'],
                'count': [],
                'descr': {'usuario': 'Total:'},
                'global_sum': ['qtd'],
                'global_descr': {'usuario': 'Total geral:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(dados_dest, group)
        self.context[dest] = {
            'titulo': dest.capitalize(),
            'data': dados_dest,
            'group': group,
            'vazio': "Sem produção no dia"
        }
        self.table_defs.hfs_dict_context(self.context[dest])

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.dados = cd_bonus_query(
            self.cursor,
            data=self.data,
        )

        PrepRows(
            self.dados,
        ).a_blank(
            'ref', 'produto:ref__get'
        ).a_blank(
            'op', 'producao:op__get'
        ).process()

        self.monta_dados_dest('atacado')
        self.monta_dados_dest('varejo')
