from pprint import pprint

from utils.functions.digits import *
from utils.functions.models import rows_to_dict_list_lower


def lista_solicita_lote(cursor, filtro=None, data=None):
    filtra_data = ''
    if data is not None:
        filtra_data = f'''--
            AND s.data = '{data}'
        '''
    sql = f'''
        select
          s.id
        , s.codigo
        , s.descricao
        , s.data
        , s.ativa
        , s.create_at
        , s.update_at
        , s.usuario_id
        , u.username usuario__username
        , sum(sq.qtd) total_qtd
        , sum(
            case when l.local is null
            then 0
            else sq.qtd
            end
          ) total_no_cd
        from fo2_cd_solicita_lote s
        left join fo2_cd_solicita_lote_qtd sq
          on sq.solicitacao_id = s.id
         and sq.origin_id = 0
        left join fo2_cd_lote l
          on l.id = sq.lote_id
        left join auth_user u
          on u.id = s.usuario_id
        where 1=1
          {filtra_data} -- filtra_data
        group by
          s.id
        , s.codigo
        , s.descricao
        , s.ativa
        , s.create_at
        , s.update_at
        , s.usuario_id
        , u.username
        order by
          s.update_at desc
    '''
    cursor.execute(sql)
    data = rows_to_dict_list_lower(cursor)

    for row in data:
        row['numero'] = f"#{fo2_digit_with(row['id'])}"

    if filtro:
        data = filtered_date_fields(
            filtro,
            data,
            'numero',
            'codigo',
            'descricao',
            'usuario__username',
        )

    for row in data:
        if row['data'] is None:
            row['data'] = ''

    return data


def search_in_dict_fields(search, row, *fields, **params):
    ignore_case = params.get('ignore_case', True)
    for part in search.split():
        for field in fields:
            pattern = part.lower() if ignore_case else part
            value = row[field].lower() if ignore_case else row[field]
            if pattern in value:
                return True
    return False


def filtered_date_fields(search, data, *fields, **params):
    result = []
    for row in data:
        if search_in_dict_fields(search, row, *fields, **params):
            result.append(row)
    return result
