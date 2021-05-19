from pprint import pprint

import systextil.models

import lotes.models


def sync_regra_colecao():
    colecoes = systextil.models.Colecao.objects.exclude(
        colecao=0).order_by('colecao')

    regra_colecao = lotes.models.RegraColecao.objects.all(
        ).order_by('colecao')

    acoes = {}
    inter_col = colecoes.iterator()
    inter_regra = regra_colecao.iterator()
    walk = 'b'   # from, to, both
    while True:
        if walk in ['f', 'b']:
            try:
                col = next(inter_col)
            except StopIteration:
                col = None

        if walk in ['t', 'b']:
            try:
                rc = next(inter_regra)
            except StopIteration:
                rc = None

        if rc is None and col is None:
            break

        rec = {}
        acao_definida = False

        if rc is not None:
            if col is None or col.colecao > rc.colecao:
                acao_definida = True
                rec['status'] = 'd'
                rec['colecao'] = rc.colecao
                walk = 't'

        if not acao_definida:
            rec['colecao'] = col.colecao
            if rc is None or col.colecao < rc.colecao:
                acao_definida = True
                rec['status'] = 'i'
                walk = 'f'

        if not acao_definida:
            rec['status'] = 'u'
            walk = 'b'

        acoes[rec['colecao']] = rec

    for colecao in acoes:
        if acoes[colecao]['status'] == 'd':
            try:
                lotes.models.RegraColecao.objects.filter(colecao=colecao).delete()
            except lotes.models.RegraColecao.DoesNotExist:
                return 'Erro apagando regra de coleção'
            continue

        if acoes[colecao]['status'] == 'i':
            try:
                rc = lotes.models.RegraColecao()
                rc.colecao = colecao
                rc.save()
            except Exception:
                return 'Erro inserindo regra de coleção '

    return None
