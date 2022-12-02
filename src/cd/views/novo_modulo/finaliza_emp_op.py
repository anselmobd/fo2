from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.models import Colaborador
from base.views.o2.get_post import O2BaseGetPostView
from systextil.models import Usuario as SystextilUsuario
from utils.functions.strings import pluralize

from lotes.queries.op import op_aprod

import cd.forms
from cd.queries.novo_modulo.solicitacoes import get_solicitacoes
from cd.queries.novo_modulo.solicitacao import get_solicitacao
from cd.queries.novo_modulo import (
    empenho_hist,
    finaliza_empenho,
)


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

        try:
            colab = Colaborador.objects.get(user=self.request.user)
        except Colaborador.DoesNotExist as e:
            self.context.update({
                'mensagem': 'Não é possível utilizar um usuário que não '
                    'está cadastrado como colaborador.'
            })
            return

        try:
            s_user = SystextilUsuario.objects.get(codigo_usuario=colab.matricula)
        except SystextilUsuario.DoesNotExist as e:
            self.context.update({
                'mensagem': 'Não é possível utilizar um colaborador sem '
                    'matrícula válida ou inativo.'
            })
            return

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
            self.context['mensagem'] = 'OP sem empenhos (situacao < 5)'
            return

        for row in data:
            if row['situacao'] < 5:
                empenho = finaliza_empenho.exec(
                    cursor,
                    ordem_producao=row['ordem_producao'],
                    ordem_confeccao=row['ordem_confeccao'],
                    pedido_destino=row['pedido_destino'],
                    grupo_destino=row['grupo_destino'],
                )
                if len(empenho) > 1:
                    self.context['mensagem'] = (
                        'Ao verificar o que seria finalizado, filtro de '
                        'lote encontrou mais de um registro'
                    )
                    return

        count = 0
        for row in data:
            if row['situacao'] < 5:
                count_exec = finaliza_empenho.exec(
                    cursor,
                    executa=True,
                    ordem_producao=row['ordem_producao'],
                    ordem_confeccao=row['ordem_confeccao'],
                    pedido_destino=row['pedido_destino'],
                    grupo_destino=row['grupo_destino'],
                )
                count += count_exec
                if count_exec:
                    count_insert = empenho_hist.insere_hist(
                        cursor,
                        usuario=s_user.usuario,
                        alteracao={
                            'situacao': {
                                'old': row['situacao'],
                                'new': 5,
                            }
                        },
                        ordem_producao=row['ordem_producao'],
                        ordem_confeccao=row['ordem_confeccao'],
                        pedido_destino=row['pedido_destino'],
                        op_destino=row['op_destino'],
                        oc_destino=row['oc_destino'],
                        dep_destino=row['dep_destino'],
                        grupo_destino=row['grupo_destino_ori'],
                        alter_destino=row['alter_destino'],
                        sub_destino=row['sub_destino_ori'],
                        cor_destino=row['cor_destino_ori'],
                    )
                    if count_insert < 1:
                        self.context['mensagem'] = (
                            "Erro ao gravar histórico de finalização do empenho "
                            f"da OC {row['ordem_confeccao']} "
                            f"da OP {row['ordem_producao']}."
                        )
                        return

        self.context.update({
            'mensagem': (
                f"Finalizado{pluralize(count)} "
                f"{count} empenho{pluralize(count)} da OP"
            ),
        })
