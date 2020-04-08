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

    def get(
            self,
            request,
            tip_mov,
            nivel,
            ref,
            tam,
            cor,
            quantidade,
            deposito_origem,
            deposito_destino,
            nova_ref,
            novo_tam,
            nova_cor,
            num_doc,
            descricao,
            cria_num_doc,
            ):

        data = {
            'tip_mov': tip_mov,
            'nivel': nivel,
            'ref': ref,
            'tam': tam,
            'cor': cor,
            'quantidade': quantidade,
            'deposito_origem': deposito_origem,
            'deposito_destino': deposito_destino,
            'nova_ref': nova_ref,
            'novo_tam': novo_tam,
            'nova_cor': nova_cor,
            'num_doc': num_doc,
            'descricao': descricao,
            'cria_num_doc': cria_num_doc,
        }

        cursor = connections['so'].cursor()
        erro = False

        try:
            quantidade = int(quantidade)
        except Exception as e:
            erro = True
            descricao_erro = 'Quantidade deve ser numérica'

        if not erro:
            if num_doc == '-':
                num_doc = None
            if descricao == '-':
                descricao = None
            if cria_num_doc == '-':
                cria_num_doc = False

            try:
                transf = classes.Transfere(
                    cursor,
                    tip_mov,
                    nivel,
                    ref,
                    tam,
                    cor,
                    quantidade,
                    deposito_origem,
                    deposito_destino,
                    nova_ref,
                    novo_tam,
                    nova_cor,
                    num_doc,
                    descricao,
                    request,
                    cria_num_doc,
                )
            except Exception as e:
                erro = True
                descricao_erro = str(e)

        if erro:
            data.update({
                'result': 'ERR',
                'descricao_erro': descricao_erro,
            })
            return JsonResponse(data, safe=False)

        data.update({
            'result': 'OK',
        })
        return JsonResponse(data, safe=False)
