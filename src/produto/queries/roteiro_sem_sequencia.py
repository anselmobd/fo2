from pprint import pprint

from systextil.queries.base import SMountQuery


def roteiro_sem_sequencia():
    return SMountQuery(
        fields=[
          "r.GRUPO_ESTRUTURA REF",
          "r.SUBGRU_ESTRUTURA TAM",
          "r.ITEM_ESTRUTURA COR",
          "r.NUMERO_ALTERNATI ALT",
          "r.NUMERO_ROTEIRO ROT",
        ],
        table="MQOP_050 r",
        where=[
            "r.NIVEL_ESTRUTURA = 1",
            "r.SEQUENCIA_ESTAGIO = 0",
        ],
        group_all_fields=True,
        order_all_fields=True,
    ).oquery.debug_execute()
