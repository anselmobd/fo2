from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import (
    request_user,
    has_permission,
    )

import lotes.models
from produto.functions import papg_modelo

import cd.queries as queries


class SolicitacaoDetalhe(LoginRequiredMixin, View):

    def __init__(self):
        self.template_name = 'cd/solicitacao_detalhe.html'
        self.title_name = 'Detalhes de solicitação'

    def link_endereco(self, row):
        if row['lote__local'] != '-Ausente-':
            row['lote__local|LINK'] = reverse(
                'cd:estoque_filtro',
                args=['E', row['lote__local']])
            row['lote__local|TARGET'] = '_BLANK'

    def mount_context(self, solicit_id, user):
        context = {
            'solicit_id': solicit_id,
            'user': user,
        }

        try:
            solicitacao = lotes.models.SolicitaLote.objects.get(
                id=solicit_id)
        except lotes.models.SolicitaLote.DoesNotExist:
            context['erro'] = \
                'Id de solicitação inválido.'
            return context

        solicit_ativa_recs = lotes.models.SolicitaLote.objects.filter(
            usuario=user, ativa=True)
        if len(solicit_ativa_recs) == 1:
            solicit_ativa_cod = solicit_ativa_recs[0].codigo
            solicit_ativa_id = str(solicit_ativa_recs[0].id)
            if solicit_ativa_id != solicit_id:
                context['solicit_ativa_cod'] = solicit_ativa_cod
                context['solicit_ativa_id'] = solicit_ativa_id
            else:
                context['solicit_ativa_cod'] = '='

        context['solicitacao'] = solicitacao

        solicit_qtds = lotes.models.SolicitaLoteQtd.objects.values(
            'id', 'lote__op', 'lote__lote', 'lote__referencia',
            'lote__cor', 'lote__tamanho', 'qtd', 'update_at'
        ).annotate(
            lote__local=Coalesce('lote__local', Value('-Ausente-'))
        ).filter(
            solicitacao=solicitacao
        ).order_by(
            '-update_at'
        )

        for row in solicit_qtds:
            row['delete'] = ''
            row['delete|HOVER'] = 'Exclui lote'
            row['delete|LINK'] = reverse(
                'cd:solicitacao_detalhe__get3',
                args=[solicitacao.id, 'd', row['id']])
            row['delete|GLYPHICON'] = 'glyphicon-remove'
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'
            self.link_endereco(row)

        link = reverse(
            'cd:solicitacao_detalhe__get2',
            args=[solicitacao.id, 'l'])
        limpa = '''
            <a title="Limpa solicitação"
            href="{link}"
            ><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"
            ></span></a>
        '''.format(link=link)

        context.update({
            'headers': ['Endereço', 'OP', 'Lote', 'Referência',
                        'Cor', 'Tamanho', 'Quant. Solicitada', 'Em', (limpa,)],
            'fields': ['lote__local', 'lote__op', 'lote__lote',
                       'lote__referencia', 'lote__cor', 'lote__tamanho', 'qtd',
                       'update_at', 'delete'],
            'data': solicit_qtds,
        })

        solicit_qtds_inat = \
            lotes.models.SolicitaLoteQtd.objects_inactive.values(
                'id', 'lote__op', 'lote__lote', 'lote__referencia',
                'lote__cor', 'lote__tamanho', 'qtd', 'when'
            ).annotate(
                lote__local=Coalesce('lote__local', Value('-ausente-'))
            ).filter(
                solicitacao=solicitacao
            ).order_by(
                '-when'
            )

        for row in solicit_qtds_inat:
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'

        context.update({
            'inat_headers': ['Endereço', 'OP', 'Lote',
                             'Referência', 'Cor', 'Tamanho',
                             'Quant. Solicitada', 'Removido em'],
            'inat_fields': ['lote__local', 'lote__op', 'lote__lote',
                            'lote__referencia', 'lote__cor', 'lote__tamanho',
                            'qtd', 'when'],
            'inat_data': solicit_qtds_inat,
        })

        por_endereco = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__referencia', 'lote__cor', 'lote__tamanho'
        ).annotate(
            lote_ordem=Coalesce('lote__local', Value('0000')),
            lote__local=Coalesce('lote__local', Value('-Ausente-')),
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao
        ).order_by(
            'lote_ordem', 'lote__op', 'lote__referencia', 'lote__cor',
            'lote__tamanho', 'lote__lote'
        )

        for row in por_endereco:
            if row['qtdsum'] == row['lote__qtd_produzir']:
                row['inteira_parcial'] = 'Lote inteiro'
            else:
                row['inteira_parcial'] = 'Parcial'
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'
            self.link_endereco(row)

        context.update({
            'e_headers': ['Endereço', 'OP', 'Lote',
                          'Referência', 'Cor', 'Tamanho',
                          'Quant. Solicitada', 'Solicitação'],
            'e_fields': ['lote__local', 'lote__op', 'lote__lote',
                         'lote__referencia', 'lote__cor', 'lote__tamanho',
                         'qtdsum', 'inteira_parcial'],
            'e_data': por_endereco,
        })

        para_cx = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__estagio', 'lote__referencia',
            'lote__cor', 'lote__tamanho', 'lote__ordem_tamanho',
            'lote__op_obj__deposito'
        ).annotate(
            lote_ordem=Coalesce('lote__local', Value('0000')),
            lote__local=Coalesce('lote__local', Value('-Ausente-')),
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao
        )

        for row in para_cx:
            row['modelo'] = papg_modelo(row['lote__referencia'])
            row['modelo_order'] = int(row['modelo'])
            if row['qtdsum'] == row['lote__qtd_produzir']:
                row['inteira_parcial'] = 'Lote inteiro'
            else:
                row['inteira_parcial'] = 'Parcial'
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'
            if row['lote__estagio'] == 999:
                row['estagio'] = 'Finalizado'
            else:
                row['estagio'] = row['lote__estagio']
            can_transf = row['inteira_parcial'] == 'Parcial'
            can_transf = can_transf or (
                row['lote_ordem'] == '0000'
                and row['inteira_parcial'] == 'Lote inteiro')
            can_transf = can_transf and row['lote__estagio'] == 999
            can_transf = can_transf and row['lote__op_obj__deposito'] != 0
            row['transf_order'] = 1
            row['transf'] = ''
            if can_transf:
                row['transf_order'] = 0
                row['transf|HOVER'] = 'Transfere lote para caixinha'
                row['transf|LINK'] = (
                    "javascript:transfere("
                    f"  '{row['lote__referencia']}'"
                    f", '{row['lote__cor']}'"
                    f", '{row['lote__tamanho']}'"
                    f", '{row['qtdsum']}'"
                    f", '{row['lote__op_obj__deposito']}'"
                    f", '{row['modelo'].zfill(5)}'"
                    ")")
                row['transf|GLYPHICON'] = 'glyphicon-log-in'
            row['lote__op|LINK'] = reverse(
                'producao:op__get', args=[row['lote__op']])
            self.link_endereco(row)

        para_cx = sorted(
            para_cx, key=lambda i: (
                i['transf_order'],
                i['modelo_order'],
                i['lote__cor'],
                i['lote__ordem_tamanho'],
                i['lote__referencia'],
                i['lote__lote'],
                ))

        context.update({
            'cx_headers': [
                'Modelo',
                'Cor',
                'Tamanho',
                'Quant. Solicitada',
                'Referência',
                'Depósito',
                'Transfere',
                'OP',
                'Lote',
                'Solicitação',
                'Endereço',
                'Estágio',
            ],
            'cx_fields': [
                'modelo',
                'lote__cor',
                'lote__tamanho',
                'qtdsum',
                'lote__referencia',
                'lote__op_obj__deposito',
                'transf',
                'lote__op',
                'lote__lote',
                'inteira_parcial',
                'lote__local',
                'estagio',
            ],
            'cx_style': {},
            'cx_data': para_cx,
        })

        referencias = lotes.models.SolicitaLoteQtd.objects.filter(
            solicitacao=solicitacao
        ).values('lote__referencia').distinct()

        cursor_def = connection.cursor()
        grades2 = []
        for referencia in referencias:
            # Grade de solicitação
            context_ref = queries.grade_solicitacao(
                cursor_def, referencia['lote__referencia'],
                solicit_id=solicit_id)
            grades2.append(context_ref)

        context.update({
            'grades2': grades2,
        })

        grade_total = queries.grade_solicitacao(
            cursor_def, solicit_id=solicit_id)
        grade_total.update({
            'style': {i: 'text-align: right;'
                      for i in range(2, len(grade_total['fields'])+1)},
        })
        context.update({
            'gt': grade_total,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'acao' in kwargs:
            acao = kwargs['acao']
        else:
            acao = None
        if 'id' in kwargs:
            slq_id = kwargs['id']
        else:
            slq_id = None
        solicit_id = kwargs['solicit_id']

        user = request_user(request)

        if acao is not None:
            if not has_permission(request, 'lotes.change_solicitalote'):
                context.update({
                    'erro': 'Usuário não tem direito de alterar solicitações.'
                })
                return render(request, self.template_name, context)

        if acao == 'd' and slq_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.get(
                    id=slq_id)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        if acao == 'l' and solicit_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.filter(
                    solicitacao__id=solicit_id)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        # desreserva lote em todas as solicitações
        if acao == 'dl' and slq_id is not None:
            lote = slq_id
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.filter(
                    lote__lote=lote)
                solicit_qtds.delete()
                context.update({
                    'acao_mensagem':
                        'Lote {} cacelado em todas as solicitações.'.format(
                            lote
                        )
                })
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        # desreserva endereçados
        if acao == 'de' and solicit_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.filter(
                    solicitacao__id=solicit_id, lote__local__isnull=False)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        # move endereçados
        if acao == 'move' and solicit_id is not None:
            try:
                solicit_ativa = lotes.models.SolicitaLote.objects.get(
                    usuario=user, ativa=True)
                try:
                    for solicit_qtd in \
                            lotes.models.SolicitaLoteQtd.objects.filter(
                                solicitacao__id=solicit_id,
                                lote__local__isnull=False):
                        solicit_qtd.solicitacao = solicit_ativa
                        solicit_qtd.save()
                except Exception:
                    pass
            except lotes.models.SolicitaLote.DoesNotExist:
                pass

        data = self.mount_context(solicit_id, user)
        context.update(data)
        return render(request, self.template_name, context)
