from pprint import pprint

from systextil.queries.base import SMountQuery


def query_pallete():
    return SMountQuery(
        fields=[
          "co.COD_CONTAINER palete",
        ],
        table="ENDR_012 co",
        where=[
            "co.COD_CONTAINER LIKE 'PLT%'",
        ],
        order_all_fields=True,
    ).oquery.debug_execute()
