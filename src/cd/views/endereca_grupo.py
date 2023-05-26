from pprint import pprint

from django.urls import reverse

from base.paginator import paginator_basic
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
        self.title_name = 'Paletes'
        self.Form_class = EnderecaGrupoForm
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

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

        data = get_paletes(cursor, palete_list=palete_list)

        data = paginator_basic(data, 100, page)

        link_ids = []
        for row in data:
            row['cod_container|LINK'] = reverse(
                'cd:conteudo_local',
                args=[row['cod_container']]
            )
            if not row['endereco_container']:
                row['endereco_container'] = '-'
            if not row['ultima_inclusao']:
                row['ultima_inclusao'] = '-'
            palete = row['cod_container']
            link_ids.append(palete)
            row['print'] = f"""
                <a title="Imprime etiqueta" href="#" id="run_{palete}" onclick="PaletePrint('{palete}');return false;"><span
                  class="glyphicon glyphicon-print" aria-hidden="true"></span></a><span
                    class="glyphicon glyphicon-print" id="running_{palete}" style="display:none;color:grey" aria-hidden="true"></span><span
                      class="glyphicon glyphicon-ok-sign" id="runok_{palete}" style="display:none;color:darkgreen" aria-hidden="true"></span><span
                        class="glyphicon glyphicon-alert" id="runerr_{palete}" style="display:none;color:darkred" aria-hidden="true"></span>
            """

        headers = [
            'Palete',
            'Endereço',
            'Nº Lotes',
            'Última inclusão',
        ]
        fields = [
            'cod_container',
            'endereco_container',
            'lotes',
            'ultima_inclusao',
        ]

        if (
            self.request.user.is_authenticated
            and has_permission(self.request, 'cd.imprime_etq_palete')
        ):
            headers.append('Imprime')
            fields.append('print')
            self.context['can_print'] = True

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'safe': ['print'],
            'link_ids': link_ids,
        })
