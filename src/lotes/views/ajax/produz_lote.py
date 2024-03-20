from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from lotes.queries.lote import movimentacao_de_lote


class ProduzLote(View):

    ERROR_STATUS = "ERROR"
    OK_STATUS = "OK"

    def get_movimentacoes(self):
        try:
            self.movimentacoes = movimentacao_de_lote.get_movimentacoes_ate_estagio(
                cursor=self.cursor,
                lote=self.lote,
                estagio=self.estagio,
            )
        except Exception as e:
            return f"Erro ao buscar movimentações do lote no estágio: {e}"
        if not self.movimentacoes:
            return "Só é possível inserir movimentação se já houver movimentação no lote"

    def insere_movimentacao(self):
        try:
            movimentacao_de_lote.insere(
                cursor=self.cursor,
                lote=self.lote,
                estagio=self.estagio,
                qtd=self.qtd,
                estagio_modelo=self.movimentacoes[-1]['pcpc040_estconf'],
            )
        except Exception as e:
            return f"Erro ao inserir movimentação de lote: {e}"

    def process(self):
        result_error = self.get_movimentacoes()
        if result_error:
            return (self.ERROR_STATUS, result_error)

        pprint(self.movimentacoes)

        result_error = self.insere_movimentacao()
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
        self.lote=kwargs['lote']
        self.estagio=kwargs['estagio']
        self.qtd=kwargs['qtd']
        self.movimentacoes = None

    def get(self, request, *args, **kwargs):
        self.inicializa_variaveis(request, kwargs)
        return JsonResponse(self.response(self.process()), safe=False)
