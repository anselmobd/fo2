from pprint import pprint

from django.conf import settings

import lotes.models


def lista_lotes_em(endereco):
    show_qtd_end = settings.DESLIGANDO_CD_FASE < 1
    context = {}
    lotes_no_local = lotes.models.Lote.objects.filter(
        local=endereco).order_by(
            '-local_at'
            ).values(
                'op', 'lote', 'qtd_produzir', 'qtd', 'conserto',
                'referencia', 'cor', 'tamanho',
                'local_at', 'local_usuario__username')
    if lotes_no_local:
        q_itens = 0
        q_itens_end = 0
        for row in lotes_no_local:
            row['qtd_livre'] = row['qtd'] - row['conserto']
            q_itens += row['qtd']
            q_itens_end += row['conserto']
        context.update({
            'q_lotes': len(lotes_no_local),
            'q_itens': q_itens,
            'q_itens_end': q_itens_end,
            'headers': ['Bipado em', 'Bipado por',
                        'Lote', 'Q.Ori.', 'Q.Est.', 'Q.Livre', 'Q.End.',
                        'Ref.', 'Cor', 'Tam.', 'OP'],
            'fields': ['local_at', 'local_usuario__username',
                       'lote', 'qtd_produzir', 'qtd', 'qtd_livre', 'conserto',
                       'referencia', 'cor', 'tamanho', 'op'],
            'data': lotes_no_local,
            })
        if not show_qtd_end:
            context['q_itens_end'] = q_itens
            context['headers'].remove('Q.Livre')
            context['headers'].remove('Q.End.')
            context['fields'].remove('qtd_livre')
            context['fields'].remove('conserto')
       
    return context
