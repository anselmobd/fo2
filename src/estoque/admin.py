from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMovStq, DocMovStq, MovStq


class TipoMovStqAdmin(admin.ModelAdmin):
    list_display = [
        "codigo", "descricao", "trans_saida", "trans_entrada", "menu", "ordem",
        "renomeia", "unidade"]
    ordering = ["ordem"]


class DocMovStqAdmin(admin.ModelAdmin):

    def num_doc(self, obj):
        return obj.num_doc

    num_doc.short_description = 'Número de documento'

    list_display = ["num_doc", "descricao"]


class MovStqAdmin(admin.ModelAdmin):
    list_display = ["tipo_mov", "__str__", "usuario"]
    readonly_fields = ['hora']
    search_fields = [
        'deposito_destino',
        'deposito_origem',
        'documento__descricao',
        'documento__id',
        'item__produto__referencia',
        'item__tamanho__tamanho__nome',
        'item__cor__cor',
        'novo_item__produto__referencia',
        'novo_item__tamanho__tamanho__nome',
        'novo_item__cor__cor',
        'obs',
        'quantidade',
        'usuario__username',
    ]


intr_adm_site.register(TipoMovStq, TipoMovStqAdmin)
intr_adm_site.register(DocMovStq, DocMovStqAdmin)
intr_adm_site.register(MovStq, MovStqAdmin)
