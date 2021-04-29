from pprint import pprint

from django.db import connection
from django.urls import reverse

from base.views import O2BaseGetPostView
from utils.functions.models import rows_to_dict_list_lower

import servico.forms
import servico.models


class Lista(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Lista, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.ListaForm
        self.template_name = 'servico/lista.html'
        self.title_name = 'Lista ordens'


    def mount_context(self):
        try:
            self.ordem = int(self.ordem)
        except Exception:
            return
        
        # if self.ordem == 0:
        #     interacoes = servico.models.Interacao.objects.all().order_by(
        #         "-documento_id", "-create_at")
        # else:
        #     try:
        #         interacoes = servico.models.Interacao.objects.filter(documento_id=self.ordem)
        #     except servico.models.Documento.DoesNotExist:
        #         self.context.update({
        #             'erro': 'Ordem não encontrada.',
        #         })
        #         return

        # interacoes = interacoes.values(
        #     'documento_id', 'create_at', 'user__username', 'descricao', 'equipe__nome', 'status__nome', 'evento__nome', 'nivel__nome'
        # )

        filtra_ordem = ''
        if self.ordem != 0:
            filtra_ordem = f'and il.documento_id = {self.ordem}'

        sql = f"""
            with inte_limites as
            ( select
              int_lim.documento_id
            , max(int_lim.create_at) ult_at
            , min(int_lim.create_at) pri_at
            from fo2_serv_interacao int_lim
            group by
              int_lim.documento_id
            )
            select
              inte.documento_id
            , inte.create_at
            , s.nome status__nome
            , ev.nome evento__nome
            , u.username user__username
            , e.nome equipe__nome
            , na.nome nivel__nome
            , inte.descricao
            , last_s.nome last_status__nome
            , last_inte.create_at last_create_at
            , il.ult_at - il.pri_at diff_at
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
            join fo2_serv_nivel_atend na
              on na.id = inte.nivel_id
            join fo2_serv_interacao last_inte
              on last_inte.documento_id = il.documento_id
             and last_inte.create_at = il.ult_at
            join fo2_serv_status last_s
              on last_s.id = last_inte.status_id
            where 1=1
              {filtra_ordem} -- filtra_ordem
            order by
              il.documento_id desc
        """
        cursor = connection.cursor()
        cursor.execute(sql)
        interacoes = rows_to_dict_list_lower(cursor)

        for row in interacoes:
            row['documento_id|LINK'] = reverse(
                    'servico:ordem__get',
                    args=[row['documento_id']],
                )

        self.context.update({
            'headers': ['#', 'Status', 'Evento', 'Usuário', 'Data/hora', 'Equipe', 'Descrição', 'Nível'],
            'fields': ['documento_id', 'status__nome', 'evento__nome', 'user__username', 'create_at', 'equipe__nome', 'descricao', 'nivel__nome'],
            'data': interacoes,
        })
