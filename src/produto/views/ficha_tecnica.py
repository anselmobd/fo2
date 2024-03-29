from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

import produto.forms
import produto.models
import produto.queries


class FichaTecnica(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FichaTecnica, self).__init__(*args, **kwargs)
        self.Form_class = produto.forms.ReferenciaNoneForm
        self.template_name = 'produto/ficha_tecnica.html'
        self.title_name = 'Ficha técnica'

    def get_ftec_refs(self):
        dados_refs = produto.models.FichaTecnica.objects.filter(
            habilitada=True,
        ).distinct().values('referencia')
        ftec_refs = tuple([r['referencia'] for r in dados_refs])
        if len(ftec_refs) == 0:
            self.context.update({
                'erro': 'Nenhuma ficha cadastrada',
            })
        return ftec_refs

    def mount_context(self):
        ref = self.form.cleaned_data['ref']

        ftec_refs = self.get_ftec_refs()
        if not ftec_refs:
            return

        fichas = produto.models.FichaTecnica.objects

        cursor = db_cursor_so(self.request)
        if ref == '':
            ref_linha = produto.queries.dict_ref_val(cursor, ftec_refs, 'linha')
        else:
            ref_linha = produto.queries.dict_ref_val(cursor, ref, 'linha')
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
            row['referencia|LINK'] = f'/media/{row["ficha"]}'
            row['referencia|TARGET'] = '_blank'
            row['linha'] = ref_linha[row['referencia']]

        self.context.update({
            'headers': ['Linha', 'Referência', 'Tipo', 'Data/hora'],
            'fields': ['linha', 'referencia', 'tipo__tipo', 'uploaded_at'],
            'data': fichas,
        })
