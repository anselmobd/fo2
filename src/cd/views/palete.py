from pprint import pprint

from django.urls import reverse

from base.paginator import paginator_basic
from o2.views.base.get import O2BaseGetView

from fo2.connections import db_cursor_so

from geral.functions import has_permission

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
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'safe': ['print'],
        })
