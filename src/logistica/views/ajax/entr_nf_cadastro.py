import json
from pprint import pprint

from django.http import HttpResponse

from utils.functions.cadastro import CNPJ

from logistica.models import NfEntrada


def entr_nf_cadastro(request, *args, **kwargs):
    result = {}

    try:
        cadastro = kwargs['cadastro']
        val_cnpj = CNPJ()
        if val_cnpj.validate(cadastro):
            cadastro = val_cnpj.cnpj
            result = NfEntrada.objects.filter(
                cadastro=cadastro
            ).values(
                'emissor', 'descricao', 'transportadora'
            ).order_by('-quando').first()
    except Exception:
        pass

    return HttpResponse(json.dumps(result), content_type="application/json")