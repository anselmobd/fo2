from pprint import pprint

from django.http import JsonResponse


def ajax_conserto_lote(request, lote):
    data = {'lote': lote}

    return JsonResponse(data, safe=False)
