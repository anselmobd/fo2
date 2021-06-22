import datetime
import json
from pprint import pprint

from django.db.models import Q
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
            cadastro_mask = val_cnpj.mask(cadastro)
            result = NfEntrada.objects.filter(
                Q(cadastro=cadastro) | Q(cadastro=cadastro_mask)
            ).values(
                'emissor', 'descricao', 'transportadora',
                'motorista', 'placa', 'quando'
            ).order_by('-quando').first()
            result.update({
                'cadastro': cadastro_mask,
            })
            result['quando'] = result['quando'].date()
            if result['quando'] != datetime.date.today():
                del(result['motorista'])
                del(result['placa'])
    except Exception:
        pass

    return HttpResponse(json.dumps(result, default=str), content_type="application/json")