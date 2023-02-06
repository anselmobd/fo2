from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from base.models import Colaborador

from lotes.models.op import OpCortada


class MarcaOpCortada(PermissionRequiredMixin, View):

    def __init__(self, *args, **kwargs):
        super(MarcaOpCortada, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.pode_marcar_op_como_cortada'

    def process(self, request, kwargs):
        op = kwargs['op']

        try:
            op_object = OpCortada.objects.get(op=op)
        except OpCortada.DoesNotExist:
            op_object = None

        try:
            colab = Colaborador.objects.get(user__username=request.user.username)
        except Colaborador.DoesNotExist:
            colab = None

        if op_object:
            op_object.delete()
            return 'DESMARCADA'
        else:
            op_object = OpCortada(
                op=op,
                colaborador=colab,
            )
            op_object.save()
            return 'MARCADA'

    def response(self, request, kwargs):
        try:
            status = self.process(request, kwargs)
            message = ""
        except Exception as e:
            status =  'ERRO'
            message = repr(e)
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.response(request, kwargs), safe=False)
