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

        fixo, *variavel = self.endereco.split("|")
        try:
            inicio, *final = variavel[0].split("-")
            inicio = int(inicio)
            final = int(final[0])
            incr = final - inicio
            incr = incr // abs(incr)
        except Exception:
            self.context.update({
                'msgerr': "Mascara de endereço inválida"
            })
            return

        end_list = []
        for num in range(inicio, final+incr, incr):
            end_list.append(f"{fixo}{num}")

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

        if len(end_list) != len(palete_list):
            self.context.update({
                'msgerr': "Número de paletes diferente do número de endereços"
            })

        data = []
        for num in range(max(len(end_list), len(palete_list))):
            data.append({
                'num': num + 1,
                'palete': palete_list[num] if num < len(palete_list) else "?",
                'endereco': end_list[num] if num < len(end_list) else "?",
            })
        headers = [
            '#',
            'Palete',
            'Endereço',
        ]
        fields = [
            'num',
            'palete',
            'endereco',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
        pprint(self.context)
