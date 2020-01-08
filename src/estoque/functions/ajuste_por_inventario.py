import datetime
from pprint import pprint

from django.db import connections

from estoque import queries
from estoque.classes import TransacoesDeAjuste
from estoque.functions import transfo2_num_doc


def ajuste_por_inventario(
    dep,
    ref,
    tam,
    cor,
    qtd,
    data,
    hora,
    force,
):
    '''
        Recebe qtd, data e hora do inventário
        Calcula ajuste necessário.
        Devolve sucesso, mensagem e mais informações.
    '''
    infos = {}

    infos['dep'] = dep
    if dep not in ['101', '102', '231']:
        return False, 'Depósito inválido', infos

    cursor = connections['so'].cursor()
    infos['ref'] = ref
    infos['tam'] = tam
    infos['cor'] = cor
    produto = queries.get_preco_medio_ref_cor_tam(cursor, ref, cor, tam)
    try:
        preco_medio = produto[0]['preco_medio']
    except Exception:
        return False, 'Referência/Cor/Tamanho não encontrada', infos

    estoque_list = queries.get_estoque_dep_ref_cor_tam(
        cursor, dep, ref, cor, tam)
    if len(estoque_list) == 0:
        estoque = 0
    else:
        estoque = estoque_list[0]['estoque']
    infos['estoque'] = estoque

    dt = datetime.datetime.strptime(data, '%Y-%m-%d').date()
    infos['data'] = dt

    tm = datetime.datetime.strptime(hora, '%Hh%M').time()
    infos['hora'] = tm

    movimento = 0
    movimento_list = queries.get_transfo2_deposito_ref(
        cursor, dep, ref, cor, tam, tipo='s', data=dt, hora=tm)
    if len(movimento_list) != 0:
        for row in movimento_list:
            if row['es'] == 'E':
                movimento += row['qtd']
            elif row['es'] == 'S':
                movimento -= row['qtd']
    infos['movimento'] = movimento

    infos['qtd'] = qtd
    ajuste = round(qtd - estoque + movimento)
    sinal = 1 if ajuste > 0 else -1
    ajuste *= sinal
    infos['ajuste'] = ajuste
    if ajuste == 0:
        return True, 'Nada a fazer', infos

    transacoes = TransacoesDeAjuste()
    trans, es, descr = transacoes.get(sinal)
    infos['trans'] = trans
    infos['es'] = es
    infos['descr'] = descr

    num_doc = transfo2_num_doc(dt, tm)
    infos['num_doc'] = num_doc

    infos['force'] = force

    if not force:
        data = queries.get_transfo2(
            cursor,
            dep,
            num_doc,
            ref,
            cor,
            tam,
        )
        if len(data) != 0:
            return (
                True,
                'Já existe ajuste desse item nesse depósito com esse numdoc',
                infos)

    if queries.insert_transacao_ajuste(
            cursor,
            dep,
            ref,
            tam,
            cor,
            num_doc,
            trans,
            es,
            ajuste,
            preco_medio
            ):
        return True, 'Executado o ajuste por inventário no Systêxtil', infos
    return False, 'Erro durante inserção da transação no Systêxtil', infos
