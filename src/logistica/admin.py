from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'ativa', 'saida', 'entrega', 'confirmada',
                    'observacao']
    list_filter = ['ativa', 'saida', 'entrega', 'confirmada']
    search_fields = ['numero', 'observacao']
    ordering = ['-numero']
    fields = (('numero', 'ativa'), 'saida', 'entrega', 'confirmada',
              'observacao')
    readonly_fields = ['numero', 'ativa']


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
