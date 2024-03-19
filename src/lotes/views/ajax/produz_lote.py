from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from lotes.queries.lote import movimentacao_de_lote


class ProduzLote(View):

    def __init__(self):
        self._cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = db_cursor_so(self.request)
        return self._cursor 

    def process(self, kwargs):
        try:
            movimentacao_de_lote.insere(
                self.cursor, kwargs['lote'], kwargs['estagio'], kwargs['qtd'])
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
