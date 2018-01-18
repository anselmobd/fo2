from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import NotaFiscal


class NotaFiscalAdmin(admin.ModelAdmin):
    list_per_page = 40
    list_display = ['numero', 'faturamento',
                    'saida', 'entrega', 'confirmada',
                    'natu_venda', 'ativa',
                    'uf', 'transp_nome',
                    'dest_nome', 'dest_cnpj',
                    'valor', 'volumes',
                    'cod_status',
                    'observacao']
    list_editable = ['saida', 'entrega', 'confirmada']
    # list_filter = ['ativa', 'natu_venda', 'saida',
    #                'entrega', 'confirmada',
    #                'faturamento', 'transp_nome', 'cod_status', 'uf']
    search_fields = ['numero', 'dest_cnpj', 'dest_nome', 'natu_descr',
                     'transp_nome', 'observacao']
    ordering = ['-numero']
    fields = (('numero', 'ativa'),
              ('dest_cnpj', 'dest_nome', 'uf', 'transp_nome'),
              ('pedido', 'ped_cliente'),
              ('natu_venda', 'natu_descr'),
              ('volumes', 'valor'),
              ('faturamento', 'cod_status', 'msg_status'),
              'saida', 'entrega', 'confirmada', 'observacao', 'id')
    readonly_fields = ['id', 'numero', 'faturamento',
                       'pedido', 'ped_cliente',
                       'volumes', 'valor',
                       'cod_status', 'msg_status', 'ativa',
                       'dest_cnpj', 'dest_nome', 'uf',
                       'transp_nome', 'natu_descr', 'natu_venda',
                       ]


intr_adm_site.register(NotaFiscal, NotaFiscalAdmin)
