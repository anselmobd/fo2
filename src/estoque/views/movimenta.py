from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.http import JsonResponse
from django.views import View

from estoque import classes


class Movimenta(PermissionRequiredMixin, View):

    template_name = 'estoque/ajax/movimenta.html'

    def __init__(self):
        self.permission_required = 'estoque.can_transferencia'

    def get(self, request, **kwargs):

        self.data = kwargs

        cursor = connections['so'].cursor()
        erro = False

        try:
            self.data['quantidade'] = int(self.data['quantidade'])
        except Exception as e:
            erro = True
            descricao_erro = 'Quantidade deve ser numérica'

        if not erro:
            if self.data['num_doc'] == '-':
                self.data['num_doc'] = None
            if self.data['descricao'] == '-':
                self.data['descricao'] = None
            self.data['cria_num_doc'] = \
                self.data['cria_num_doc'].upper() == 'S'

            try:
                transf = classes.Transfere(
                    cursor,
                    request,
                    *(self.data[f] for f in [
                        'tip_mov', 'nivel', 'ref', 'tam', 'cor', 'qtd',
                        'deposito_origem', 'deposito_destino',
                        'nova_ref', 'novo_tam', 'nova_cor',
                        'num_doc', 'descricao', 'cria_num_doc']),
                )
            except Exception as e:
                erro = True
                descricao_erro = str(e)

            self.data.update({
                'num_doc': transf.num_doc,
            })
        if erro:
            self.data.update({
                'result': 'ERR',
                'descricao_erro': descricao_erro,
            })
            return JsonResponse(self.data, safe=False)

        self.data.update({
            'result': 'OK',
        })
        return JsonResponse(self.data, safe=False)
