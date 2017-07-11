from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'dest_cnpj', 'dest_nome', 'uf',
                    'natu_descr', 'natu_venda',
                    'faturamento', 'cod_status', 'msg_status', 'ativa',
                    'saida', 'entrega', 'confirmada', 'observacao']
    list_filter = ['ativa', 'natu_venda', 'saida',
                   'entrega', 'confirmada',
                   'faturamento', 'cod_status', 'uf']
    search_fields = ['numero', 'observacao',
                     'dest_cnpj', 'dest_nome', 'natu_descr']
    ordering = ['-numero']
    fields = (('numero', 'ativa'),
              ('faturamento', 'cod_status', 'msg_status'),
              ('dest_cnpj', 'dest_nome', 'uf'),
              ('natu_descr', 'natu_venda'),
              'saida', 'entrega', 'confirmada', 'observacao')
    readonly_fields = ['numero', 'faturamento',
                       'cod_status', 'msg_status', 'ativa',
                       'dest_cnpj', 'dest_nome', 'uf',
                       'natu_descr', 'natu_venda',
                       ]


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
