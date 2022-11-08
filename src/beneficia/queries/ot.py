import datetime
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.dict import dict_get_none


def busca_ot(cursor, ot=None):

    filtra_ot = f"""--
        AND t.ORDEM_AGRUPAMENTO = {ot}
    """ if ot else ''

    sql = f'''
        SELECT 
          t.ORDEM_AGRUPAMENTO OT
        , t.ORDEM_PRODUCAO OB
        , t.TIPO_ORDEM
        , t.RELACAO_BANHO 
        , t.VOLUME_BANHO 
        , t.GRUPO_MAQUINA GRUP_MAQ
        , t.SUBGRUPO_MAQUINA SUB_MAQ 
        , t.NUMERO_MAQUINA NUM_MAQ
        , t.SITUACAO
        , t.SITUACAO_RECEITA
        FROM PCPB_100 t -- OT
        WHERE 1=1
          {filtra_ot} -- filtra_ot
        ORDER BY
          t.ORDEM_AGRUPAMENTO
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    tipo_ordem = {
        None: {
            None: "Desconhecida",
            'tpl': '{k}-{v}',
        },
        '1': "Ordem tingimento",
        '2': "Ordem lavação",
        '3': "Ordem estamparia",
        '4': "Ordem reprocesso",
        '5': "Ordem retração",
        '6': "Processo contínuo",
        '7': "Ordem revestimento",
        '': '',
    }

    situacao = {
        None: {
            None: "Desconhecida",
            'tpl': '{k}-{v}',
        },
        '0': "Digitada",
        '1': "Impressa",
        '2': "A produzir",
        '3': "Em producao",
        '4': "Produzida",
        '5': "Ordem alterada na producao",
        '': '',
    }

    situacao_receita = {
        None: {
            None: "Desconhecida",
            'tpl': '{k}-{v}',
        },
        '0': "A imprimir",
        '1': "Impressa",
        '2': "Revisada/confirmada",
        '3': "Teste de desenvolvimento",
        '4': "Estoque insuficiente",
        '5': "Exportar - link outro software",
        '6': "Exportado - link outro software",
        '7': "Bloqueada manualmente",
        '': '',
    }

    for row in dados:
        row['tipo'] = dict_get_none(tipo_ordem, row['tipo_ordem'])
        grup_maq = row['grup_maq']
        sub_maq = row['sub_maq']
        num_maq = row['num_maq']
        row['maq'] = f"{grup_maq} {sub_maq} {num_maq:05}"
        row['sit'] = dict_get_none(situacao, row['situacao'])
        row['sit_receita'] = dict_get_none(
            situacao_receita, row['situacao_receita'])

    return dados
