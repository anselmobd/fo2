from pprint import pprint

__all__ = ['nf_situacao_descr']


def nf_situacao_descr(situacao, status):
    situacao_descr = {
        0: 'CALCULADA',
        1: {
            100: 'ATIVA',  # 'EMITIDA',
            None: 'REJEITADA',
        },
        2: 'CANCELADA',
        3: 'VERIFICAR',
        4: 'CONFIRMADA',
        5: 'INCOMPLETA',
        6: 'INCOMPLETA',  # porém foi calculada a duplicata
    }

    try:
        descr = situacao_descr[situacao]
    except KeyError:
        descr = 'desconhecido'
    if isinstance(descr, dict):
        try:
            descr = situacao_descr[situacao][status]
        except KeyError:
            descr = situacao_descr[situacao][None]
    return descr.capitalize()
