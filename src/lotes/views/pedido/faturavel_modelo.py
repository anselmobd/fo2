from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views.o2.get_post import O2BaseGetPostView
from geral.functions import config_get_value
from utils.views import group_rowspan, totalize_grouped_data
from utils.table_defs import TableDefs

import produto.queries
import comercial.models

import lotes.models
from lotes.queries.pedido import faturavel_modelo as queries_faturavel_modelo, varejo_empenhado
from lotes.queries.pedido import faturado_empenhado
from lotes.forms.pedido import faturavel_modelo as forms_faturavel_modelo


class FaturavelModelo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FaturavelModelo, self).__init__(*args, **kwargs)
        self.Form_class = forms_faturavel_modelo.Form
        self.template_name = 'lotes/pedido/faturavel_modelo.html'
        self.title_name = 'Pedido faturável por modelo'
        self.get_args = ['modelo']
        self.get_args2form = True
        self.cleaned_data2self = True

        self.table_defs = TableDefs(
            {
                'EMP_SIT': ["Sit.Emp."],
                'PEDIDO': ["Nº pedido"],
                'AGRUPADOR': ["Agrupador", 'l', 16],
                'PEDIDOS': ["Pedidos", 'l', 16],
                'DATA': ["Data embarque"],
                'CLIENTE': ["Cliente"],
                'REF': ["Referência"],
                'QTD_EMP': ["Qtd.Emp.", 'r'],
                'QTD_SOL': ["Qtd.Fin.", 'r'],
                'QTD': ["Qtd.pedida", 'r', 1],
                'QTD_FAT': ["Qtd.faturada", 'r', 9],
                'QTD_AFAT': ["Qtd.faturar", 'r', 4],
                'PAC': ["Pacote", 'r', 2],
                'QTD_PAC': ["Qtd.pacote", 'r', 2],
                'FAT': ["Faturamento", 'l', 4],
            },
            ['header', '+style', 'flags_bitmap'],
            style = {'_': 'text-align'},
        )
        # flags_bitmap
        # 1 = faturavel parcialmente faturado
        # 2 = pacotes
        # 4 = faturavel
        # 8 = faturado
        # 16 = só para dados_var

        self._pac_quant = None

    @property
    def pac_quant(self):
        if self._pac_quant is None:
            pac_quant_data = comercial.models.MetaModeloReferencia.objects.filter(
                modelo=self.modelo,
                # incl_excl='i',
            ).values('referencia', 'quantidade')
            self._pac_quant = {
                row['referencia']: row['quantidade']
                for row in pac_quant_data
            } if pac_quant_data else {}
        return self._pac_quant

    def monta_dados(self, data, faturavel=False):
        tot_qtd_fat = 0
        for row in data:
            row['PEDIDO'] = f"{row['PEDIDO']}"
            row['PEDIDO|GLYPHICON'] = '_'
            row['PEDIDO|TARGET'] = '_blank'
            row['PEDIDO|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO']])
            tot_qtd_fat += row['QTD_FAT']
            row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
            row['DATA'] = row['DATA'].date() if row['DATA'] else ''
            if row['EMP_SIT_MIN'] == 0:
                if row['AGRUPADOR'] == 0:
                    row['EMP_SIT'] = 'Sem Emp.'
                else:
                    row['EMP_SIT'] = 'Emp.Varejo'
            else:
                if row['EMP_SIT_MIN'] == row['EMP_SIT_MAX']:
                    row['EMP_SIT'] = row['EMP_SIT_MIN']
                else:
                    row['EMP_SIT'] = f"{row['EMP_SIT_MIN']} a {row['EMP_SIT_MAX']}"
            if self.com_pac:
                if row['REF'] in self.pac_quant:
                    row['PAC'] = self.pac_quant[row['REF']]
                else:
                    row['PAC'] = 1
                if faturavel:
                    row['QTD_PAC'] = row['QTD_AFAT'] * row['PAC']
                else:
                    row['QTD_PAC'] = row['QTD_FAT'] * row['PAC']

        if self.com_pac:
            tot_sum_fields = ['QTD_EMP', 'QTD_SOL', 'QTD_PAC']
        else:
            if faturavel:
                tot_sum_fields = ['QTD_AFAT', 'QTD_EMP', 'QTD_SOL']
            else:
                tot_sum_fields = ['QTD_FAT', 'QTD_EMP', 'QTD_SOL']

        group = ['EMP_SIT']
        totalize_grouped_data(data, {
            'group': group,
            'sum': tot_sum_fields,
            'count': [],
            'descr': {'PEDIDO': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': tot_sum_fields,
            'global_descr': {'EMP_SIT': 'Total geral:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        flags_bitmap = (
            (1 * (tot_qtd_fat != 0 and faturavel)) +
            (2 * self.com_pac) +
            (4 * faturavel) +
            (8 * (not faturavel))
        )
        dados = self.table_defs.hfs_dict(bitmap=flags_bitmap)
        dados.update({
            'data': data,
            'group': group,
        })
        return dados

    def add_links_pedidos(self, pedidos):
        if not pedidos:
            return ''
        pedido_list = []
        for pedido in pedidos.split(','):
            pedido = pedido.strip()
            link = reverse(
                'producao:pedido__get', args=[pedido])
            pedido_list.append(
                f'<a href="{link}" '
                f'target="_BLANK">{pedido}</a>'
            )
        return ', '.join(pedido_list)

    def monta_dados_var(self, data):
        for row in data:
            if row['EMP_SIT_MIN'] == row['EMP_SIT_MAX']:
                row['EMP_SIT'] = row['EMP_SIT_MIN']
            else:
                row['EMP_SIT'] = f"{row['EMP_SIT_MIN']} a {row['EMP_SIT_MAX']}"
            row['PEDIDOS'] = self.add_links_pedidos(row['PEDIDOS'])
            row['PEDIDOS|SAFE'] = True
            # if self.com_pac:
            #     if row['REF'] in self.pac_quant:
            #         row['PAC'] = self.pac_quant[row['REF']]
            #     else:
            #         row['PAC'] = 1
            #     row['QTD_PAC'] = row['QTD'] * row['PAC']

        # if self.com_pac:
        #     tot_sum_fields = ['QTD_PAC']
        # else:
        tot_sum_fields = ['QTD_EMP']

        group = ['EMP_SIT']
        totalize_grouped_data(data, {
            'group': group,
            'sum': tot_sum_fields,
            'count': [],
            'descr': {'PEDIDO': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': tot_sum_fields,
            'global_descr': {'EMP_SIT': 'Total geral:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        var_fields=[
            'EMP_SIT',
            'AGRUPADOR',
            'PEDIDOS',
            'REF',
            'QTD_EMP',
        ]
        # if self.com_pac:
        #     var_fields += [
        #         'PAC',
        #         'QTD_PAC',
        #     ]
        dados = self.table_defs.hfs_dict(*var_fields)
        dados.update({
            'data': data,
            'group': group,
        })
        return dados


    def mount_context(self):
        cursor = db_cursor_so(self.request)

        codigo_colecao = self.colecao.colecao if self.colecao else None
        
        lead = 0
        if self.modelo:
            lead = produto.queries.lead_de_modelo(cursor, self.modelo)

        lc_lead = 0
        if self.colecao:
            try:
                lc = lotes.models.RegraColecao.objects.get(colecao=codigo_colecao)
                lc_lead = lc.lead
            except lotes.models.RegraColecao.DoesNotExist:
                pass
        lead = max(lead, lc_lead)

        self.context.update({
            'lead': lead,
        })

        if self.considera_lead == 's':
            dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
            self.context['dias_alem_lead'] = dias_alem_lead
            busca_periodo = lead + dias_alem_lead
        else:
            busca_periodo = ''

        self.com_pac = self.considera_pacote == 's'

        data = queries_faturavel_modelo.query(
            cursor,
            periodo=':{}'.format(busca_periodo),
            modelo=self.modelo,
            colecao=codigo_colecao,
            tam=self.tam,
            cor=self.cor,
            com_pac=self.com_pac,
            cached=False,
        )
        if data:
            self.context.update({
                'dados_pre': self.monta_dados(data, faturavel=True),
            })

        if self.considera_lead == 's':
            data_pos = queries_faturavel_modelo.query(
                cursor,
                periodo='{}:'.format(busca_periodo),
                modelo=self.modelo,
                colecao=codigo_colecao,
                tam=self.tam,
                cor=self.cor,
                com_pac=self.com_pac,
                cached=False,
            )
            if data_pos:
                self.context.update({
                    'dados_pos': self.monta_dados(data_pos, faturavel=True),
                })

        data_fat = faturado_empenhado.query(
            cursor,
            modelo=self.modelo,
            colecao=codigo_colecao,
            cor=self.cor,
            tam=self.tam,
            com_pac=self.com_pac,
            cached=False,
        )
        if data_fat:
            self.context.update({
                'dados_fat': self.monta_dados(data_fat, faturavel=False),
            })

        data_var = varejo_empenhado.query(
            cursor,
            modelo=self.modelo,
            colecao=codigo_colecao,
            cor=self.cor,
            tam=self.tam,
            com_pac=False,
            cached=False,
        )
        if data_var:
            self.context.update({
                'dados_var': self.monta_dados_var(data_var),
            })
