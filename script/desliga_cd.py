from pprint import pprint

import db_password
from inventario import Oracle, Postgre


def syst_lotes_cons(op=None):
    filtro_op = f"AND l.ORDEM_PRODUCAO < {op}" if op else ''
    sql = f"""
        SELECT DISTINCT 
          l.PERIODO_PRODUCAO periodo
        , l.ORDEM_CONFECCAO oc
        , l.CODIGO_ESTAGIO est
        , l.QTDE_CONSERTO qtd
        FROM PCPC_040 l
        WHERE 1=1
          {filtro_op} -- filtro_op
        AND l.QTDE_CONSERTO <> 0
        ORDER BY
          l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
    """
    return ora.execute(sql)


def fo2_lotes_cons(op=None):
    filtro_op = f"AND l.op < {op}" if op else ''
    sql = f"""
        select distinct 
          l.lote 
        from fo2_cd_solicita_lote_qtd slq
        join fo2_cd_lote l
          on l.id = slq.lote_id 
        where slq.origin_id = 0
          {filtro_op} -- filtro_op
    """
    return pos.execute(sql)


def tira_conserto():
    op = None

    dados_fo2 = fo2_lotes_cons(op)
    lotes_fo2 = [row[0] for row in dados_fo2['data']]
    # pprint(lotes_fo2[:10])

    lotes_syst = syst_lotes_cons(op)
    # pprint(lotes_syst['keys'])
    print('len_lotes_com_conserto', len(lotes_syst['data']))

    tirar = []
    for dado in lotes_syst['data']:
        row = dict(zip(lotes_syst['keys'], dado))
        row['lote'] = f"{row['PERIODO']}{row['OC']:05}"
        if row['lote'] not in lotes_fo2:
            tirar.append(row['lote'])

    print('len_tirar=', len(tirar))
    pprint(tirar)


if __name__ == '__main__':
    ora = Oracle(
        username='systextil',
        password=db_password.DBPASS_SH,
        hostname='localhost',
        port=14521,
        servicename='db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        schema='SYSTEXTIL',
    )
    ora.connect()
    pos = Postgre()
    pos.connect()
    tira_conserto()