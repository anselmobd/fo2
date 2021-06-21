import json
from pprint import pprint

from django.http import HttpResponse

from logistica.models import NfEntrada


def entr_nf_cadastro(request, *args, **kwargs):
    try:
        cadastro = kwargs['cadastro']
        result = NfEntrada.objects.filter(
            cadastro=cadastro
        ).values(
            'emissor', 'descricao', 'transportadora'
        ).order_by('-quando').first()
    except Exception:
        result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")