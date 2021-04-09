from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import *


class ModeloPassadoAdmin(admin.ModelAdmin):
    fields = ['nome', 'padrao']


class ModeloPassadoPeriodoAdmin(admin.ModelAdmin):
    fields = ['modelo', 'ordem', 'meses', 'peso']
    ordering = ['modelo__nome', 'ordem']


intr_adm_site.register(ModeloPassado, ModeloPassadoAdmin)
intr_adm_site.register(ModeloPassadoPeriodo, ModeloPassadoPeriodoAdmin)


class MetaEstoqueAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'venda_mensal', 'multiplicador', 'meta_estoque']


class MetaEstoqueTamanhoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'quantidade', 'ordem']


class MetaEstoqueCorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'quantidade']


class MetaModeloReferenciaAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    ordering = ['modelo', 'referencia']


intr_adm_site.register(MetaEstoque, MetaEstoqueAdmin)
intr_adm_site.register(MetaEstoqueTamanho, MetaEstoqueTamanhoAdmin)
intr_adm_site.register(MetaEstoqueCor, MetaEstoqueCorAdmin)
intr_adm_site.register(MetaModeloReferencia, MetaModeloReferenciaAdmin)


class MetaFaturamentoAdmin(admin.ModelAdmin):
    list_display = ['data', 'faturamento', 'ajuste']
    ordering = ['-data']


class PendenciaFaturamentoAdmin(admin.ModelAdmin):
    list_display = ['mes', 'ordem', 'cliente', 'entrega']
    ordering = ['mes', 'ordem']
    # 'mes', 'ordem', 'cliente', 'pendencia', 'valor', 'entrega',
    # 'responsavel', 'obs',


intr_adm_site.register(MetaFaturamento, MetaFaturamentoAdmin)
intr_adm_site.register(PendenciaFaturamento, PendenciaFaturamentoAdmin)
