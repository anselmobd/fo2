from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.row_field import PrepRows
from utils.table_defs import TableDefsHpS
from utils.views import group_rowspan, totalize_grouped_data, totalize_data
from base.models import Colaborador

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
            'qtd': ["Quantidade Lote", 'r'],
            'qtd_res': ["Quantidade Solicitação", 'r'],
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
                'sum': ['qtd', 'qtd_res'],
                'count': [],
                'descr': {'usuario': "Total:"},
                'global_sum': ['qtd', 'qtd_res'],
                'global_descr': {'usuario': f"Total do {dest}:"},
                'row_style': "font-weight: bold;",
            })
            group_rowspan(dados_dest, group)
        self.context[dest] = {
            'titulo': dest.capitalize(),
            'data': dados_dest,
            'group': group,
            'vazio': "Sem produção no dia"
        }
        self.table_defs.hfs_dict_context(self.context[dest])

    def monta_dados_totais(self):
        dict_totais = {}
        for row in self.dados:
            try:
                row_totais = dict_totais[row['usuario']]
            except KeyError:
                row_totais = dict_totais[row['usuario']] = {
                    'usuario': row['usuario'],
                    'qtd': 0,
                    'qtd_res': 0,
                }
            row_totais['qtd'] += row['qtd']
            row_totais['qtd_res'] += row['qtd_res']
        pprint(dict_totais)
        dados_totais = list(dict_totais.values())
        pprint(dados_totais)
        if dados_totais:
            totalize_data(dados_totais, {
                'sum': ['qtd', 'qtd_res'],
                'count': [],
                'descr': {'usuario': 'Total do dia:'},
                'row_style': 'font-weight: bold;',
            })
        self.context['totais'] = {
            'titulo': 'Por usuário',
            'data': dados_totais,
        }
        self.table_defs.hfs_dict_context(
            self.context['totais'],
            'usuario',
            'qtd',
            'qtd_res',
        )

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        colaboradores = Colaborador.objects.filter(
            cd_bonus=True
        ).values('matricula')
        usuarios = [
            colaborador['matricula']
            for colaborador in colaboradores
        ]

        self.dados = cd_bonus_query(
            self.cursor,
            data=self.data,
            usuario=usuarios,
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
        self.monta_dados_totais()
