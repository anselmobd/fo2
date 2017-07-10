from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'faturamento',
                    'cod_status', 'msg_status', 'ativa',
                    'saida', 'entrega', 'confirmada', 'observacao']
    list_filter = ['ativa', 'saida', 'entrega', 'confirmada',
                   'faturamento', 'cod_status']
    search_fields = ['numero', 'observacao']
    ordering = ['-numero']
    fields = (('numero', 'ativa'),
              ('faturamento', 'cod_status', 'msg_status'),
              'saida', 'entrega', 'confirmada', 'observacao')
    readonly_fields = ['numero', 'faturamento',
                       'cod_status', 'msg_status', 'ativa']


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
