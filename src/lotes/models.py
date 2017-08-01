from django.db import models

from fo2.models import rows_to_dict_list


class ModeloTermica(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20, null=True, blank=True,
        verbose_name='código')
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='nome')
    modelo = models.TextField(
        null=True, blank=True,
        verbose_name='modelo')
    campos = models.TextField(
        null=True, blank=True,
        verbose_name='campos')

    class Meta:
        db_table = "fo2_lot_modelo_termica"
        verbose_name = "modelo de etiqueta térmica"
        verbose_name_plural = "modelos de etiqueta térmica"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo and self.codigo.upper()
        super(ModeloTermica, self).save(*args, **kwargs)


class ImpressoraTermica(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    class Meta:
        db_table = "fo2_lot_impr_termica"
        verbose_name = "impressora térmica"
        verbose_name_plural = "impressoras térmicas"


def existe_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT DISTINCT
          l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


def posicao_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          el.CODIGO_ESTAGIO
        , el.DESCRICAO DESCRICAO_ESTAGIO
        FROM (
        SELECT
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND l.QTDE_EM_PRODUCAO_PACOTE <> 0
        UNION
        SELECT
          0
        , 'FINALIZADO'
        from dual
        ORDER BY
          1 DESC
        ) el
        WHERE rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


def posicao_periodo_oc(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , TO_CHAR(p.DATA_INI_PERIODO, 'DD/MM/YYYY') INI
        , TO_CHAR(p.DATA_FIM_PERIODO - 1, 'DD/MM/YYYY') FIM
        , %s OC
        FROM PCPC_010 p
        WHERE p.AREA_PERIODO = 1
          AND p.PERIODO_PRODUCAO = %s
    '''
    cursor.execute(sql, [ordem_confeccao, periodo])
    return rows_to_dict_list(cursor)


def posicao_get_op(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        , l.SITUACAO_ORDEM SITU
        , TO_CHAR(o.DATA_HORA, 'DD/MM/YYYY HH24:MI') DT
        FROM PCPC_040 l
        JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = l.NOME_PROGRAMA_CRIACAO
         AND p.LOCALE = 'pt_BR'
        LEFT JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) != 0:
        situacoes = {
            1: 'ORDEM CONF. GERADA',
            2: 'ORDENS EM PRODUCAO',
            9: 'ORDEM CANCELADA',
        }
        for row in data:
            if row['SITU'] in situacoes:
                row['SITU'] = '{} - {}'.format(
                    row['SITU'], situacoes[row['SITU']])
    return data


def posicao_get_item(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.PROCONF_NIVEL99
          || '.' || l.PROCONF_GRUPO
          || '.' || l.PROCONF_SUBGRUPO
          || '.' || l.PROCONF_ITEM ITEM
        , i.NARRATIVA NARR
        , l.QTDE_PECAS_PROG QTDE
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , case
          when l.PROCONF_GRUPO <= '99999' then 'PA'
          when l.PROCONF_GRUPO <= 'A9999' then 'PG'
          else 'MD'
          end TIPO
        FROM PCPC_040 l
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND i.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND i.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
         AND i.ITEM_ESTRUTURA = l.PROCONF_ITEM
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


def posicao_estagios(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.QTDE_PROGRAMADA Q_PROG
        , l.QTDE_PECAS_PROG Q_P
        , l.QTDE_A_PRODUZIR_PACOTE Q_AP
        , l.QTDE_EM_PRODUCAO_PACOTE Q_EP
        , l.QTDE_PECAS_PROD Q_PROD
        , l.QTDE_PECAS_2A Q_2A
        , l.QTDE_PERDAS Q_PERDA
        , l.CODIGO_FAMILIA FAMI
        , l.NUMERO_ORDEM OS
        , coalesce(d.USUARIO_SYSTEXTIL, ' ') USU
        , TO_CHAR(d.DATA_INSERCAO, 'DD/MM/YYYY HH24:MI') DT
        , coalesce(d.PROCESSO_SYSTEXTIL || ' - ' || p.DESCRICAO, ' ') PRG
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        LEFT JOIN PCPC_045 d
          ON d.PCPC040_PERCONF = l.PERIODO_PRODUCAO
         AND d.PCPC040_ORDCONF = l.ORDEM_CONFECCAO
         AND d.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = d.PROCESSO_SYSTEXTIL
         AND p.LOCALE = 'pt_BR'
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        , d.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    for row in data:
        if row['DT'] is None:
            row['DT'] = ''
    return data


def op_inform(cursor, op):
    # informações gerais
    sql = '''
        SELECT
          case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'A9999' then 'PG'
          else 'MD'
          end TIPO_REF
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0 THEN 'Filha de'
          WHEN ofi.ORDEM_PRODUCAO IS NOT NULL THEN 'Mãe de'
          ELSE 'Avulsa'
          END TIPO_OP
        , coalesce( ofi.ORDEM_PRODUCAO, o.ORDEM_PRINCIPAL ) OP_REL
        , o.SITUACAO ||
          CASE
          WHEN o.SITUACAO = 2 THEN '-Ordem conf. gerada'
          WHEN o.SITUACAO = 4 THEN '-Ordens em produção'
          WHEN o.SITUACAO = 9 THEN '-Ordem cancelada'
          ELSE ' '
          END SITUACAO
        , o.COD_CANCELAMENTO ||
          CASE
          WHEN o.COD_CANCELAMENTO = 0 THEN ''
          ELSE '-' || c.DESCRICAO
          END CANCELAMENTO
        , o.ALTERNATIVA_PECA ALTERNATIVA
        , o.ROTEIRO_PECA ROTEIRO
        , o.REFERENCIA_PECA REF
        , ( SELECT
              COUNT( DISTINCT l.ORDEM_CONFECCAO )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) LOTES
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          ) QTD
        FROM PCPC_020 o
        JOIN pcpt_050 c
          ON c.COD_CANCELAMENTO = o.COD_CANCELAMENTO
        LEFT JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.ORDEM_PRODUCAO
        WHERE o.ORDEM_PRODUCAO = %s
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          ll.EST
        , (SELECT
              cast( SUM( lp.QTDE_PECAS_PROD ) / SUM( lp.QTDE_PECAS_PROG ) * 100
                    AS NUMERIC(10,2) )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) PERC
        , (SELECT
              SUM( lp.QTDE_PECAS_PROD )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) PROD
        FROM
        (
        SELECT DISTINCT
          l.ORDEM_PRODUCAO
        , l.SEQ_OPERACAO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        FROM pcpc_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.ORDEM_PRODUCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        ) ll
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def get_lotes(cursor, op='', os=''):
    # Lotes ordenados por OP + OS + referência + estágio
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , CASE WHEN dos.NUMERO_ORDEM IS NULL
          THEN '0'
          ELSE l.NUMERO_ORDEM || ' (' || eos.DESCRICAO || ')'
          END OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , COALESCE(
          ( SELECT
              LISTAGG(le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO, ' & ')
              WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
            FROM PCPC_040 le
            JOIN MQOP_005 ed
              ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
            WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
              AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
              AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
          )
          , 'FINALIZADO'
          ) EST
        , l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        , l.QTDE_PROGRAMADA QTD
        FROM (
          SELECT
            os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          , os.ORDEM_PRODUCAO
          , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
          , max( os.QTDE_PROGRAMADA ) QTDE_PROGRAMADA
          FROM PCPC_040 os
          WHERE 1=1
            AND (os.ORDEM_PRODUCAO = %s or %s IS NULL)
            AND (os.NUMERO_ORDEM = %s or %s IS NULL)
          GROUP BY
            os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          , os.ORDEM_PRODUCAO
        ) l
        LEFT JOIN PCPC_040 dos
          ON l.NUMERO_ORDEM <> 0
         AND dos.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
         AND dos.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
         AND dos.NUMERO_ORDEM = l.NUMERO_ORDEM
        LEFT JOIN MQOP_005 eos
          ON eos.CODIGO_ESTAGIO = dos.CODIGO_ESTAGIO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        ORDER BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
    '''
    cursor.execute(sql, [op, op, os, os])
    return rows_to_dict_list(cursor)


def op_lotes(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, op=op)


def op_ref_estagio(cursor, op):
    # Totais por referência + estágio
    sql = '''
        SELECT
          lote.REF
        , lote.TAM
        , lote.COR
        , lote.EST
        , count(*) LOTES
        , sum(lote.QTD) QTD
        FROM (
          SELECT
            l.PROCONF_GRUPO REF
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          , COALESCE(
              ( SELECT
                  LISTAGG(le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO, ' & ')
                  WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
                FROM PCPC_040 le
                JOIN MQOP_005 ed
                  ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
                WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                  AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                  AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
              )
            , 'FINALIZADO'
            ) EST
          , l.QTDE_PROGRAMADA QTD
          FROM (
            SELECT
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
            , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
            , max( os.QTDE_PROGRAMADA ) QTDE_PROGRAMADA
            FROM PCPC_040 os
            WHERE os.ORDEM_PRODUCAO = %s
            GROUP BY
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
          ) l
        ) lote
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = lote.TAM
        GROUP BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.TAM
        , lote.EST
        ORDER BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.EST
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_os(cursor, op):
    # OSs da OP
    sql = """
        SELECT
          l.NUMERO_ORDEM OS
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(l.QTDE_PECAS_PROG) QTD
        FROM pcpc_040 l
        WHERE l.ORDEM_PRODUCAO = %s
          AND l.NUMERO_ORDEM <> 0
        GROUP BY
          l.NUMERO_ORDEM
        ORDER BY
          l.NUMERO_ORDEM
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_os_ref(cursor, op):
    # Totais por OS + referência
    sql = """
        SELECT
          l.NUMERO_ORDEM OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , count( l.ORDEM_CONFECCAO ) LOTES
        , SUM (
            ( SELECT
                q.QTDE_PROGRAMADA
              FROM PCPC_040 q
              WHERE q.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                AND q.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND q.SEQ_OPERACAO = (
                  SELECT
                    min(o.SEQ_OPERACAO)
                  FROM PCPC_040 o
                  WHERE o.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                    AND o.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                )
            )
          ) QTD
        FROM (
          SELECT DISTINCT
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          FROM PCPC_040 os
          WHERE os.ORDEM_PRODUCAO = %s
          GROUP BY
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
        ) l
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        GROUP BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
        ORDER BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def get_os(cursor, os='', op='', periodo='', oc=''):
    # Informações sobre OS
    sql = """
        SELECT DISTINCT
          os.NUMERO_ORDEM OS
        , os.CODIGO_SERVICO || '-' || s.DESC_TERCEIRO SERV
        , os.CGCTERC_FORNE9 CNPJ9
        , os.CGCTERC_FORNE4 CNPJ4
        , os.CGCTERC_FORNE2 CNPJ2
        , f.NOME_FANTASIA NOME
        , CASE os.SITUACAO_ORDEM
          WHEN 1 THEN '1-Aberta'
          WHEN 2 THEN '2-Em Processo'
          WHEN 3 THEN '3-Baixa Parcial'
          WHEN 4 THEN '4-Baixa Total'
          ELSE '-'
          END SITUACAO
        , os.COD_CANC_ORDEM || '-' || c.DESCR_CANC_ORDEM CANC
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(l.QTDE_PECAS_PROG) QTD
        FROM OBRF_080 os
        JOIN OBRF_070 s
          ON s.CODIGO_TERCEIRO = os.CODIGO_SERVICO
        JOIN SUPR_010 f
          ON f.FORNECEDOR9 = os.CGCTERC_FORNE9
         AND f.FORNECEDOR4 = os.CGCTERC_FORNE4
        JOIN OBRF_087 c
          ON c.COD_CANC_ORDEM = os.COD_CANC_ORDEM
        JOIN pcpc_040 l
          ON l.NUMERO_ORDEM = os.NUMERO_ORDEM
        WHERE 1=1
          AND (os.NUMERO_ORDEM = %s or %s IS NULL)
          AND (l.ORDEM_PRODUCAO = %s or %s IS NULL)
          AND (l.PERIODO_PRODUCAO = %s or %s IS NULL)
          AND (l.ORDEM_CONFECCAO = %s or %s IS NULL)
          AND l.NUMERO_ORDEM <> 0
        GROUP BY
          os.NUMERO_ORDEM
        , os.CODIGO_SERVICO
        , s.DESC_TERCEIRO
        , os.CGCTERC_FORNE9
        , os.CGCTERC_FORNE4
        , os.CGCTERC_FORNE2
        , f.NOME_FANTASIA
        , os.SITUACAO_ORDEM
        , os.COD_CANC_ORDEM
        , c.DESCR_CANC_ORDEM
        ORDER BY
          os.NUMERO_ORDEM
    """
    cursor.execute(sql, [os, os, op, op, periodo, periodo, oc, oc])
    return rows_to_dict_list(cursor)


def os_inform(cursor, os):
    # Informações sobre OS
    return get_os(cursor, os=os)


def os_op(cursor, os):
    # Totais por OP
    sql = """
        SELECT
          l.ORDEM_PRODUCAO OP
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(l.QTDE_PECAS_PROG) QTD
        FROM pcpc_040 l
        WHERE l.NUMERO_ORDEM = %s
        GROUP BY
          l.ORDEM_PRODUCAO
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)


def os_lotes(cursor, os):
    # Lotes ordenados por OP + referência + estágio
    return get_lotes(cursor, os=os)
