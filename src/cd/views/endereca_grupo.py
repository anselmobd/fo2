from pprint import pprint

from django.urls import reverse

from o2.views.base.get_post import O2BaseGetPostView

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.functions.strings import str2int
from utils.functions.strings import re_split_non_empty

from cd.classes.palete import Plt
from cd.forms import EnderecaGrupoForm
from cd.queries.endereco import local_de_lote
from cd.queries.palete import get_paletes


class EnderecaGrupo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EnderecaGrupo, self).__init__(*args, **kwargs)
        self.template_name = 'cd/endereca_grupo.html'
        self.title_name = 'Endereça grupo'
        self.Form_class = EnderecaGrupoForm
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        palete_list = []
        def add_palete(val):
            if int(val) > 9999:
                local = local_de_lote(cursor, val)
                if local:
                    val = local[0]['palete']
            palete_list.append(Plt().mount(val))

        for item in re_split_non_empty(self.filtro, " ,;.\n"):
            if "-" in item:
                ini, fim, *_ = map(str2int, item.split("-"))
                for val in range(ini, fim+1):
                    add_palete(val)
            else:
                add_palete(item)

        data = [
            {'palete': palete}
            for palete in palete_list
        ]
        headers = [
            'Palete',
        ]
        fields = [
            'palete',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
        pprint(self.context)
