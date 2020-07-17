from pprint import pprint

import lotes.models


def lista_lotes_em(endereco):
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
            row['qtd_est'] = row['qtd'] + row['conserto']
            q_itens += row['qtd'] + row['conserto']
            q_itens_end += row['conserto']
        context.update({
            'q_lotes': len(lotes_no_local),
            'q_itens': q_itens,
            'q_itens_end': q_itens_end,
            'headers': ('Bipado em', 'Bipado por',
                        'Lote', 'Q.Ori.', 'Q.Está.', 'Q.Livre', 'Q.End.',
                        'Ref.', 'Cor', 'Tam.', 'OP'),
            'fields': ('local_at', 'local_usuario__username',
                       'lote', 'qtd_produzir', 'qtd_est', 'qtd', 'conserto',
                       'referencia', 'cor', 'tamanho', 'op'),
            'data': lotes_no_local,
            })
    return context
