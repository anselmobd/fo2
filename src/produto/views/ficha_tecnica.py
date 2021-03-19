from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import produto.forms
import produto.models
import produto.queries


class FichaTecnica(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FichaTecnica, self).__init__(*args, **kwargs)
        self.Form_class = produto.forms.ReferenciaNoneForm
        self.template_name = 'produto/ficha_tecnica.html'
        self.title_name = 'Ficha técnica'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']

        fichas = produto.models.FichaTecnica.objects
        if ref != '':
            cursor = db_cursor_so(self.request)

            data = produto.queries.ref_inform(cursor, ref)
            if len(data) == 0:
                self.context.update({
                    'erro': 'Referência não encontrada',
                })
                return

            fichas = fichas.filter(
                referencia=ref,
            )

        fichas = fichas.filter(
            habilitada=True,
        ).order_by(
            'referencia',
        ).values(
            'referencia',
            'tipo__tipo',
            'uploaded_at',
            'ficha',
        )

        self.context.update({
            'count': len(fichas),
        })

        for row in fichas:
            row['tipo__tipo|LINK'] = f'/media/{row["ficha"]}'
            row['tipo__tipo|TARGET'] = '_blank'

        self.context.update({
            'headers': ['Referência', 'Tipo', 'Data/hora'],
            'fields': ['referencia', 'tipo__tipo', 'uploaded_at'],
            'data': fichas,
        })
