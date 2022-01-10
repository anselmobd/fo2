from pprint import pprint

from django.contrib import admin

from fo2.admin import intr_adm_site as site

from systextil.models import Empresa as ErpEmpresa

from .models import (
    Colaborador,
    Empresa,
    Imagem,
    Requisicao,
    Tamanho,
    TipoImagem,
)


@admin.register(TipoImagem, site=site)
class TipoImagemAdmin(admin.ModelAdmin):
    list_display = ["nome", "slug", "descricao"]
    fields = ["nome", "slug", "descricao"]
    readonly_fields = ['slug']


@admin.register(Imagem, site=site)
class ImagemAdmin(admin.ModelAdmin):
    list_filter = [
         "tipo_imagem"
    ]
    list_display = ["tipo_imagem", "descricao", "slug", "caminho", "imagem"]
    fields = ["tipo_imagem", "descricao", "slug", "caminho", "imagem"]
    readonly_fields = ['slug']


@admin.register(Tamanho, site=site)
class TamanhoAdmin(admin.ModelAdmin):
    list_display = ["nome", "ordem"]
    ordering = ["ordem"]


@admin.register(Colaborador, site=site)
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


@admin.register(Requisicao, site=site)
class RequisicaoAdmin(admin.ModelAdmin):
    list_display = ["quando", "colaborador", "request_method", "path_info", "ip"]
    fields = [
        "colaborador", "request_method", "path_info", "http_accept",
        "quando", "ip"
    ]


@admin.register(Empresa, site=site)
class EmpresaAdmin(admin.ModelAdmin):
    readonly_fields = ['numero', 'nome']

    def get_queryset(self, request):
        erp_empr = ErpEmpresa.objects.all().values()
        dict_erp_empr = {e['codigo_empresa']: e['nome_fantasia'] for e in erp_empr}

        fo2_empr = Empresa.objects.all().values()
        dict_fo2_empr = {e['numero']: e['nome'] for e in fo2_empr}

        excluir = dict(set(dict_fo2_empr.items())-set(dict_erp_empr.items()))
        for numero in excluir:
            exclui = Empresa.objects.get(numero=numero, nome=excluir[numero])
            exclui.delete()

        incluir = dict(set(dict_erp_empr.items())-set(dict_fo2_empr.items()))
        for numero in incluir:
            inclui = Empresa(numero=numero, nome=incluir[numero])
            inclui.save()

        return super(EmpresaAdmin, self).get_queryset(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
