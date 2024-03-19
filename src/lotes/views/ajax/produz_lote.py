from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from lotes.queries.lote import movimentacao_de_lote


class ProduzLote(View):

    ERROR_STATUS = "ERROR"
    OK_STATUS = "OK"


    def __init__(self):
        self._cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = db_cursor_so(self.request)
        return self._cursor 

    def get_movimentacoes(self, lote, estagio):
        try:
            self.movimentacoes = movimentacao_de_lote.get_movimentacoes(
                cursor=self.cursor,
                lote=lote,
                estagio=estagio,
            )
        except Exception as e:
            return f"Erro ao buscar movimentações do lote no estágio: {e}"

    def get_movimentacoes_estagio_anterior(self, lote, estagio):
        try:
            self.movimentacoes = movimentacao_de_lote.get_movimentacoes_estagio_anterior(
                cursor=self.cursor,
                lote=lote,
                estagio=estagio,
            )
        except Exception as e:
            return f"Erro ao buscar movimentações em estágios anteriores do lote no estágio: {e}"

    def process(self, kwargs):
        self.movimentacoes = None

        result_error = self.get_movimentacoes(
            lote=kwargs['lote'],
            estagio=kwargs['estagio'],
        )
        if result_error:
            return (self.ERROR_STATUS, result_error)

        if not self.movimentacoes:
            result_error = self.get_movimentacoes_estagio_anterior(
                lote=kwargs['lote'],
                estagio=kwargs['estagio'],
            )
            if result_error:
                return (self.ERROR_STATUS, result_error)

        if not self.movimentacoes:
            return (
                'ERROR',
                "Só é possível inserir movimentação se já houver movimentação no lote",
            )

        pprint(self.movimentacoes)

        try:
            movimentacao_de_lote.insere(
                cursor=self.cursor,
                lote=kwargs['lote'],
                estagio=kwargs['estagio'],
                qtd=kwargs['qtd'],
                estagio_modelo=self.movimentacoes[-1]['pcpc040_estconf'],
            )
            return ('OK', "OK!")
        except Exception as e:
            return ('ERROR',  f"Erro ao inserir movimentação de lote: {e}")
            

    def response(self, result):
        status, message = result
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        self.request = request
        result = self.process(kwargs)
        return JsonResponse(self.response(result), safe=False)
