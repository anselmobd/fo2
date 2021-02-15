from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.numbers import num_digits

import insumo.functions


class MapaCompras(View):
    template_name = 'insumo/mapa_compras.html'
    title_name = 'Mapa de compras'

    def __init__(self, *args, **kwargs):
        super(MapaCompras, self).__init__(*args, **kwargs)
        self.calc = True

    def mount_context(self, cursor, nivel, ref, cor, tam):
        context = {
            'nivel': nivel,
            'ref': ref,
            'cor': cor,
            'tam': tam,
            'calc': self.calc,
        }

        datas = insumo.functions.mapa_compras_semana_ref_dados(
            cursor, nivel, ref, cor, tam, calc=self.calc)
        if 'msg_erro' in datas:
            context.update({
                'msg_erro': datas['msg_erro'],
            })
            return context

        data_id = datas['data_id']

        for row in data_id:
            row['REF'] = row['REF'] + ' - ' + row['DESCR']
            row['COR'] = row['COR'] + ' - ' + row['DESCR_COR']
            if row['TAM'] != row['DESCR_TAM']:
                row['TAM'] = row['TAM'] + ' - ' + row['DESCR_TAM']
            if row['ULT_ENTRADA']:
                row['ULT_ENTRADA'] = row['ULT_ENTRADA'].date()
            else:
                row['ULT_ENTRADA'] = ''
            if row['ULT_SAIDA']:
                row['ULT_SAIDA'] = row['ULT_SAIDA'].date()
            else:
                row['ULT_SAIDA'] = ''
            if row['DT_INVENTARIO']:
                row['DT_INVENTARIO'] = row['DT_INVENTARIO'].date()
            else:
                row['DT_INVENTARIO'] = ''
            row['REP_STR'] = '{}d. ({}s.)'.format(
                row['REPOSICAO'], row['SEMANAS'])
            if row['QUANT'] < row['STQ_MIN']:
                row['QUANT|STYLE'] = 'font-weight: bold; color: red;'

        context.update({
            'headers_id': ['Nível', 'Insumo', 'Cor', 'Tamanho',
                           'Reposição', 'Est.Mínimo', 'Múltiplo',
                           'Estoque', 'Unid.',
                           'Última Entrada', 'Última Saída',
                           'Inventário'],
            'fields_id': ['NIVEL', 'REF', 'COR', 'TAM',
                          'REP_STR', 'STQ_MIN', 'LOTE_MULTIPLO',
                          'QUANT', 'UNID',
                          'ULT_ENTRADA', 'ULT_SAIDA',
                          'DT_INVENTARIO'],
            'data_id': data_id,
        })

        semana_hoje = datas['semana_hoje']

        # Necessidades
        data_ins = datas['data_ins']

        max_digits = 0
        for row in data_ins:
            max_digits = max(
                max_digits,
                num_digits(row['QTD_INSUMO'])
            )

        for row in data_ins:
            row['SEMANA_NECESSIDADE|LINK'] = reverse(
                'insumo:mapa_compras_necessidade_detalhe',
                args=[nivel, ref, cor, tam, row['SEMANA_NECESSIDADE']])
            row['SEMANA_NECESSIDADE|TARGET'] = '_blank'
            row['QTD_INSUMO|DECIMALS'] = max_digits
            if row['SEMANA_NECESSIDADE'] < semana_hoje:
                row['QTD_INSUMO|STYLE'] = \
                    'font-weight: bold; color: darkorange;'
            if 'ITALIC' in row:
                row['QTD_INSUMO|STYLE'] = \
                    'font-weight: bold; font-style: italic;'

        context.update({
            'header_link_ins': reverse(
                'insumo:mapa_compras_necessidades__get',
                args=[nivel, ref, cor, tam, 't']),
            'headers_ins': ['Semana', 'Quantidade'],
            'fields_ins': ['SEMANA_NECESSIDADE', 'QTD_INSUMO'],
            'style_ins': {2: 'text-align: right;'},
            'data_ins': data_ins,
        })

        # Previsões
        data_prev = datas['data_prev']

        max_digits = 0
        for row in data_prev:
            max_digits = max(
                max_digits,
                num_digits(row['QTD'])
            )

        previsao_alterada = False
        for row in data_prev:
            if row['QTD_ORIGINAL'] != row['QTD']:
                previsao_alterada = True
            row['QTD|DECIMALS'] = max_digits
            if 'ITALIC' in row:
                row['QTD|STYLE'] = \
                    'font-weight: bold; font-style: italic;'

        headers_prev = ['Semana', 'Previsto']
        fields_prev = ['DT_NECESSIDADE', 'QTD_ORIGINAL']
        style_prev = {2: 'text-align: right;'}
        if previsao_alterada:
            headers_prev.append(('Previsto -</br>Necessidade',))
            fields_prev.append('QTD')
            style_prev[3] = 'text-align: right;'

        context.update({
            'headers_prev': headers_prev,
            'fields_prev': fields_prev,
            'style_prev': style_prev,
            'data_prev': data_prev,
        })

        # Adiantamentos de recebimentos
        data_adi = datas['data_adi']

        # Recebimentos
        data_irs = datas['data_irs']

        max_digits = 0
        for row in data_irs:
            max_digits = max(
                max_digits,
                num_digits(row['QTD_A_RECEBER'])
            )

        for row in data_irs:
            row['QTD_A_RECEBER|DECIMALS'] = max_digits
            plural = 's' if ',' in row['PEDIDO'] else ''
            row['QTD_A_RECEBER|HOVER'] = f"Pedido{plural} {row['PEDIDO']}"
            if row['SEMANA_ENTREGA'] < semana_hoje:
                row['QTD_A_RECEBER|STYLE'] = \
                    'font-weight: bold; color: darkcyan;'
            if row['SEMANA_ENTREGA'] in [r['SEMANA_ORIGEM'] for r in data_adi]:
                row['QTD_A_RECEBER|STYLE'] = \
                    'font-weight: bold; color: brown;'

        safe_qtd_header = (
            'Quantidade<span style="font-size: 50%;vertical-align: super;" '
            'class="glyphicon glyphicon-comment" aria-hidden="true"></span>',
        )
        context.update({
            'headers_irs': ['Semana', safe_qtd_header],
            'fields_irs': ['SEMANA_ENTREGA', 'QTD_A_RECEBER'],
            'style_irs': {2: 'text-align: right;'},
            'data_irs': data_irs,
        })

        # Adiantamentos de recebimentos
        max_digits = 0
        for row in data_adi:
            max_digits = max(
                max_digits,
                num_digits(row['QUANT'])
            )

        for row in data_adi:
            row['QUANT|DECIMALS'] = max_digits

        context.update({
            'headers_adi': ['De', 'Para', 'Quantidade'],
            'fields_adi': ['SEMANA_ORIGEM', 'SEMANA_DESTINO', 'QUANT'],
            'style_adi': {3: 'text-align: right;'},
            'data_adi': data_adi,
        })

        estoque_minimo = datas['estoque_minimo']
        semana_recebimento = datas['semana_recebimento']
        semanas = datas['semanas']

        # se tem alguma entrada ou saída
        data_sug = datas['data_sug']
        if len(data_sug) != 0:

            max_digits = 0
            for row in data_sug:
                max_digits = max(
                    max_digits,
                    num_digits(row['QUANT'])
                )

            for row in data_sug:
                row['QUANT|DECIMALS'] = max_digits
                if row['SEMANA_RECEPCAO'] < semana_hoje:
                    row['SEMANA_RECEPCAO|STYLE'] = \
                        'font-weight: bold; color: red;'
                if row['SEMANA_COMPRA'] < semana_hoje:
                    row['QUANT|STYLE'] = \
                        'font-weight: bold; color: darkmagenta;'

            context.update({
                'headers_sug': ['Semana de compra', 'Semana de chegada',
                                'Quantidade'],
                'fields_sug': ['SEMANA_COMPRA', 'SEMANA_RECEPCAO', 'QUANT'],
                'style_sug': {3: 'text-align: right;'},
                'data_sug': data_sug,
            })

        data = []
        if 'data' in datas:
            data = datas['data']
        if len(data) != 0:

            max_digits = 0
            for row in data:
                max_digits = max(
                    max_digits,
                    num_digits(
                        row['ESTOQUE'] +
                        row['NECESSIDADE'] +
                        row['NECESSIDADE_PASSADA'] +
                        row['RECEBIMENTO'] +
                        row['RECEBIMENTO_ATRASADO'] +
                        row['COMPRAR'] +
                        row['COMPRAR_PASSADO'] +
                        row['RECEBER']
                    ),
                )

            arrows = []
            for index, row in enumerate(data):

                if row['RECEBIMENTO_MOVIDO'] != 0:
                    row['RECEBIMENTO_MOVIDO|STYLE'] = \
                        'font-weight: bold; color: brown;'

                movidos_no_dia = [row_adi for row_adi in data_adi
                                  if row_adi['SEMANA_ORIGEM'] == row['DATA']]

                if len(movidos_no_dia) != 0:
                    row['RECEBIMENTO|STYLE'] = \
                        'font-weight: bold; color: brown;'

                if row['ESTOQUE'] < estoque_minimo:
                    if index == 0:
                        row['ESTOQUE|STYLE'] = 'font-weight: bold; color: red;'
                    else:
                        row['ESTOQUE|STYLE'] = 'color: red;'
                if row['NECESSIDADE_PASSADA'] > 0:
                    row['NECESSIDADE_PASSADA|STYLE'] = \
                        'font-weight: bold; color: darkorange;'
                if row['RECEBIMENTO_ATRASADO'] > 0:
                    row['RECEBIMENTO_ATRASADO|STYLE'] = \
                        'font-weight: bold; color: darkcyan;'
                if row['COMPRAR_PASSADO'] > 0:
                    row['COMPRAR_PASSADO|STYLE'] = \
                        'font-weight: bold; color: darkmagenta;'
                if row['DATA'] < semana_recebimento and \
                        row['RECEBER'] > 0:
                    row['RECEBER|STYLE'] = \
                        'font-weight: bold; color: darkmagenta;'

                row['ESTOQUE|DECIMALS'] = max_digits
                row['NECESSIDADE|DECIMALS'] = max_digits
                row['NECESSIDADE_PASSADA|DECIMALS'] = max_digits
                row['RECEBIMENTO|DECIMALS'] = max_digits
                row['RECEBIMENTO_ATRASADO|DECIMALS'] = max_digits
                row['COMPRAR|DECIMALS'] = max_digits
                row['COMPRAR_PASSADO|DECIMALS'] = max_digits
                row['RECEBER|DECIMALS'] = max_digits

                isemana = index+1
                if row['RECEBER'] > 0:
                    if isemana <= semanas:
                        arrows.append([1, 8, isemana, 9, 'darkmagenta'])
                    else:
                        arrows.append([isemana-semanas, 7, isemana, 9,
                                       'steelblue'])
                for row_adi in data_adi:
                    if row_adi['SEMANA_ORIGEM'] == row['DATA']:
                        row_adi['ISEMANA_ORIGEM'] = isemana
                    if row_adi['SEMANA_DESTINO'] == row['DATA']:
                        row_adi['ISEMANA_DESTINO'] = isemana

            for row_adi in data_adi:
                if 'ISEMANA_DESTINO' in row_adi:
                    arrows.append([
                        row_adi['ISEMANA_ORIGEM'], 4,
                        row_adi['ISEMANA_DESTINO'], 6, 'brown'])
                else:
                    arrows.append([
                        row_adi['ISEMANA_ORIGEM'], 4,
                        1, 5, 'brown'])

            context.update({
                'headers': ['Semana', 'Estoque Real',
                            'Necessidade', 'Necessidade passada',
                            'Recebimento', 'Recebimento atrasado',
                            'Recebimento movido',
                            'Compra sugerida', 'Compra atrasada',
                            'Recebimento sugerido'],
                'fields': ['DATA', 'ESTOQUE',
                           'NECESSIDADE', 'NECESSIDADE_PASSADA',
                           'RECEBIMENTO', 'RECEBIMENTO_ATRASADO',
                           'RECEBIMENTO_MOVIDO',
                           'COMPRAR', 'COMPRAR_PASSADO', 'RECEBER'],
                'style': {2: 'text-align: right;',
                          3: 'text-align: right;',
                          4: 'text-align: right;',
                          5: 'text-align: right;',
                          6: 'text-align: right;',
                          7: 'text-align: right;',
                          8: 'text-align: right;',
                          9: 'text-align: right;',
                          10: 'text-align: right;'},
                'data': data,
                'arrows': arrows,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(
                cursor, kwargs['nivel'], kwargs['ref'],
                kwargs['cor'], kwargs['tam']))
        return render(request, self.template_name, context)


class MapaComprasCalc(MapaCompras):
    def __init__(self, *args, **kwargs):
        super(MapaComprasCalc, self).__init__(*args, **kwargs)
        self.calc = True
