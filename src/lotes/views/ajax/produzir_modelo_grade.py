from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from lotes.queries.analise.produzir_grade_empenho import mount_produzir_grade_empenho

__all__ = ['produzir_modelo_grade']


def get_total(dados, grade, grade_alt=None):
    grades = [grade, grade_alt]
    for grd in grades:
        if grd:
            if grd in dados:
                for row in dados[grd]['data']:
                    if row['cor'] == 'Total':
                        return row['total']
    return -1


def produzir_modelo_grade(request, modelo):
    cursor = db_cursor_so(request)
    data = {
        'modelo': modelo,
    }

    try:
        dados_produzir = mount_produzir_grade_empenho(cursor, modelo)

        data['modelo'] = modelo
        data['meta_estoque'] = get_total(dados_produzir, 'gme')
        data['meta_giro'] = get_total(dados_produzir, 'gmg')
        data['meta'] = get_total(dados_produzir, 'gm')
        data['inventario'] = get_total(dados_produzir, 'ginv')
        data['op_andamento'] = get_total(dados_produzir, 'gopa_ncd')
        data['total_op'] = get_total(dados_produzir, 'gopa')
        data['empenho'] = get_total(dados_produzir, 'gsol')
        data['pedido'] = get_total(dados_produzir, 'gped')
        data['livres'] = get_total(dados_produzir, 'gopp')
        data['excesso'] = get_total(dados_produzir, 'gex')
        data['a_produzir'] = get_total(dados_produzir, 'gap')
        data['a_produzir_tam'] = get_total(dados_produzir, 'glm', 'gap')
        data['a_produzir_cor'] = get_total(dados_produzir, 'glc', 'gap')

    except Exception as e:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao quantidades de modelo',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
    })
    return JsonResponse(data, safe=False)
