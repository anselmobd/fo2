from pprint import pprint

from django.urls import reverse

from o2.views.base.get_post import O2BaseGetPostView

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.functions.strings import str2int
from utils.functions.strings import re_split_non_empty
from utils.functions.strings import is_only_digits

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

        for line in map(str.strip, self.paletes.split("\n")):
            palete = None
            if is_only_digits(line):
                if int(line) > 9999:
                    local = local_de_lote(cursor, line)
                    if local:
                        palete = local[0]['palete']
                    else:
                        palete = f"!!! {line}"
            if not palete:
                palete = Plt().mount(line)
            palete_list.append(palete)

        data = [
            {
                'num': num + 1,
                'palete': palete,
            }
            for num, palete in enumerate(palete_list)
        ]
        headers = [
            '#',
            'Palete',
        ]
        fields = [
            'num',
            'palete',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
        pprint(self.context)
