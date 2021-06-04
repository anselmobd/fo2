from pprint import pprint

import comercial.models
import produto.models
import produto.queries
from comercial.views.estoque import grade_meta_estoque

import lotes.views.a_produzir


def grade_meta_giro(meta, lead, show_distrib=True):
    meta_giro = round(
        meta.venda_mensal / 30 * lead)

    grade = {}
    grade['headers'] = ['Cor/Tamanho']
    grade['fields'] = ['cor']

    meta_tamanhos = comercial.models.MetaEstoqueTamanho.objects.filter(
        meta=meta).order_by('ordem')
    meta_grade_tamanhos = {}
    tot_tam = 0
    qtd_por_tam = {}
    style = ["text-align: left;"] 
    for tamanho in meta_tamanhos:
        if tamanho.quantidade != 0:
            if show_distrib:
                grade['headers'].append(
                    '{}({})'.format(tamanho.tamanho, tamanho.quantidade))
            else:
                grade['headers'].append(tamanho.tamanho)
            grade['fields'].append(tamanho.tamanho)
            meta_grade_tamanhos[tamanho.tamanho] = tamanho.quantidade
            tot_tam += tamanho.quantidade
            qtd_por_tam[tamanho.tamanho] = 0
            style.append('text-align: right;')
    style.append('text-align: right; font-weight: bold;')
    grade['style'] = dict(enumerate(style, start=1))

    resto = meta_giro % tot_tam
    if resto != 0:
        meta_giro = meta_giro + tot_tam - resto

    grade['headers'].append('Total')
    grade['fields'].append('total')

    tot_packs = meta_giro / tot_tam

    meta_cores = comercial.models.MetaEstoqueCor.objects.filter(
        meta=meta).order_by('cor')
    tot_cor = 0
    for cor in meta_cores:
        tot_cor += cor.quantidade

    grade['data'] = []
    meta_giro = 0
    for cor in meta_cores:
        if cor.quantidade != 0:
            if show_distrib:
                linha = {
                    'cor': '{}({})'.format(cor.cor, cor.quantidade),
                }
            else:
                linha = {
                    'cor': cor.cor,
                }
            cor_packs = round(
                tot_packs / tot_cor * cor.quantidade)
            for meta_tam in meta_grade_tamanhos:
                qtd_cor_tam = cor_packs * meta_grade_tamanhos[meta_tam]
                linha.update({
                    meta_tam: round(qtd_cor_tam),
                })
                qtd_por_tam[meta_tam] += qtd_cor_tam
            linha['total'] = cor_packs * tot_tam
            meta_giro += linha['total']
            grade['data'].append(linha)

    grade['meta_giro'] = meta_giro
    grade['data'].append({
        'cor': 'Total',
        **qtd_por_tam,
        'total': meta_giro,
        '|STYLE': 'font-weight: bold;',
    })
    return grade


def calculaMetaGiroMetas(cursor, metas):
    metas_list = []
    for meta in metas:
        meta_dict = meta.__dict__
        metas_list.append(meta_dict)

        lead = produto.queries.lead_de_modelo(
            cursor, meta_dict['modelo'])

        grade = grade_meta_giro(meta, lead)

        meta_dict['lead'] = lead
        meta_dict['giro'] = grade['meta_giro']

        if meta.meta_giro != meta_dict['giro']:
            meta.meta_giro = meta_dict['giro']
            meta.save()

        meta_dict['grade'] = grade
    return metas_list


def calculaMetaTotalMetas(cursor, metas):
    metas_list = []
    total = 0
    for meta in metas:
        lead = produto.queries.lead_de_modelo(cursor, meta.modelo)
        qtd = 0

        ggrade = grade_meta_giro(meta, lead, show_distrib=False)
        qtd += ggrade['meta_giro']

        egrade = grade_meta_estoque(meta)
        qtd += egrade['meta_estoque']

        total += qtd

        grade = lotes.views.a_produzir.soma_grades(ggrade, egrade)

        metas_list.append({
            'modelo': meta.modelo,
            'qtd': qtd,
            'grade': grade,
        })
    return metas_list, total
