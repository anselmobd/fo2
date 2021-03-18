from django.contrib import admin
# from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from fo2.admin import intr_adm_site

from .forms import ProdutoForm
from .models import (
    Composicao, 
    ComposicaoLinha, 
    FichaTecnica,
    GtinLog, 
    GtinRange, 
    Produto,
    ProdutoCor, 
    ProdutoItem, 
    ProdutoTamanho,
)


# class ProdutoCorInline(NestedStackedInline):
#     model = ProdutoCor
#     extra = 0
#     fields = ['cor']


class GtinRangeAdmin(admin.ModelAdmin):
    search_fields = ['codigo']
    ordering = ['ordem']
    fields = ['ordem', 'pais', 'codigo']


# class ProdutoAdmin(NestedModelAdmin):
class ProdutoAdmin(admin.ModelAdmin):
    form = ProdutoForm
    # inlines = [ProdutoCorInline]
    search_fields = ['referencia']
    ordering = ['referencia']


class ProdutoCorAdmin(admin.ModelAdmin):
    search_fields = ['produto__referencia', 'cor']
    ordering = ['produto__referencia', 'cor']


class ProdutoTamanhoAdmin(admin.ModelAdmin):
    search_fields = ['produto__referencia', 'tamanho__nome']
    ordering = ['produto__referencia', 'tamanho__ordem']


class ProdutoItemAdmin(admin.ModelAdmin):
    search_fields = [
        'produto__referencia', 'cor__cor', 'tamanho__tamanho__nome']
    ordering = [
        'produto__referencia', 'cor__cor', 'tamanho__tamanho__ordem']


class ComposicaoAdmin(admin.ModelAdmin):
    ordering = ['descricao']


class ComposicaoLinhaAdmin(admin.ModelAdmin):
    ordering = ['composicao', 'ordem']


class GtinLogAdmin(admin.ModelAdmin):
    pass

class FichaTecnicaAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'uploaded_at', 'habilitada']
    readonly_fields = ['uploaded_at']
    search_fields = ['referencia']
    ordering = ['referencia', 'uploaded_at']


intr_adm_site.register(Composicao, ComposicaoAdmin)
intr_adm_site.register(ComposicaoLinha, ComposicaoLinhaAdmin)
intr_adm_site.register(FichaTecnica, FichaTecnicaAdmin)
intr_adm_site.register(GtinLog, GtinLogAdmin)
intr_adm_site.register(GtinRange, GtinRangeAdmin)
intr_adm_site.register(Produto, ProdutoAdmin)
intr_adm_site.register(ProdutoCor, ProdutoCorAdmin)
intr_adm_site.register(ProdutoItem, ProdutoItemAdmin)
intr_adm_site.register(ProdutoTamanho, ProdutoTamanhoAdmin)
