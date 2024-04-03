from pprint import pprint

from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from base.models import Colaborador
from geral.functions import has_permission
from utils.classes import LoggedInUser

from systextil.models import Usuario as SystextilUsuario
from cd.queries.novo_modulo import (
    empenho_hist,
    situacao_empenho,
)


class CancelSolicitacao(View):

    ERROR_STATUS = "ERROR"
    OK_STATUS = "OK"

    def verifica_usuario(self):
        self.logged_in = LoggedInUser()
        if not self.logged_in.has_user:
            return "É necessário estar logado"
        if not has_permission(self.request, 'lotes.pode_produzir_lote'):
            return "É necessário ter permissão para utilizar esta rotina"

    def verifica_colaborador(self):
        try:
            self.colaborador = Colaborador.objects.get(user=self.request.user)
        except Colaborador.DoesNotExist as e:
            return (
                "Não é possível utilizar um usuário que "
                "não está cadastrado como colaborador."
            )

    def verifica_matricula(self):
        try:
            self.matricula = SystextilUsuario.objects.get(
                codigo_usuario=self.colaborador.matricula)
        except SystextilUsuario.DoesNotExist as e:
            return (
                "Não é possível utilizar um colaborador "
                "sem matrícula válida ou inativo."
            )

    def busca_empenhos(self):
        self.empenhos = situacao_empenho.exec(
            self.cursor,
            consulta=True,
            solicitacao=self.solicitacao,
        )
        if not self.empenhos:
            return "Não encontrado nenhum empenho não finalizado ou cancelado"

    def cancela_empenhos(self):
        try:
            for idx, empenho in enumerate(self.empenhos):
                with transaction.atomic(using='sn'):
                    self.cancela_empenho(empenho)
                    self.log_historico(empenho)
        except Exception as e:
            return f"Ocorreu algum erro ao cancelar empenho <{e}>"

    def cancela_empenho(self, empenho):
        row_count = situacao_empenho.exec(
            self.cursor,
            cancela=True,
            solicitacao=self.solicitacao,
            ordem_producao=empenho['ordem_producao'],
            ordem_confeccao=empenho['ordem_confeccao'],
            pedido_destino=empenho['pedido_destino'],
            op_destino=empenho['op_destino'],
            oc_destino=empenho['oc_destino'],
            dep_destino=empenho['dep_destino'],
            grupo_destino=empenho['grupo_destino'],
            alter_destino=empenho['alter_destino'],
            sub_destino=empenho['sub_destino'],
            cor_destino=empenho['cor_destino'],
        )
        if not row_count:
            raise DatabaseError(
                "Nenhum registro afetado ao cancelar empenho "
                f"da solicitacao {self.solicitacao} "
                f"da OC {empenho['ordem_confeccao']} "
                f"da OP {empenho['ordem_producao']}."
            )

    def log_historico(self, empenho):
        count_insert = empenho_hist.insere_hist(
            self.cursor,
            usuario=self.matricula.usuario,
            alteracao={
                'situacao': {
                    'old': empenho['situacao'],
                    'new': 9,
                }
            },
            ordem_producao=empenho['ordem_producao'],
            ordem_confeccao=empenho['ordem_confeccao'],
            pedido_destino=empenho['pedido_destino'],
            op_destino=empenho['op_destino'],
            oc_destino=empenho['oc_destino'],
            dep_destino=empenho['dep_destino'],
            grupo_destino=empenho['grupo_destino'],
            alter_destino=empenho['alter_destino'],
            sub_destino=empenho['sub_destino'],
            cor_destino=empenho['cor_destino'],
            solicitacao=self.solicitacao,
            rotina='cancela_solicitacao',
            can_raise=True,
        )
        if count_insert != 1:
            raise DatabaseError(
                "Nenhum registro inserido ao gravar histórico de cancelamento do empenho "
                f"da solicitacao {self.solicitacao} "
                f"da OC {empenho['ordem_confeccao']} "
                f"da OP {empenho['ordem_producao']}."
            )

    def process(self):
        for passo in [
            self.verifica_usuario,
            self.verifica_colaborador,
            self.verifica_matricula,
            self.busca_empenhos,
            self.cancela_empenhos,
        ]:
            result_error = passo()
            if result_error:
                return (self.ERROR_STATUS, result_error)

        return (self.OK_STATUS, "OK!")

    def response(self, result):
        status, message = result
        return {
            'status': status,
            'message': message,
        }

    def inicializa_variaveis(self, request, kwargs):
        self.cursor = db_cursor_so(request)
        self.request = request
        self.solicitacao = kwargs['solicitacao']

    def get(self, request, *args, **kwargs):
        self.inicializa_variaveis(request, kwargs)
        return JsonResponse(self.response(self.process()), safe=False)
