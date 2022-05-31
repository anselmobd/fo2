from pprint import pprint

from django.db.models import Q

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)

from cd.forms import ListaLoteInventForm


class ListaLoteInvent(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ListaLoteInvent, self).__init__(*args, **kwargs)
        self.Form_class = ListaLoteInventForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/lista_lotes_invent.html'
        self.title_name = 'Lista lotes inventariados'
        self.por_pagina = 20

    def mount_context(self):
        data = InventarioLote.objects.filter(
            inventario=self.inventario
        )

        if self.filtro:
            data = data.filter(
                Q(lote__contains=self.filtro) |
                Q(usuario__username__icontains=self.filtro)
            )

        data = data.order_by(
            '-quando',
        ).values(
            'lote',
            'quantidade',
            'usuario__username',
            'quando',
        )
        qtd_invent = len(data)

        data = paginator_basic(data, self.por_pagina, self.page)

        fields = {
            'lote': 'Lote',
            'quantidade': 'Quantidade',
            'usuario__username': 'Usuário',
            'quando': 'Quando',
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            'qtd_invent': qtd_invent,
            'por_pagina': self.por_pagina,
        })
