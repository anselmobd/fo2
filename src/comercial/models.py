from fo2.models import rows_to_dict_list, cursorF1


def ficha_cliente(cnpj9, cnpj4):
    cursor = cursorF1()
    cliente = "{:08d}{:04d}".format(int(cnpj9), int(cnpj4))
    sql = """
        SELECT
          c.C_CGC CNPJ
        , c.C_RSOC CLIENTE
        , d.D_DUPNUM DUPLICATA
        , d.D_STAT STAT
        , d.D_PEDNUM PEDIDO
        , d.D_DFAT EMISSAO
        , d.D_DVENCORI VENC_ORI
        , d.D_DVENC VENCIMENTO
        , CASE WHEN mod(ord(d.D_AUX), 2) = 1
          THEN 'P'
          ELSE ' '
          END PRORROGADO
        , CASE WHEN d.D_VPAGO = 0 AND d.D_DVENC < 'NOW'
          THEN d.D_VALOR
          ELSE d.D_VALOR*(1-(d.D_DESC/100))
          END VALOR
        , d.D_QTD QUANT
        , d.D_QTDFAT QUANT_FAT
        , d.D_DPAGO DATA_PAGO
        , d.D_VPAGO VALOR_PAGO
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0 -- ''
            ELSE
              d.D_VPAGO - d.D_VALOR
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0 -- ''
            WHEN d.D_VPAGO <> 0 THEN
              d.D_VPAGO - d.D_VALOR
            ELSE
              d.D_VALOR
              * (d.D_JUROS * ((cast('NOW' AS DATE) - d.D_DVENC)
                              / 3000.0000))
            END
          END JUROS
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0
            ELSE
              d.D_DPAGO - d.D_DVENC
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0
            ELSE
              cast('NOW' AS DATE) - d.D_DVENC
            END
          END ATRASO
        , d.D_OP OP
        , d.D_BANCO BANCO
        , d.D_DESCONTO DESCONTO
        , d.D_OBS OBSERVACAO
        FROM DIS_DUP d
        LEFT JOIN DIS_CLI c
          ON c.C_CGC = d.D_CGC
        WHERE d.D_CGC STARTING WITH ?
          AND D.D_STAT >= '0' -- nao canceladas
          AND d.D_CODFIS IN ( '5101', '6101', '6107', '6109'
                            , '5124', '6124', '5125', '6125') -- cpof de venda
        ORDER BY
          d.D_DUPNUM
    """
    cursor.execute(sql, [cliente])
    return rows_to_dict_list(cursor)
