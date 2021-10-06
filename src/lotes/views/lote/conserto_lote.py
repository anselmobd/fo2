from pprint import pprint

from django.contrib.auth.models import User
from django.http import JsonResponse

from fo2.connections import db_cursor_so

from base.models import Colaborador
from geral.functions import request_user
from systextil.models import Usuario


def dict_conserto_lote(request, lote, estagio, in_out, qtd_a_mover):
    cursor = db_cursor_so(request)
    return dict_conserto_lote_custom(
        cursor, lote, estagio, in_out, qtd_a_mover, request=request)


def dict_conserto_lote_custom(
        cursor, lote, estagio, in_out, qtd_a_mover, request=None, username=None):
    in_out = in_out.lower()
    data = {
        'lote': lote,
        'estagio': estagio,
        'in_out': in_out,
        'qtd_a_mover': qtd_a_mover,
    }

    if qtd_a_mover is None:
        qtd_a_mover = '0'

    user = None

    if username is not None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

    if request is not None:
        user = request_user(request)

    if user is None:
        if request is None:
            missing_user = 'É necessário informar o nome do usuário'
        else:
            missing_user = 'É necessário estar logado na intranet'
        data.update({
            'error_level': 11,
            'msg': missing_user,
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

    if not estagio.isnumeric():
        data.update({
            'error_level': 25,
            'msg': 'Parâmetro estágio com valor inválido',
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

    if isinstance(qtd_a_mover, str):
        if qtd_a_mover.isnumeric():
            qtd_a_mover = int(qtd_a_mover)
        else:
            data.update({
                'error_level': 24,
                'msg': 'Quantidade a mover com valor inválido',
            })
            return data

    if qtd_a_mover < 0:
        data.update({
            'error_level': 26,
            'msg': 'Quantidade a mover com valor negativo',
        })
        return data

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
            'error_level': 3,
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
          mli.*
        FROM (
          SELECT
            ml1.*
          FROM (
            SELECT
            l.PERIODO_PRODUCAO PCPC040_PERCONF
            , l.ORDEM_CONFECCAO PCPC040_ORDCONF
            , l.CODIGO_ESTAGIO PCPC040_ESTCONF
            , COALESCE( ml.SEQUENCIA + 1, 0 ) SEQUENCIA
            , TO_DATE(CURRENT_DATE) DATA_PRODUCAO
            , CURRENT_TIMESTAMP HORA_PRODUCAO
            , 0 QTDE_PRODUZIDA
            , 0 QTDE_PECAS_2A
            , {qtd_a_mover}  QTDE_CONSERTO
            , COALESCE( ml.TURNO_PRODUCAO, 1 ) TURNO_PRODUCAO
            , COALESCE( ml.TIPO_ENTRADA_ORD, 0 ) TIPO_ENTRADA_ORD
            , COALESCE( ml.NOTA_ENTR_ORDEM, 0 ) NOTA_ENTR_ORDEM
            , ml.SERIE_NF_ENT_ORD
            , COALESCE( ml.SEQ_NF_ENTR_ORD, 0 ) SEQ_NF_ENTR_ORD
            , l.ORDEM_PRODUCAO ORDEM_PRODUCAO
            , {colab.matricula} CODIGO_USUARIO
            , 0 QTDE_PERDAS
            , COALESCE( ml.NUMERO_DOCUMENTO, 0) NUMERO_DOCUMENTO
            , COALESCE( ml.CODIGO_DEPOSITO, 0) CODIGO_DEPOSITO
            , COALESCE( ml.CODIGO_FAMILIA, 0) CODIGO_FAMILIA
            , COALESCE( ml.CODIGO_INTERVALO, 0) CODIGO_INTERVALO
            , COALESCE( ml.EXECUTA_TRIGGER, 3) EXECUTA_TRIGGER
            , CURRENT_TIMESTAMP DATA_INSERCAO
            , '?' PROCESSO_SYSTEXTIL
            , COALESCE( ml.NUMERO_VOLUME, 0) NUMERO_VOLUME
            , COALESCE( ml.NR_OPERADORES, 0) NR_OPERADORES
            , COALESCE( ml.ATZ_PODE_PRODUZIR, 0) ATZ_PODE_PRODUZIR
            , COALESCE( ml.ATZ_EM_PROD, 0) ATZ_EM_PROD
            , COALESCE( ml.ATZ_A_PROD, 0) ATZ_A_PROD
            , COALESCE( ml.EFICIENCIA_INFORMADA, 0) EFICIENCIA_INFORMADA
            , '?' USUARIO_SYSTEXTIL
            , COALESCE( ml.CODIGO_OCORRENCIA, 0) CODIGO_OCORRENCIA
            , COALESCE( ml.COD_OCORRENCIA_ESTORNO, 0) COD_OCORRENCIA_ESTORNO
            , COALESCE( ml.SOLICITACAO_CONSERTO, 0) SOLICITACAO_CONSERTO
            , COALESCE( ml.NUMERO_SOLICITACAO, 0) NUMERO_SOLICITACAO
            , COALESCE( ml.NUMERO_ORDEM, 0) NUMERO_ORDEM
            , COALESCE( ml.MINUTOS_PECA, 0) MINUTOS_PECA
            , ml.NR_OPERADORES_INFORMADO
            , ml.EFICIENCIA
            FROM PCPC_040 l
            LEFT JOIN SYSTEXTIL.PCPC_045 ml
            ON ml.PCPC040_PERCONF = l.PERIODO_PRODUCAO
            AND ml.PCPC040_ORDCONF = l.ORDEM_CONFECCAO
            AND ml.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
            WHERE l.PERIODO_PRODUCAO = {lote[:4]}
            AND l.ORDEM_CONFECCAO = {lote[4:]}
            AND l.CODIGO_ESTAGIO = {estagio}
            ORDER BY
            ml.SEQUENCIA DESC
          )
          WHERE rownum = 1
        ) mli
        LEFT JOIN SYSTEXTIL.PCPC_045 mlt
          ON mlt.PCPC040_PERCONF = mli.PCPC040_PERCONF
         AND mlt.PCPC040_ORDCONF = mli.PCPC040_ORDCONF
         AND mlt.PCPC040_ESTCONF = mli.PCPC040_ESTCONF
         AND mlt.DATA_INSERCAO >= mli.DATA_INSERCAO - 2/24/60/60 -- existe um igual feita há 2 segundos
         AND mlt.QTDE_CONSERTO = mli.QTDE_CONSERTO
         AND mlt.QTDE_PRODUZIDA = mli.QTDE_PRODUZIDA
         AND mlt.QTDE_PECAS_2A = mli.QTDE_PECAS_2A
         AND mlt.QTDE_PERDAS = mli.QTDE_PERDAS
        WHERE mlt.PCPC040_PERCONF IS NULL 
    """

    try:
        cursor.execute(sql)
    except Exception:
        data.update({
            'error_level': 31,
            'msg': 'Erro ao mover a quantidade',
        })
        return data

    if cursor.rowcount == 0:
        data.update({
            'error_level': 41,
            'msg': 'Tentativa de gravar 2 vezes o mesmo movimento',
        })
        return data

    sql = f"""
        UPDATE PCPC_045 ml
        SET
            ml.USUARIO_SYSTEXTIL = '*' || (
            SELECT
                u.USUARIO
            FROM HDOC_030 u
            WHERE u.EMPRESA = 1
                AND u.CODIGO_USUARIO = ml.CODIGO_USUARIO
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
            ON u.EMPRESA = 1
            AND u.CODIGO_USUARIO = ml.CODIGO_USUARIO
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
            'error_level': 32,
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
