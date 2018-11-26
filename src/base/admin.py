from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoImagem, Imagem


class TipoImagemAdmin(admin.ModelAdmin):
    fields = ["nome", "slug", "descricao"]
    readonly_fields = ['slug']


class ImagemAdmin(admin.ModelAdmin):
    list_display = ["tipo_imagem", "descricao", "slug", "imagem"]
    fields = ["tipo_imagem", "descricao", "slug", "imagem"]
    readonly_fields = ['slug']


intr_adm_site.register(TipoImagem, TipoImagemAdmin)
intr_adm_site.register(Imagem, ImagemAdmin)
