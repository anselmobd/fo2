from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from base.models import Colaborador

from lotes.models.op import OpComCorte
from lotes.queries.producao.romaneio_corte import op_cortada


__all__ = ['MarcaOpCortada']


class MarcaOpCortada(PermissionRequiredMixin, View):

    def __init__(self, *args, **kwargs):
        super(MarcaOpCortada, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.pode_marcar_op_como_cortada'

    def process(self, request, kwargs):
        op = kwargs['op']
        acao = None

        try:
            op_object = OpComCorte.objects.get(op=op)
        except OpComCorte.DoesNotExist:
            op_object = None

        try:
            colab = Colaborador.objects.get(user__username=request.user.username)
        except Colaborador.DoesNotExist:
            colab = None

        if op_object:
            if op_object.pedido_fm_num:
                raise AttributeError("Pedido FM já gerado")
            else:
                op_object.delete()
                op_object = None
                acao = 'DESMARCADA'
        else:
            self.cursor = db_cursor_so(self.request)
            dados_op_cortada = op_cortada.query(
                self.cursor,
                op1=op,
            )

            op_object = OpComCorte(
                op=op,
                cortada_colab=colab,
                cortada_quando=dados_op_cortada[0]['dt_corte'],
            )
            op_object.save()
            acao = 'MARCADA'
        return acao, op_object

    def response(self, request, kwargs):
        result = {}
        try:
            result['status'], op_object = self.process(request, kwargs)
            if op_object:
                result['cortada_colab'] = op_object.cortada_colab.user.username
                result['cortada_quando'] = op_object.cortada_quando.date().strftime("%d/%m/%Y")
                result['when'] = op_object.when.strftime('%d/%m/%Y %H:%M:%S')
        except Exception as e:
            result['status'] =  'ERRO'
            result['message'] = repr(e) if settings.DEBUG else ''
        return result

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.response(request, kwargs), safe=False)
