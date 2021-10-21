from pprint import pprint

from django.http import JsonResponse

import email_signature.classes as classes
import email_signature.models as models


def gerar_assinatura(request, id):
    data = {
        'id': id,
    }

    try:
        conta = models.Account.objects.get(id=id)
    except Exception as e:
        data.update({
            'result': 'Erro',
            'descricao_erro': f'Erro ao buscar conta {id}',
        })
        return JsonResponse(data, safe=False)

    erro, msg = classes.assinatura.GeraAssinatura(conta).exec()
    if erro:
        data.update({
            'result': erro,
            'descricao_erro': msg,
        })
    else:
        data.update({
            'result': 'OK',
        })

    return JsonResponse(data, safe=False)
