import locale
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from lotes.forms.analise import CdBonusViewForm


class CdBonusView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CdBonusView, self).__init__(*args, **kwargs)
        self.Form_class = CdBonusViewForm
        self.template_name = 'lotes/analise/cd_bonus.html'
        self.title_name = 'Análise - Produzido - CD (bônus)'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True
        self.get_args = ['data']

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        dados = []
        # xyz.query(
        #     self.cursor,
        #     data=data,
        # )

        if not dados:
            return

        for row in dados:
            row['op|TARGET'] = '_blank'
            row['op|A'] = reverse(
                'producao:op__get', args=[row['op']])

        headers = [
            'Usuário',
            'Referência',
            'Quantidade',
        ]
        fields = [
            'usuario',
            'ref',
            'qtd',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
            'style': {
                3: 'text-align: right;',
            },
        })
