from pprint import pprint

from o2.views.base.get_post import O2BaseGetPostView

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.functions.strings import (
    is_only_digits,
    split_non_empty,
)
from cd.classes.palete import Plt
from cd.forms import EnderecaGrupoForm
from cd.queries.endereco import (
    get_palete,
    local_de_lote,
    palete_set_endereco,
)


class EnderecaGrupo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EnderecaGrupo, self).__init__(*args, **kwargs)
        self.template_name = 'cd/endereca_grupo.html'
        self.title_name = 'Endereça grupo'
        self.Form_class = EnderecaGrupoForm
        self.cleaned_data2self = True

    def get_end_atuais(self, palete_list):
        paletes = get_palete(self.cursor, palete_list)
        return {
            p['cod_container']: p['endereco']
            for p in paletes
        }

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

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

        for line in map(str.strip, split_non_empty(self.paletes, "\n")):
            palete = None
            if is_only_digits(line):
                if int(line) > 9999:
                    local = local_de_lote(self.cursor, line)
                    if local:
                        palete = local[0]['palete']
                    else:
                        palete = f"Não é lote: {line}"
            if not palete:               
                palete = Plt().mount(line)
                if line[-1].isalpha():
                    if palete[-1] != line[-1].upper():
                        palete = f"Verificador inválido: {line}"
            palete_list.append(palete)

        if len(end_list) != len(palete_list):
            self.context.update({
                'msgerr': "Número de paletes diferente do número de endereços"
            })

        end_atuais = self.get_end_atuais(palete_list)

        if 'endereca' in self.request.POST:
            for num, palete in enumerate(palete_list):
                if end_list[num] != end_atuais[palete]:
                    palete_set_endereco(self.cursor, palete, end_list[num])

        end_atuais = self.get_end_atuais(palete_list)

        data = []
        for num in range(max(len(end_list), len(palete_list))):
            data.append({
                'num': num + 1,
                'palete': palete_list[num] if num < len(palete_list) else "?",
                'endereco': end_list[num] if num < len(end_list) else "?",
                'atual': end_atuais.get(palete_list[num], "?") if num < len(palete_list) else "?"
            })
        headers = [
            '#',
            'Palete',
            'Endereço',
            'Atual',
        ]
        fields = [
            'num',
            'palete',
            'endereco',
            'atual',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

