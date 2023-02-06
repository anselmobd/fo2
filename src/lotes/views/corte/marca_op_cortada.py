from pprint import pprint

from django.http import JsonResponse
from django.views import View

from lotes.models.op import OpCortada


class MarcaOpCortada(View):

    def process(self, kwargs):
        op = kwargs['op']

        try:
            op_object = OpCortada.objects.get(op=op)
        except OpCortada.DoesNotExist:
            op_object = None

        if op_object:
            op_object.delete()
            return 'DESMARCADA'
        else:
            op_object = OpCortada(op=op)
            op_object.save()
            return 'MARCADA'

    def response(self, kwargs):
        try:
            status = self.process(kwargs)
            message = ""
        except Exception as e:
            status =  'ERRO'
            message = repr(e)
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.response(kwargs), safe=False)
