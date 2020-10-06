from pprint import pprint

from utils.functions.data import filtered_data_fields
from utils.functions.digits import *
from utils.functions.models import rows_to_dict_list_lower


def lista_solicita_lote(cursor, filtro=None, data=None, ref=None):
    filtra_data = ''
    if data is not None:
        filtra_data = f'''--
            AND s.data = '{data}'
        '''
    filtra_ref = ''
    if ref is not None and ref != '':
        filtra_ref = f'''--
            AND s.id in (
              select distinct
                sq.solicitacao_id
              from fo2_cd_solicita_lote_qtd sq
              left join fo2_cd_lote l
                on l.id = sq.lote_id
              where
                l.referencia = '{ref}'
            )
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
        , s.can_print
        , s.coleta
        , u.username usuario__username
        , coalesce(sum(sq.qtd), 0) total_qtd
        , coalesce(sum(
            case when l.local is null
            then 0
            else sq.qtd
            end
          ), 0) total_no_cd
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
          {filtra_ref} -- filtra_ref
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
        data = filtered_data_fields(
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
