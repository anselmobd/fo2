import operator
import re
from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def query_endereco(cursor, tipo='TO'):
    where_tipo = []
    if tipo == 'IE':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGH][0123456789]{{4}}$')",
        ]
    elif tipo == 'IQ':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1Q[0123456789]{{4}}$')",
        ]
    elif tipo == 'IL':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1L[0123456789]{{4}}$')",
        ]
    elif tipo == 'IN':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGHLQ][0123456789]{{4}}$')",
        ]
    elif tipo == 'IT':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
        ]
    elif tipo == 'EL':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^2S[0123456789]{{4}}$')",
        ]
    elif tipo == 'EN':
        where_tipo = [
            "e.COD_ENDERECO LIKE '2%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^2S[0123456789]{{4}}$')",
        ]
    elif tipo == 'ET':
        where_tipo = [
            "e.COD_ENDERECO LIKE '2%'",
        ]
    elif tipo != 'TO':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1{tipo}[0123456789]{{4}}$')",
        ]
    field_list=[
        "e.COD_ENDERECO end",
        "e.ROTA",
        "ec.COD_CONTAINER palete",
    ]
    order_list=[
        f"e.COD_ENDERECO",
    ]
    where = "\n  AND ".join(where_tipo) if where_tipo else ""
    qwhere = " ".join(["WHERE", where]) if where else "-- where"

    fields = "\n, ".join(field_list)
    order = "\n, ".join(order_list) if order_list else ""

    sql = f"""
        select
          {fields}
        from ENDR_013 e -- endereço
        left join ENDR_015 ec -- endereço/container
          on ec.COD_ENDERECO = e.COD_ENDERECO
        {qwhere}
        order by {order}
    """
   
    debug_cursor_execute(cursor, sql)
    data = dictlist(cursor)
    
    data = data_details_from_end(data, 'end')

    return data


class EnderecoCd():
    def __init__(self, endereco=None) -> None:
        # private
        self._endereco = None

        # init
        self.endereco = endereco

        # properties
        self.valido = None
        self.espaco = None
        self.bloco = None
        self.andar = None
        self.coluna = None
        self.prioridade = None
        self.order_ap = None

    @property
    def endereco(self):
        return self._endereco

    @endereco.setter
    def endereco(self, endereco):
        if self._endereco != endereco:
            self._endereco = endereco
            self._mount_details()

    def _mount_details(self):
        parts = endereco_split(self.endereco)
        if self.endereco:
            tamanho = len(self.endereco)
            self.valido = True
            self.bloco = parts['bloco']
            self.andar = parts['andar']
            self.coluna = parts['coluna']
            if tamanho != 6:
                self.valido = False
                self.prioridade = 5
                self.order_ap = 0
                self.espaco = 'Indefinido (len)'
            elif parts['espaco'] == '1' and parts['bloco'] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                self.prioridade = 1
                self.order_ap = 10000 + int(parts['coluna']) * 100 + int(parts['andar'])
                self.espaco = 'Estantes'
            elif parts['espaco'] == '1' and parts['bloco'] == 'L':
                self.prioridade = 2
                self.order_ap = int(parts['apartamento'])
                self.espaco = 'Lateral'
            elif parts['espaco'] == '1' and parts['bloco'] == 'Q':
                self.prioridade = 3
                self.order_ap = int(parts['apartamento'])
                self.espaco = 'Quarto andar'
            elif parts['espaco'] == '2' and parts['bloco'] == 'S':
                self.prioridade = 4
                self.order_ap = 0
                self.espaco = 'Externo'
            else:
                self.valido = False
                self.prioridade = 6
                self.order_ap = 0
                self.espaco = 'Indefinido (else)'
        else:
            self.valido = False
            self.espaco = 'Não endereçado'
            self.bloco = '-'
            self.andar = '-'
            self.coluna = '-'
            self.prioridade = 7
            self.order_ap = 0

    @property
    def details_dict(self):
        return {
            'valido': self.valido,
            'espaco': self.espaco,
            'bloco': self.bloco,
            'andar': self.andar,
            'coluna': self.coluna,
            'prioridade': self.prioridade,
            'order_ap': self.order_ap,
        }

def row_details_from_end(row, end_field):
    parts = endereco_split(row[end_field])
    tamanho = len(row[end_field])
    row['bloco'] = parts['bloco']
    row['andar'] = parts['andar']
    row['coluna'] = parts['coluna']
    if tamanho != 6:
        row['prioridade'] = 5
        row['order_ap'] = 0
        row['espaco'] = 'Indefinido'
    elif parts['espaco'] == '1' and parts['bloco'] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        row['prioridade'] = 1
        row['order_ap'] = 10000 + int(parts['coluna']) * 100 + int(parts['andar'])
        row['espaco'] = 'Estantes'
    elif parts['espaco'] == '1' and parts['bloco'] == 'L':
        row['prioridade'] = 2
        row['order_ap'] = int(parts['apartamento'])
        row['espaco'] = 'Lateral'
    elif parts['espaco'] == '1' and parts['bloco'] == 'Q':
        row['prioridade'] = 3
        row['order_ap'] = int(parts['apartamento'])
        row['espaco'] = 'Quarto andar'
    elif parts['espaco'] == '2' and parts['bloco'] == 'S':
        row['prioridade'] = 4
        row['order_ap'] = 0
        row['espaco'] = 'Externo'
    else:
        row['prioridade'] = 5
        row['order_ap'] = 0
        row['espaco'] = 'Indefinido'
    return row


def data_details_from_end(data, end_field):
    for row in data:
        if not row['palete']:
            row['palete'] = '-'
        row = row_details_from_end(row, end_field)

    data.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

    return data


def endereco_split(endereco):
    """Split endereço em espaco, bloco e apartamento; e este último em andar e coluna"""
    parts = {
        'espaco' : None,
        'bloco' : None,
        'apartamento' : None,
        'andar' : None,
        'coluna' : None,
    }
    if not endereco:
        return parts
    try:
        end_parts = re.search('^([0-9])([A-Z]?[0-9]?[A-Z])([0-9]+)$', endereco)
    except Exception:
        end_parts = None
    if end_parts:
        try:
            parts['espaco'] = end_parts.group(1)
            parts['bloco'] = end_parts.group(2)
            parts['apartamento'] = end_parts.group(3)
        except AttributeError:
            end_parts = None
    if end_parts:
        if parts['apartamento'] and len(parts['apartamento']) >= 4:
            try:
                ap_parts = re.search('^([0-9]+)([0-9]{2})$', parts['apartamento'])
                parts['andar'] = ap_parts.group(1)
                parts['coluna'] = ap_parts.group(2)
            except Exception:
                pass
    else:
        parts['espaco'] = endereco[0]
        parts['bloco'] = endereco[1:]
    return parts


def calc_rota(endereco):
    ruas = {
        'A': 'AB',
        'B': 'AB',
        'C': 'CD',
        'D': 'CD',
        'E': 'EF',
        'F': 'EF',
        'G': 'GH',
        'H': 'GH',
    }
    parts = endereco_split(endereco)
    if parts['bloco'] in ruas:
        icoluna = int(parts['coluna'])
        irota = icoluna//2
        rua = ruas[parts['bloco']]
        rota = f"{parts['espaco']}{rua}{irota:02}"
    else:
        rota = f"{parts['espaco']}{parts['bloco']}"
    return rota


def add_endereco(cursor, endereco):
    """Cria endereco no banco de dados
    Recebe: cursor e endereco a ser criado
    Retorna: Se sucesso, None, senão, mensagem de erro
    """
    rota = calc_rota(endereco)
    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_013
        (RUA, BOX, ALTURA, COD_ENDERECO, EMPRESA, PROCESSO, SITUACAO, TIPO_ENDERECO, ROTA)
        VALUES(NULL, NULL, NULL, '{endereco}', 1, 1, '1', '1', '{rota}')
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)

def lotes_em_local(cursor, local=None):
    """Lista lotes paletezados"""
    filtro = f"""--
        WHERE ec.COD_ENDERECO = '{local}'
            OR UPPER(lp.COD_CONTAINER)  = '{local}'
    """ if local else ''
    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco
        , UPPER(lp.COD_CONTAINER) palete
        , lp.ORDEM_PRODUCAO op
        , lp.ORDEM_CONFECCAO lote
        , lp.DATA_INCLUSAO data
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON UPPER(ec.COD_CONTAINER) = UPPER(lp.COD_CONTAINER)
        {filtro} -- filtro
        ORDER BY
          lp.DATA_INCLUSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def lotes_em_versao_palete(cursor, palete, data_versao):
    sql = f"""
        SELECT
          lph.ORDEM_PRODUCAO op
        , lph.ORDEM_CONFECCAO lote
        , lph.DATA_INCLUSAO data
        FROM ENDR_014_HIST_DUOMO lph -- esvaziamento de palete - lote/palete - oc/container
        WHERE lph.COD_CONTAINER = '{palete}'
          AND lph.DATA_VERSAO = '{data_versao}'
        ORDER BY
          lph.DATA_INCLUSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def lotes_em_palete(cursor, palete):
    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco
        , lp.COD_CONTAINER palete
        , lp.ORDEM_PRODUCAO op
        , lp.ORDEM_CONFECCAO lote
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON ec.COD_CONTAINER = lp.COD_CONTAINER 
        WHERE 1=1
          AND lp.COD_CONTAINER = '{palete}'
        ORDER BY
          lp.ORDEM_PRODUCAO
        , lp.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def add_lote_in_endereco(cursor, endereco, op, lote):
    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_014
        (COD_CONTAINER, ORDEM_PRODUCAO, ORDEM_CONFECCAO, DATA_INCLUSAO, NIVEL, GRUPO, SUB, ITEM, QUANTIDADE)
        VALUES('{endereco}', {op}, '{lote}', CURRENT_TIMESTAMP, NULL, NULL, NULL, NULL, 0)
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False


def local_de_lote(cursor, lote):
    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco 
        , lp.COD_CONTAINER palete
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON ec.COD_CONTAINER = lp.COD_CONTAINER 
        WHERE lp.ORDEM_CONFECCAO = {lote}
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def esvazia_palete(cursor, palete):
    sql = f"""
        DELETE FROM ENDR_014 lp -- lote/palete - oc/container
        WHERE lp.COD_CONTAINER  = '{palete}'
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False

def palete_guarda_hist(cursor, palete):
    sql = f"""
        INSERT INTO ENDR_014_HIST_DUOMO
          (COD_CONTAINER, ORDEM_PRODUCAO, ORDEM_CONFECCAO, DATA_INCLUSAO, NIVEL, GRUPO, SUB, ITEM, QUANTIDADE)
        SELECT
          COD_CONTAINER, ORDEM_PRODUCAO, ORDEM_CONFECCAO, DATA_INCLUSAO, NIVEL, GRUPO, SUB, ITEM, QUANTIDADE
        FROM ENDR_014 -- lote/palete - oc/container
        WHERE COD_CONTAINER = '{palete}'
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False

def get_palete(cursor, palete):
    sql = f"""
        SELECT
          p.COD_CONTAINER
        , p.COD_TIPO
        , p.ENDERECO
        , p.TARA_CONTAINER
        , p.QUANTIDADE_MAXIMO
        , p.ULTIMA_ATUALIZACAO_TARA
        , p.SITUACAO
        , p.TUSSOR_IMPRESSA
        FROM ENDR_012 p -- container palete
        WHERE p.COD_CONTAINER = '{palete}'
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def get_endereco(cursor, endereco):
    sql = f"""
        SELECT
          e.RUA
        , e.BOX
        , e.ALTURA
        , e.COD_ENDERECO
        , e.EMPRESA
        , e.PROCESSO
        , e.SITUACAO
        , e.TIPO_ENDERECO
        , e.ROTA
        FROM ENDR_013 e
        WHERE e.COD_ENDERECO = '{endereco}'
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def get_esvaziamentos_de_palete(cursor, palete):
    sql = f"""
        SELECT DISTINCT
          h.DATA_VERSAO dh
        FROM ENDR_014_HIST_DUOMO h
        WHERE h.COD_CONTAINER = '{palete}'
        ORDER BY 
          h.DATA_VERSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
