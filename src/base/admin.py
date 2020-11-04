from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import (
    Colaborador,
    Imagem,
    Requisicao,
    Tamanho,
    TipoImagem,
)


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
        "user", "matricula", "nome", "nascimento", "cpf", "obs",
        "logged", "quando", "ip_interno"
    ]
    list_display = [
        "user", "matricula", "nome", "cpf", "obs",
    ]
    search_fields = [
        "user__username", "matricula", "nome", "cpf", "obs",
    ]


class RequisicaoAdmin(admin.ModelAdmin):
    list_display = ["colaborador", "quando", "path_info"]
    fields = [
        "colaborador", "request_method", "path_info", "http_accept",
        "quando", "ip"
    ]


intr_adm_site.register(TipoImagem, TipoImagemAdmin)
intr_adm_site.register(Imagem, ImagemAdmin)
intr_adm_site.register(Tamanho, TamanhoAdmin)
intr_adm_site.register(Colaborador, ColaboradorAdmin)
intr_adm_site.register(Requisicao, RequisicaoAdmin)
