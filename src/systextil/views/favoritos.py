from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from systextil.forms.usuario import FavoritosForm
from systextil.models.base import Usuario
from systextil.queries import favoritos



class Favoritos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Favoritos, self).__init__(*args, **kwargs)
        self.template_name = 'systextil/favoritos.html'
        self.title_name = 'Favoritos de usuário'
        self.Form_class = FavoritosForm
        self.cleaned_data2self = True
        self.por_pagina = 20

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.login = self.login.upper()

        try:
            _ = Usuario.objects_all.get(
                usuario=self.login, empresa=self.empresa)
        except Usuario.DoesNotExist:
            self.context.update({
                'msg': f"Usuário '{self.login}' na empresa '{self.empresa}' inexistente",
            })
            return

        dados = favoritos.query(
            self.cursor,
            self.empresa,
            self.login,
        )
        pprint(dados)
        if len(dados) == 0:
            return
        
        dados = paginator_basic(dados, self.por_pagina, self.page)

        self.context.update({
            'headers': [
                'Programa',
                'Descrição',
            ],
            'fields': [
                'programa',
                'descricao',
            ],
            'data': dados,
        })
