from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'volumes', 'valor', 'dest_cnpj', 'dest_nome', 'uf',
                    'transp_nome', 'natu_venda',
                    'faturamento', 'cod_status', 'ativa',
                    'saida', 'entrega', 'confirmada', 'observacao']
    list_filter = ['ativa', 'natu_venda', 'saida',
                   'entrega', 'confirmada',
                   'faturamento', 'transp_nome', 'cod_status', 'uf']
    search_fields = ['numero', 'dest_cnpj', 'dest_nome', 'natu_descr',
                     'transp_nome', 'observacao']
    ordering = ['-numero']
    fields = (('numero', 'ativa'),
              ('dest_cnpj', 'dest_nome', 'uf', 'transp_nome'),
              ('natu_venda', 'natu_descr'),
              ('volumes', 'valor'),
              ('faturamento', 'cod_status', 'msg_status'),
              'saida', 'entrega', 'confirmada', 'observacao')
    readonly_fields = ['numero', 'faturamento',
                       'volumes', 'valor',
                       'cod_status', 'msg_status', 'ativa',
                       'dest_cnpj', 'dest_nome', 'uf',
                       'transp_nome', 'natu_descr', 'natu_venda',
                       ]


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
