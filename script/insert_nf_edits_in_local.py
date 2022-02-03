import sys
from pprint import pprint

import db_password
from inventario import Postgre


def prod_get_nf():
    sql = f"""
        select 
          nf.*
        from fo2_fat_nf nf
        order by
          nf.numero
    """
    return prod.execute(sql)


def monta_update(
    numero=None, confirmada=None, saida=None, 
    entrega=None, observacao=None, **kwargs
):
    saida = f"'{saida}'" if saida else "NULL"
    entrega = f"'{entrega}'" if entrega else "NULL"
    if observacao:
        observacao = observacao.replace("'", "''")
        observacao = f"'{observacao}'"
    else:
        observacao = "NULL"

    sql = f"""
        update fo2_fat_nf
        set
          confirmada = {confirmada}
        , saida = {saida}
        , entrega = {entrega}
        , observacao = {observacao}
        where numero = {numero}
    """
    return sql


def gera_inserts_nf(ini, quant):
    ini -= 1
    dados_prod = prod_get_nf()
    print('len_dados_prod=', len(dados_prod['data']))
    for idx, dado in enumerate(dados_prod['data']):
        if idx < ini:
            continue
        row = dict(zip(dados_prod['keys'], dado))
        print(row['numero'])
        update_sql = monta_update(**row)
        # print(update_sql)
        dev.execute(update_sql)
        if idx == (ini + quant - 1):
            break


if __name__ == '__main__':
    try:
        ini = int(sys.argv[1])
        quant = int(sys.argv[2])
    except Exception:
        print(f"syntax: {sys.argv[0]} ini quant")
        raise SystemExit
        
    prod = Postgre(
        username="tussor_fo2",
        password=db_password.DBPASS_POSTGRE,
        hostname="127.0.0.1",
        port=25432,
        database="tussor_fo2_production",
    )
    prod.connect()
    
    dev = Postgre(
        username="tussor_dev_fo2",
        password=db_password.DBPASS,
        hostname="localhost",
        port=5434,
        database="tussor_dev_fo2_production",
    )
    dev.connect()

    gera_inserts_nf(ini, quant)