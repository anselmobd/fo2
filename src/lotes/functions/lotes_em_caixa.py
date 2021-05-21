from pprint import pprint

from django.urls import reverse

import lotes.queries


def lotes_em_caixa(view_obj, cursor, op):
    data_op = lotes.queries.op.op_inform(cursor, op, cached=False)
    if len(data_op) == 0:
        view_obj.context.update({
            'msg_erro': 'OP não encontrada',
        })
        return False

    row_op = data_op[0]
    if row_op['TIPO_REF'] not in ['MD', 'MP']:
        view_obj.context.update({
            'msg_erro': 'Lotes agrupados em caixas é utilizado apenas para MD e MP',
        })
        return False

    if row_op['SITUACAO'] == 9:
        view_obj.context.update({
            'msg_erro': 'OP cancelada!',
        })
        return False

    view_obj.context.update({
        'ref': row_op['REF'],
        'tipo_ref': row_op['TIPO_REF'],
        'colecao': row_op['COLECAO'],
    })

    # Lotes order 'r' = referência + cor + tamanho + OC
    data = lotes.queries.lote.get_imprime_lotes(cursor, op=op, order='r')
    if len(data) == 0:
        view_obj.context.update({
            'msg_erro': 'Lotes não encontrados',
        })
        return False

    try:
        rc = lotes.models.RegraColecao.objects_referencia.get(
            colecao=data[0]['colecao'], referencia=view_obj.context['ref'][0])
        view_obj.context.update({
            'ini_ref': rc.referencia,
        })
    except lotes.models.RegraColecao.DoesNotExist:
        try:
            rc = lotes.models.RegraColecao.objects.get(
                colecao=data[0]['colecao'])
            view_obj.context.update({
                'ini_ref': '',
            })
        except lotes.models.RegraColecao.DoesNotExist:
            view_obj.context.update({
                'msg_erro': 'Regra de coleção e referência não encontrados',
            })
            return False
    view_obj.context.update({
        'lotes_caixa': rc.lotes_caixa,
    })

    caixa_op = 0
    cor_ant = '!!!!!!'
    tam_ant = '!!!!'
    for lote in data:
        lote['lote'] = f"{lote['periodo']}{lote['oc']:05}"
        lote['lote|LINK'] = reverse('producao:posicao__get', args=[lote['lote']])
        lote['peso'] = " "
        
        # inicio - necessários para impressão de etiquetas
        lote['data_entrada_corte'] = row_op['DT_CORTE']
        lote['situacao'] = row_op['SITUACAO']
        # fim

        if lote['cor'] != cor_ant or lote['tam'] != tam_ant:
            cor_ant = lote['cor']
            tam_ant = lote['tam']
            caixa_ct = 1
            caixa_op += 1
            conta_lotes_caixa = 1
            n_lote_caixa = 0
            qtd_caixa = 0
        else:
            conta_lotes_caixa += 1

        if conta_lotes_caixa > rc.lotes_caixa:
            conta_lotes_caixa = 1
            caixa_ct += 1
            caixa_op += 1
            n_lote_caixa = 1
            qtd_caixa = lote['qtd']
        else:
            n_lote_caixa += 1
            qtd_caixa += lote['qtd']

        lote['n_lote_caixa'] = n_lote_caixa
        lote['qtd_caixa'] = qtd_caixa
        lote['caixa_op'] = caixa_op
        lote['caixa_ct'] = caixa_ct

    caixa_op_ant = 0
    cor_ant = '!!!!!!'
    tam_ant = '!!!!'
    total_cx_op = data[-1]['caixa_op']
    for lote in data[::-1]:
        if lote['caixa_op'] != caixa_op_ant:
            caixa_op_ant = lote['caixa_op']
            qtd_caixa = lote['qtd_caixa']
            qtd_lote_caixa = lote['n_lote_caixa']
            lote['qtd_lote_caixa'] = qtd_lote_caixa
        else:
            lote['qtd_caixa'] = qtd_caixa
            lote['qtd_lote_caixa'] = qtd_lote_caixa

        if lote['cor'] != cor_ant or lote['tam'] != tam_ant:
            cor_ant = lote['cor']
            tam_ant = lote['tam']
            total_cx_ct = lote['caixa_ct']

        lote['num_caixa_txt'] = f"{lote['caixa_op']}/{total_cx_op}"
        lote['cor_tam_caixa_txt'] = f"{lote['caixa_ct']}/{total_cx_ct}"

    view_obj.context.update({
        'data': data,
    })

    return True
