from pprint import pprint

from systextil.queries.base import SQuery, MountQuery


def roteiro_sem_sequencia():
    return SQuery(MountQuery(
        fields=[
          'r.GRUPO_ESTRUTURA REF',
          'r.SUBGRU_ESTRUTURA TAM',
          'r.ITEM_ESTRUTURA COR',
          'r.NUMERO_ALTERNATI ALT',
          'r.NUMERO_ROTEIRO ROT',
        ],
        table='MQOP_050 r',
        where=[
            'r.NIVEL_ESTRUTURA = 1',
            'r.SEQUENCIA_ESTAGIO = 0',
        ],
        group_all_fields=True,
        order_all_fields=True,
    )).debug_execute()
    return SQuery("""
        SELECT
          r.GRUPO_ESTRUTURA REF
        , r.SUBGRU_ESTRUTURA TAM
        , r.ITEM_ESTRUTURA COR
        , r.NUMERO_ALTERNATI ALT
        , r.NUMERO_ROTEIRO ROT
        FROM MQOP_050 r 
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.SEQUENCIA_ESTAGIO = 0
        GROUP BY 
          r.GRUPO_ESTRUTURA
        , r.SUBGRU_ESTRUTURA 
        , r.ITEM_ESTRUTURA
        , r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
        ORDER BY 
          r.GRUPO_ESTRUTURA
        , r.SUBGRU_ESTRUTURA 
        , r.ITEM_ESTRUTURA
        , r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
    """).debug_execute()
