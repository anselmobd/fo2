from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoImagem


class TipoImagemAdmin(admin.ModelAdmin):
    fields = ["nome", "slug", "descricao"]
    readonly_fields = ['slug']


intr_adm_site.register(TipoImagem, TipoImagemAdmin)
