from pprint import pprint

from django.urls import reverse

from utils.classes import Perf

import lotes.queries
from lotes.queries.op import op_inform_basico
from lotes.queries.lote import get_lotes


__all__ = ['data']


def data(cursor, op):
    p = Perf(id='lotes_em_caixa.data', on=False)
    result = {}
    # data_op = lotes.queries.op.op_inform(cursor, op, cached=False)
    data_op = op_inform_basico.query(cursor, op)
    p.prt('op_inform')
    if len(data_op) == 0:
        result.update({
            'msg_erro': 'OP não encontrada',
            'result': False,
        })
        return result

    row_op = data_op[0]
    if row_op['TIPO_REF'] not in ['MD', 'MP']:
        result.update({
            'msg_erro': 'Lotes agrupados em caixas é utilizado apenas para MD e MP',
            'result': False,
        })
        return result

    if row_op['COD_SITUACAO'] == 9:
        result.update({
            'msg_erro': 'OP cancelada!',
            'result': False,
        })
        return result

    result.update({
        'ref': row_op['REF'],
        'descr_ref': row_op['DESCR_REF'],
        'tipo_ref': row_op['TIPO_REF'],
        'colecao': row_op['COLECAO'],
    })

    # Lotes order 'r' = referência + cor + tamanho + OC
    data = get_lotes.get_imprime_lotes(cursor, op=op, order='r')
    p.prt('get_imprime_lotes')
    if len(data) == 0:
        result.update({
            'msg_erro': 'Lotes não encontrados',
            'result': False,
        })
        return result

    try:
        rc = lotes.models.RegraColecao.objects_referencia.get(
            colecao=data[0]['colecao'], referencia=result['ref'][0])
        result.update({
            'ini_ref': rc.referencia,
        })
    except lotes.models.RegraColecao.DoesNotExist:
        try:
            rc = lotes.models.RegraColecao.objects.get(
                colecao=data[0]['colecao'])
            result.update({
                'ini_ref': '',
            })
        except lotes.models.RegraColecao.DoesNotExist:
            result.update({
                'msg_erro': 'Regra de coleção e referência não encontrados',
            'result': False,
            })
            return result
    result.update({
        'lotes_caixa': rc.lotes_caixa,
    })

    caixa_op = 0
    cor_ant = '!!!!!!'
    tam_ant = '!!!!'
    for lote in data:
        lote['lote'] = f"{lote['periodo']}{lote['oc']:05}"
        lote['lote|LINK'] = reverse('producao:lote__get', args=[lote['lote']])
        lote['peso'] = " "
        
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

        lote['total_cx_op'] = total_cx_op
        lote['total_cx_ct'] = total_cx_ct
        lote['num_caixa_txt'] = f"{lote['caixa_op']}/{total_cx_op}"
        lote['cor_tam_caixa_txt'] = f"{lote['caixa_ct']}/{total_cx_ct}"

    # inicio - necessários para impressão de etiquetas
    for lote in data:
        lote['data_entrada_corte'] = row_op['DT_CORTE']
        lote['situacao'] = row_op['SITUACAO']
    # fim

    result.update({
        'data': data,
        'total_cx_op': total_cx_op,
        'result': True,
    })
    p.prt('fim')

    return result
