from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions.strings import pluralize

from lotes.queries.op import op_aprod

import cd.forms
from cd.queries.novo_modulo.solicitacoes import get_solicitacoes
from cd.queries.novo_modulo.solicitacao import get_solicitacao
from cd.queries.novo_modulo import finaliza_empenho


class FinalizaEmpenhoOp(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FinalizaEmpenhoOp, self).__init__(*args, **kwargs)
        self.permission_required = 'cd.pode_finalizar_empenho_op_finalizada'
        self.Form_class = cd.forms.FinalizaEmpenhoOpForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/finaliza_emp_op.html'
        self.title_name = 'Finaliza empenho de OP finalizada'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = op_aprod.query(cursor, self.op)
        row = data[0]

        if row['qtd'] is None:
            self.context['mensagem'] = 'OP não encontrada'
            return

        if row['qtd'] != 0:
            self.context['mensagem'] = 'OP não finalizada'
            return

        data = get_solicitacoes(cursor, op=self.op)

        if not data:
            self.context['mensagem'] = 'OP sem empenhos'
            return

        data = get_solicitacao(
                cursor,
                op=self.op,
            )

        count = 0
        for row in data:
            if row['solicitacao']:
                self.context['mensagem'] = 'OP com solicitação'
                return
            if row['situacao'] < 5:
                count += 1

        if not count:
            self.context['mensagem'] = 'OP sem empenhos'
            return

        for row in data:
            if row['situacao'] < 5:
                empenho = finaliza_empenho.exec(
                    cursor,
                    op=row['ordem_producao'],
                    oc=row['ordem_confeccao'],
                    ped=row['pedido_destino'],
                    ref=row['grupo_destino'],
                )
                if len(empenho) > 1:
                    self.context['mensagem'] = (
                        'Ao verificar o que seria exluido, filtro de '
                        'lote encontrou mais de um registro'
                    )
                    return

        for row in data[:1]:
            if row['situacao'] < 5:
                empenho = finaliza_empenho.exec(
                    cursor,
                    executa=True,
                    op=row['ordem_producao'],
                    oc=row['ordem_confeccao'],
                    ped=row['pedido_destino'],
                    ref=row['grupo_destino'],
                )

        self.context.update({
            'mensagem': (
                f"Finalizado{pluralize(count)} "
                f"{count} empenho{pluralize(count)} da OP"
            ),
        })
