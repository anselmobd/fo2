from django.contrib import admin

from fo2.admin import intr_adm_site
from logistica.models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'ativa', 'saida', 'entrega', 'confirmada',
                    'observacao']
    list_filter = ['ativa', 'saida', 'entrega', 'confirmada']
    search_fields = ['numero', 'observacao']
    ordering = ('-numero',)
    readonly_fields = ('ativa',)


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
