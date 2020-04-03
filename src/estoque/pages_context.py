from pprint import pprint

from django.urls import reverse

import estoque.models


def get_estoque_movimentos(context):
    movimentos = None
    if context.environ['PATH_INFO'] in [
            reverse('apoio_ao_erp'),
            reverse('estoque:index')]:
        movimentos = estoque.models.TipoMovStq.objects.filter(menu=True)
    return {'estoque_movimentos': movimentos}
