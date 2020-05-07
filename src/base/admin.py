from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoImagem, Imagem, Tamanho, Colaborador


class TipoImagemAdmin(admin.ModelAdmin):
    fields = ["nome", "slug", "descricao"]
    readonly_fields = ['slug']


class ImagemAdmin(admin.ModelAdmin):
    list_display = ["tipo_imagem", "descricao", "slug", "imagem"]
    fields = ["tipo_imagem", "descricao", "slug", "imagem"]
    readonly_fields = ['slug']


class TamanhoAdmin(admin.ModelAdmin):
    list_display = ["nome", "ordem"]
    ordering = ["ordem"]


class ColaboradorAdmin(admin.ModelAdmin):
    fields = [
        "user", "matricula", "nome", "nascimento", "cpf", "obs", "logged"]


intr_adm_site.register(TipoImagem, TipoImagemAdmin)
intr_adm_site.register(Imagem, ImagemAdmin)
intr_adm_site.register(Tamanho, TamanhoAdmin)
intr_adm_site.register(Colaborador, ColaboradorAdmin)
