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

    def do_filt(row):
        return (
            filtro.lower() in row['codigo'].lower() or
            filtro.lower() in row['descricao'].lower() or
            filtro.lower() in row['usuario__username'].lower() or
            filtro.lower() in row['numero'].lower()
        )

    if filtro is None:
        data_filtered = data.copy()
    else:
        data_filtered = filter(do_filt, data)

    data_final = []
    for row in data_filtered:
        if row['data'] is None:
            row['data'] = ''
        data_final.append(row)

    return data_final
