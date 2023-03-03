from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from base.models import Colaborador

from lotes.models.op import OpComCorte


class MarcaOpCortada(PermissionRequiredMixin, View):

    def __init__(self, *args, **kwargs):
        super(MarcaOpCortada, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.pode_marcar_op_como_cortada'

    def process(self, request, kwargs):
        op = kwargs['op']

        try:
            op_object = OpComCorte.objects.get(op=op)
        except OpComCorte.DoesNotExist:
            op_object = None

        try:
            colab = Colaborador.objects.get(user__username=request.user.username)
        except Colaborador.DoesNotExist:
            colab = None

        if op_object:
            if op_object.pedido_fm_num == 0:
                op_object.delete()
                return 'DESMARCADA'
            else:
                raise AttributeError("Pedido FM já gerado")
        else:
            op_object = OpComCorte(
                op=op,
                cortado_colab=colab,
            )
            op_object.save()
            return 'MARCADA'

    def response(self, request, kwargs):
        try:
            status = self.process(request, kwargs)
            message = ""
        except Exception as e:
            status =  'ERRO'
            message = repr(e) if settings.DEBUG else ''
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.response(request, kwargs), safe=False)
