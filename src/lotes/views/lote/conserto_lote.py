from pprint import pprint

from django.db import connections
from django.http import JsonResponse

from base.models import Colaborador
from geral.functions import request_user
from systextil.models import Usuario


def dict_conserto_lote(request, lote, estagio, in_out, qtd_a_mover):
    in_out = in_out.lower()
    data = {
        'lote': lote,
        'estagio': estagio,
        'in_out': in_out,
        'qtd_a_mover': qtd_a_mover,
    }

    if qtd_a_mover is None:
        qtd_a_mover = '0'

    user = request_user(request)
    if user is None:
        data.update({
            'error_level': 11,
            'msg': 'É necessário estar logado na intranet',
        })
        return data

    try:
        colab = Colaborador.objects.get(user=user)
    except Colaborador.DoesNotExist:
        data.update({
            'error_level': 12,
            'msg': 'É necessário estar configurada a tabela de colaborador',
        })
        return data

    try:
        usuario = Usuario.objects.get(
            usuario=colab.user.username.upper(),
            codigo_usuario=colab.matricula,
        )
    except Usuario.DoesNotExist:
        data.update({
            'error_level': 13,
            'msg': 'Usuário do systextil não encontrado',
        })
        return data

    if not user.has_perm('lotes.can_inventorize_lote'):
        data.update({
            'error_level': 14,
            'msg': 'Usuário sem direito de inventariar lote',
        })
        return data

    if not lote.isnumeric():
        data.update({
            'error_level': 21,
            'msg': 'Parâmetro lote com valor inválido',
        })
        return data

    if estagio != '63':
        data.update({
            'error_level': 22,
            'msg': 'Esta rotina só deve ser utilizada para o estágio 63',
        })
        return data

    if in_out not in ['in', 'out']:
        data.update({
            'error_level': 23,
            'msg': 'Parâmetro in_out com valor inválido',
        })
        return data

    if qtd_a_mover.isnumeric():
        qtd_a_mover = int(qtd_a_mover)
    else:
        data.update({
            'error_level': 24,
            'msg': 'Quantidade a mover com valor inválido',
        })
        return data

    with connections['so'].cursor() as cursor:

        if in_out == 'in':
            qtd_var = 'l.QTDE_DISPONIVEL_BAIXA'
        else:
            qtd_var = 'l.QTDE_CONSERTO'

        sql = f"""
            SELECT
              {qtd_var} QTD
            FROM PCPC_040 l
            WHERE l.PERIODO_PRODUCAO = {lote[:4]}
              AND l.ORDEM_CONFECCAO = {lote[4:]}
              AND l.CODIGO_ESTAGIO = {estagio}
        """

        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            data.update({
                'error_level': 1,
                'msg': f'Lote {lote} sem estágio {estagio}',
            })
            return data

        if row[0] <= 0:
            data.update({
                'error_level': 2,
                'msg': f'Lote {lote} sem quantidade a mover no '
                       f'estágio {estagio}',
            })
            return data

        qtd_disponivel = row[0]
        data.update({
            'qtd_disponivel': qtd_disponivel,
        })

        if qtd_a_mover == 0:
            qtd_a_mover = qtd_disponivel

        if qtd_a_mover > qtd_disponivel:
            data.update({
                'error_level': 2,
                'msg': f'Quantidade a mover não disponível',
            })
            return data

        if in_out == 'in':
            qtd_a_mover = qtd_a_mover
        else:
            qtd_a_mover = -qtd_a_mover

        sql = f"""
            INSERT INTO SYSTEXTIL.PCPC_045
            ( PCPC040_PERCONF, PCPC040_ORDCONF, PCPC040_ESTCONF, SEQUENCIA
            , DATA_PRODUCAO, HORA_PRODUCAO, QTDE_PRODUZIDA, QTDE_PECAS_2A
            , QTDE_CONSERTO, TURNO_PRODUCAO, TIPO_ENTRADA_ORD, NOTA_ENTR_ORDEM
            , SERIE_NF_ENT_ORD, SEQ_NF_ENTR_ORD, ORDEM_PRODUCAO, CODIGO_USUARIO
            , QTDE_PERDAS, NUMERO_DOCUMENTO, CODIGO_DEPOSITO, CODIGO_FAMILIA
            , CODIGO_INTERVALO, EXECUTA_TRIGGER, DATA_INSERCAO
            , PROCESSO_SYSTEXTIL, NUMERO_VOLUME, NR_OPERADORES
            , ATZ_PODE_PRODUZIR, ATZ_EM_PROD, ATZ_A_PROD, EFICIENCIA_INFORMADA
            , USUARIO_SYSTEXTIL, CODIGO_OCORRENCIA, COD_OCORRENCIA_ESTORNO
            , SOLICITACAO_CONSERTO, NUMERO_SOLICITACAO, NUMERO_ORDEM
            , MINUTOS_PECA, NR_OPERADORES_INFORMADO, EFICIENCIA
            )
            SELECT
              *
            FROM (
              SELECT
                PCPC040_PERCONF, PCPC040_ORDCONF, PCPC040_ESTCONF
              , SEQUENCIA + 1 SEQUENCIA
              , TO_DATE(CURRENT_DATE) DATA_PRODUCAO
              , CURRENT_TIMESTAMP HORA_PRODUCAO
              , 0 QTDE_PRODUZIDA
              , 0 QTDE_PECAS_2A
              , {qtd_a_mover} QTDE_CONSERTO
              , TURNO_PRODUCAO, TIPO_ENTRADA_ORD, NOTA_ENTR_ORDEM
              , SERIE_NF_ENT_ORD, SEQ_NF_ENTR_ORD, ORDEM_PRODUCAO
              , {colab.matricula} CODIGO_USUARIO
              , 0 QTDE_PERDAS
              , NUMERO_DOCUMENTO, CODIGO_DEPOSITO, CODIGO_FAMILIA
              , CODIGO_INTERVALO, EXECUTA_TRIGGER
              , CURRENT_TIMESTAMP DATA_INSERCAO
              , '?' PROCESSO_SYSTEXTIL
              , NUMERO_VOLUME, NR_OPERADORES
              , ATZ_PODE_PRODUZIR, ATZ_EM_PROD, ATZ_A_PROD
              , EFICIENCIA_INFORMADA
              , '?' USUARIO_SYSTEXTIL
              , CODIGO_OCORRENCIA, COD_OCORRENCIA_ESTORNO, SOLICITACAO_CONSERTO
              , NUMERO_SOLICITACAO, NUMERO_ORDEM, MINUTOS_PECA
              , NR_OPERADORES_INFORMADO, EFICIENCIA
              FROM SYSTEXTIL.PCPC_045
              WHERE PCPC040_PERCONF = {lote[:4]}
                AND PCPC040_ORDCONF = {lote[4:]}
                AND PCPC040_ESTCONF = {estagio}
              ORDER BY
                SEQUENCIA DESC
            )
            WHERE rownum = 1
        """

        try:
            cursor.execute(sql)
        except Exception:
            data.update({
                'error_level': 3,
                'msg': 'Erro ao mover a quantidade',
            })
            return data

        sql = f"""
            UPDATE PCPC_045 ml
            SET
              ml.USUARIO_SYSTEXTIL = '*' || (
                SELECT
                  u.USUARIO
                FROM HDOC_030 u
                WHERE u.CODIGO_USUARIO = ml.CODIGO_USUARIO
              )
            --, ml.PROCESSO_SYSTEXTIL = '-'
            WHERE
            ( ml.PCPC040_PERCONF
            , ml.PCPC040_ORDCONF
            , ml.PCPC040_ESTCONF
            , ml.SEQUENCIA
            ) IN
            ( SELECT
                ml.PCPC040_PERCONF
              , ml.PCPC040_ORDCONF
              , ml.PCPC040_ESTCONF
              , ml.SEQUENCIA
              FROM PCPC_045 ml
              JOIN HDOC_030 u
                ON u.CODIGO_USUARIO = ml.CODIGO_USUARIO
              WHERE PCPC040_PERCONF = {lote[:4]}
                AND PCPC040_ORDCONF = {lote[4:]}
                AND PCPC040_ESTCONF = {estagio}
                AND ml.USUARIO_SYSTEXTIL != u.USUARIO
                AND ml.DATA_PRODUCAO = TO_DATE(CURRENT_DATE)
            )
        """

        try:
            cursor.execute(sql)
        except Exception:
            data.update({
                'error_level': 4,
                'msg': 'Erro ao ajustar nome do usuário',
            })
            return data

    data.update({
        'error_level': 0,
        'msg': 'OK',
    })
    return data


def ajax_conserto_lote(request, lote, estagio, in_out, qtd_a_mover):
    data = dict_conserto_lote(request, lote, estagio, in_out, qtd_a_mover)

    return JsonResponse(data, safe=False)
