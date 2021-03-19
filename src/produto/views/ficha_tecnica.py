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

        dados_refs = produto.models.FichaTecnica.objects.distinct().values('referencia')
        refs = tuple([r['referencia'] for r in dados_refs])

        if len(refs) == 0:
            self.context.update({
                'erro': 'Nenhuma ficha cadastrada',
            })
            return

        fichas = produto.models.FichaTecnica.objects

            cursor = db_cursor_so(self.request)
        if ref == '':
            ref_linha = produto.queries.dict_ref_linha(cursor, refs)
        else:
            ref_linha = produto.queries.dict_ref_linha(cursor, ref)
            fichas = fichas.filter(
                referencia=ref,
            )

        if not ref_linha:
                self.context.update({
                    'erro': 'Referência não encontrada',
                })
                return

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
