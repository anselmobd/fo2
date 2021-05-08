from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def lista_documentos(cursor, ordem, user=None):
    
    filtra_ordem = ''
    if ordem != 0:
        filtra_ordem = f'and il.documento_id = {ordem}'

    filtra_user = ''
    if user is not None:
        filtra_user = f'and last_inte.user_id = {user.id}'

    sql = f"""
        with inte_limites as
        ( select
            int_lim.documento_id
        , max(int_lim.create_at) ult_at
        , min(int_lim.create_at) pri_at
        , count(int_lim.create_at) conta
        from fo2_serv_interacao int_lim
        group by
            int_lim.documento_id
        )
        select
            inte.documento_id
        , inte.create_at
        , s.nome status__nome
        --, ev.nome evento__nome
        , u.username user__username
        , e.nome equipe__nome
        , cl.nome classificacao__nome
        , inte.descricao
        , last_s.nome last_status__nome
        , last_inte.create_at last_create_at
        , il.ult_at - il.pri_at diff_at
        , il.conta
        from inte_limites il
        join fo2_serv_interacao inte
            on inte.documento_id = il.documento_id
            and inte.create_at = il.pri_at
        join auth_user u
            on u.id = inte.user_id
        join fo2_serv_equipe e
            on e.id = inte.equipe_id
        join fo2_serv_status s
            on s.id = inte.status_id
        join fo2_serv_evento ev
            on ev.id = inte.evento_id
        join fo2_serv_classificacao cl
            on cl.id = inte.classificacao_id
        join fo2_serv_interacao last_inte
            on last_inte.documento_id = il.documento_id
            and last_inte.create_at = il.ult_at
        join fo2_serv_status last_s
            on last_s.id = last_inte.status_id
        where 1=1
            {filtra_ordem} -- filtra_ordem
            {filtra_user} -- filtra_user
        order by
            il.documento_id desc
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
