import re
from datetime import datetime
from pprint import pprint

from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from fo2.connections import db_cursor_so

from base.models import Colaborador
from utils.functions.strings import only_digits

from lotes.queries.pedido import ped_inform
from lotes.models.op import OpComCorte
from lotes.queries.pedido.ped_alter import (
    altera_pedido,
    altera_pedido_itens,
)
from lotes.queries.op import ped_cli_por_cliente
from lotes.queries.pedido.mensagem_nf import cria_mens_nf
from lotes.views.prepara_pedido_compra_matriz import cria_pedido_compra_matriz


__all__ = ['PreparaPedidoOpCortada']


class PreparaPedidoOpCortada(View):

    def process(self, request, kwargs):
        cursor = db_cursor_so(request)

        data = datetime.strptime(kwargs['data'], '%Y-%m-%d').date()
        cliente = kwargs['cliente']
        pedido = kwargs['pedido']

        try:
            colab = Colaborador.objects.get(user__username=request.user.username)
        except Colaborador.DoesNotExist:
            colab = None

        try:
            pedido = int(only_digits(pedido))
        except ValueError:
            return ('ERRO', "Pedido inválido!")

        clientes = ped_cli_por_cliente.get_cached(
            cursor, dt=data, cliente_slug=cliente)

        if not clientes:
            return ('ERRO', f"Dados de '{cliente}' não encontrados!")
    
        op_objects = OpComCorte.objects.filter(pedido_fm_num=pedido).values('op')
        if op_objects:
            ops_pedido = [
                row['op']
                for row in op_objects
            ]
            if set(ops_pedido) != clientes[cliente]['ops']:
                return ('ERRO', "Número de pedido já utilizado para outras OPs!")

        dados = ped_inform(cursor, pedido, empresa=3)
        if not dados:
            return ('ERRO', "Pedido não encontrado!")
        if dados[0]['COD_CANCELAMENTO'] != 0:
            return ('ERRO', "Pedido cancelado!")
        if dados[0]['NF'] is not None:
            return ('ERRO', "Pedido faturado!")
        if dados[0]['OBSERVACAO']:
            if re.search('^\[MPCFM\] ', dados[0]['OBSERVACAO']):
                return ('ERRO', "Pedido já preparado!")

        #   exemplos de observações:
        # [MOPCFM] Movimentacao de OPs Cortadas da Filial para Matriz; Data: 2022-03-16
        # Produção para estoque: OP(34082, 34307, 34339, 34262, 34297)
        #   ou
        # [MOPCFM] Movimentacao de OPs Cortadas da Filial para Matriz; Data: 2022-03-16
        # Produção para o cliente Renner: Pedido(5214524)-OP(34023), Pedido(5214547)-OP(34027)

        if cliente == 'estoque':
            observacao = (
                f"[MOPCFM] Movimentacao de OPs Cortadas da Filial para Matriz; Data: {data}",
                f"Producao para estoque: {clientes[cliente]['obs']}",
            )
        else:
            observacao = (
                f"[MOPCFM] Movimentacao de OPs Cortadas da Filial para Matriz; Data: {data}",
                f"Producao para o cliente {cliente.capitalize()}: {clientes[cliente]['obs']}",
            )

        cria_mens_nf(cursor, pedido, observacao)

        altera_pedido_itens(cursor, pedido, 302, 'RJ', clientes[cliente]['itens'])

        qtd_itens = 0
        for row in clientes[cliente]['itens']:
            qtd_itens += row['mov_qtd']
        altera_pedido(cursor, data, pedido, 3, qtd_itens, "\n".join(observacao))

        ops_com_corte = OpComCorte.objects.filter(op__in=clientes[cliente]['ops'])
        for op_com_corte in ops_com_corte:
            op_com_corte.pedido_fm_num = pedido
            op_com_corte.pedido_fm_colab = colab
            op_com_corte.pedido_fm_quando = timezone.now()
            op_com_corte.save()

        if not cria_pedido_compra_matriz(cursor, pedido):
            return ('ERRO', "Algum erro ocorreu durante a criação do pedido de compra!")

        return ('OK', "OK!")

    def response(self, result):
        status, message = result
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        result = self.process(request, kwargs)
        return JsonResponse(self.response(result), safe=False)
