from pprint import pprint

from django.urls import reverse

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from fo2.connections import db_cursor_so

from cd.queries.palete import get_paletes


class Palete(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

        data = get_paletes(cursor)

        data = paginator_basic(data, 100, page)

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
            row['print'] = f"""
                <a title="Imprime etiqueta" href="#" id="run_{palete}" onclick="PaletePrint('{palete}');return false;"><span
                  class="glyphicon glyphicon-print" aria-hidden="true"></span></a><span
                    class="glyphicon glyphicon-print" id="running_{palete}" style="display:none;color:grey" aria-hidden="true"></span><span
                      class="glyphicon glyphicon-ok-sign" id="runok_{palete}" style="display:none;color:darkgreen" aria-hidden="true"></span><span
                        class="glyphicon glyphicon-alert" id="runerr_{palete}" style="display:none;color:darkred" aria-hidden="true"></span>
            """

        self.context.update({
            'headers': [
                'Palete',
                'Endereço',
                'Nº Lotes',
                'Última inclusão',
                'Imprime',
            ],
            'fields': [
                'cod_container',
                'endereco_container',
                'lotes',
                'ultima_inclusao',
                'print',
            ],
            'data': data,
            'safe': ['print'],
        })
