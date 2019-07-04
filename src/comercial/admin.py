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
    list_display = ['__str__', 'venda_mensal', 'multiplicador']


class MetaEstoqueTamanhoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'quantidade']


class MetaEstoqueCorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'quantidade']


intr_adm_site.register(MetaEstoque, MetaEstoqueAdmin)
intr_adm_site.register(MetaEstoqueTamanho, MetaEstoqueTamanhoAdmin)
intr_adm_site.register(MetaEstoqueCor, MetaEstoqueCorAdmin)
