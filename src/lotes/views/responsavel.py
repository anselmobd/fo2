import re

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.models import rows_to_dict_list

from lotes.forms import ResponsPorEstagioForm


def responsTodos(request):
    return responsCustom(request, True)


def respons(request):
    return responsCustom(request, False)


def responsCustom(request, todos):
    title_name = 'Responsável por estágio'
    context = {'titulo': title_name}
    if todos:
        context.update({'todos': True})
    if request.method == 'POST':
        form = ResponsPorEstagioForm(request.POST)
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            usuario = '%'+form.cleaned_data['usuario']+'%'
            usuario_num = re.sub("\D", "", form.cleaned_data['usuario'])
            ordem = form.cleaned_data['ordem']
            cursor = connections['so'].cursor()
            sql = """
                SELECT
                  e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
                , CASE WHEN u.USUARIO IS NULL
                  THEN '--SEM RESPONSAVEL--'
                  ELSE u.USUARIO || ' ( ' || u.CODIGO_USUARIO || ' )'
                  END USUARIO
                FROM MQOP_005 e
                LEFT JOIN MQOP_006 r
                  ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
                 AND r.TIPO_MOVIMENTO = 0
                LEFT JOIN HDOC_030 u
                  ON u.CODIGO_USUARIO = r.CODIGO_USUARIO
                WHERE e.CODIGO_ESTAGIO <> 0
                  AND ( %s is NULL OR e.CODIGO_ESTAGIO = %s )
                  AND ( ( coalesce( u.USUARIO, '_' ) like %s )
                      OR ( %s is NOT NULL AND u.CODIGO_USUARIO = %s )
                      )
            """
            if not todos:
                sql = sql + """
                      AND u.USUARIO <> 'ANSELMO_SIS'
                      AND ( e.CODIGO_ESTAGIO < 7 OR
                            u.USUARIO not in ( 'ROSANGELA_PCP'
                                             , 'ALESSANDRA_PCP' )
                          )
                """
            sql = sql + """
                ORDER BY
            """
            if ordem == 'e':
                sql = sql + '''
                      e.CODIGO_ESTAGIO
                    , u.USUARIO
                '''
            else:
                sql = sql + '''
                      u.USUARIO
                    , e.CODIGO_ESTAGIO
                '''
            cursor.execute(sql, (estagio, estagio,
                                 usuario, usuario_num, usuario_num))
            data = rows_to_dict_list(cursor)
            if len(data) != 0:
                if ordem == 'e':
                    context.update({
                        'headers': ('Estágio',
                                    'Usuário Systêxtil ( matrícula )'),
                        'fields': ('ESTAGIO', 'USUARIO'),
                        'data': data,
                    })
                else:
                    context.update({
                        'headers': ('Usuário', 'Estágio'),
                        'fields': ('USUARIO', 'ESTAGIO'),
                        'data': data,
                    })
    else:
        form = ResponsPorEstagioForm()
    context['form'] = form
    return render(request, 'lotes/respons.html', context)
