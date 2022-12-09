import operator
from pprint import pprint

from utils.functions.dict import dict_get_none
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lms

__all__ = ['query']

_DICT_TIPO_PROGRAMACAO = {
    None: {
        None: "Desconhecido",
        'tpl': '{k}-{v}',
    },
    0: "Enfestos/Marcações",
    1: "Quantidade peças",
    2: "Para peça de peça",
    3: "Qtd. peças por grade de tamanho",
    4: "Qtd. peças/percentual",
    5: "Qtd. peças - Planej. de Corte",
    6: "Enfestos/Marcações",
}



def query(
    cursor,
    empresa=1,
    pedido=None,
):

    filtra_pedido = lms(f"""\
        AND op.PEDIDO_VENDA = '{pedido}'
    """) if pedido else ''

    sql = lms(f"""\
        SELECT 
          op.ORDEM_PRODUCAO OP
        , op.DEPOSITO_ENTRADA DEP
        , op.COD_CANCELAMENTO COD_CANC
        , canc.DESCRICAO DESCR_CANC
        , op.DT_CANCELAMENTO DT_CANC
        , op.REFERENCIA_PECA REF
        , r.DESCR_REFERENCIA REF_DESCR
        , r.COLECAO COD_COLECAO
        , col.DESCR_COLECAO
        , op.ALTERNATIVA_PECA ALT
        , op.QTDE_PROGRAMADA QTD
        , op.DATA_ENTRADA_CORTE DT_CORTE
        , op.ORDEM_ORIGEM OP_ORIGEM
        , op.ORDEM_PRINCIPAL OP_PRINC
        , op.ORDEM_ASSOCIADA OP_ASSOC
        , op.OBSERVACAO OBS
        , op.OBSERVACAO2 OBS2
        , op.TIPO_PROGRAMACAO TIPO_PROGR
        --, op.*
        FROM PCPC_020 op
        JOIN basi_030 r
          ON r.REFERENCIA = op.REFERENCIA_PECA
        LEFT JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        LEFT JOIN pcpt_050 canc
          ON canc.COD_CANCELAMENTO = op.COD_CANCELAMENTO
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
    """)

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        cod_canc = row['cod_canc']
        descr_canc = row['descr_canc']
        row['canc'] = f"{cod_canc}-{descr_canc}" if cod_canc else '-'

        row['tipo_progr_descr'] = dict_get_none(
            _DICT_TIPO_PROGRAMACAO,
            row['tipo_progr'],
        )

        cod_colecao = row['cod_colecao']
        descr_colecao = row['descr_colecao']
        row['colecao'] = f"{cod_colecao}-{descr_colecao}" if cod_colecao else '-'

        if row['ref'] < 'A0000':
            row['tipo_ref'] = 'PA'
            row['ordem_ref'] = 1
        elif row['ref'] < 'B0000':
            row['tipo_ref'] = 'PG'
            row['ordem_ref'] = 2
        elif row['ref'] < 'C0000':
            row['tipo_ref'] = 'PB'
            row['ordem_ref'] = 2
        elif row['ref'].startswith('F'):
            row['tipo_ref'] = 'MP'
            row['ordem_ref'] = 4
        elif row['ref'].startswith('Z'):
            row['tipo_ref'] = 'DESMONTE'
            row['ordem_ref'] = 1
        else:
            row['tipo_ref'] = 'MD'
            row['ordem_ref'] = 3

    dados.sort(key=operator.itemgetter('ordem_ref', 'ref'))

    return dados
