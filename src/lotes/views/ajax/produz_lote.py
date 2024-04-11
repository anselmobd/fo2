from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.classes import LoggedInUser

from lotes.queries.lote import (
    lote_estagios,
    movimentacao_de_lote,
    quantidade_finalizada,
)

class ProduzLote(View):

    ERROR_STATUS = "ERROR"
    OK_STATUS = "OK"

    def verifica_usuario(self):
        self.logged_in = LoggedInUser()
        if not self.logged_in.has_user:
            return "É necessário estar logado"
        if not has_permission(self.request, 'lotes.pode_produzir_lote'):
            return "É necessário ter permissão para utilizar esta rotina"

    def verifica_estagios(self):
        self.estagios = lote_estagios.get_estagios(
            self.cursor, self.lote, ['COD_EST', 'Q_DB', 'SEQ_EST'])
        if not self.estagios:
            return "Lote não encontrado"

    def busca_qtd_finalizada(self):
        dados = quantidade_finalizada.query(self.cursor, self.lote)
        if dados:
            finalizada = dados[0]
            self.estagios.append({
                'COD_EST': 99,
                'Q_DB': finalizada['qtd'],
                'SEQ_EST': finalizada['ultima_sequencia']+1,
            })
        pprint(self.estagios)

    def verifica_quantidade(self):
        self.estagio_selecionado = self.get_estagio_selecionado()
        proximo_estagio = self.get_proximo_estagio()
        pprint(self.estagio_selecionado)
        if self.qtd < 0:
            qtd_teste = -self.qtd
            qtd_estagio = proximo_estagio['Q_DB']
        else:
            qtd_teste = self.qtd
            qtd_estagio = self.estagio_selecionado['Q_DB']
        if qtd_estagio < qtd_teste:
            if self.qtd < 0:
                return (
                    f"Estágio posterior ao {self.estagio} do lote {self.lote} "
                    f"com quantidade {qtd_estagio} disponível para estorno, "
                    f"que é menor do que {qtd_teste}"
                )
            else:
                return (
                    f"Estágio {self.estagio} do lote {self.lote} "
                    f"com quantidade {qtd_estagio} disponível para baixa, "
                    f"que é menor do que {self.qtd}"
                )

    def get_estagio_selecionado(self):
        return next(
            estagio
            for estagio in self.estagios
            if estagio['COD_EST'] == self.estagio
        )

    def get_proximo_estagio(self):
        return next(
            estagio
            for estagio in self.estagios
            if estagio['SEQ_EST'] == self.estagio_selecionado['SEQ_EST'] + 1
        )

    def processa_estagios(self, estagios, estagio_selecionado):
        return [
            estagio['COD_EST']
            for estagio in estagios
            if estagio['SEQ_EST'] <= estagio_selecionado['SEQ_EST']
        ]

    def get_movimentacoes(self):
        estagios_filtrados = self.processa_estagios(self.estagios, self.estagio_selecionado)
        try:
            self.movimentacoes = movimentacao_de_lote.get_movimentacoes_estagios(
                cursor=self.cursor,
                lote=self.lote,
                estagios=estagios_filtrados,
            )
        except Exception as e:
            return f"Erro ao buscar movimentações do lote no estágio: {e}"
        if not self.movimentacoes:
            return "Só é possível inserir movimentação se já houver movimentação no lote"
        pprint(self.movimentacoes)

    def insere_movimentacao(self):
        estagio_modelo = self.movimentacoes[-1]['pcpc040_estconf']
        sequencia_modelo = self.movimentacoes[-1]['sequencia']
        self.sequencia_nova = (sequencia_modelo + 1) if self.estagio == estagio_modelo else 1
        try:
            movimentacao_de_lote.insere(
                cursor=self.cursor,
                lote=self.lote,
                estagio=self.estagio,
                qtd=self.qtd,
                estagio_modelo=estagio_modelo,
                sequencia_modelo=sequencia_modelo,
                sequencia_nova=self.sequencia_nova,
            )
        except Exception as e:
            return f"Erro ao inserir movimentação de lote: {e}"

    def corrige_usuario(self):
        try:
            movimentacao_de_lote.corrige_usuario_programa(
                cursor=self.cursor,
                lote=self.lote,
                estagio=self.estagio,
                sequencia=self.sequencia_nova,
                usuario=self.logged_in.user,
                programa=self.programa,
            )
        except Exception as e:
            return f"Erro ao corrigir o campo usuário: {e}"

    def process(self):
        for passo in [
            self.verifica_usuario,
            self.verifica_estagios,
            self.busca_qtd_finalizada,
            self.verifica_quantidade,
            self.get_movimentacoes,
            self.insere_movimentacao,
            self.corrige_usuario,
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
        self.lote = kwargs['lote']
        self.estagio = int(kwargs['estagio'])
        self.qtd = int(kwargs['qtd'])
        self.programa = kwargs['programa'] if 'programa' in kwargs else 'produz_lote'

    def get(self, request, *args, **kwargs):
        self.inicializa_variaveis(request, kwargs)
        return JsonResponse(self.response(self.process()), safe=False)
