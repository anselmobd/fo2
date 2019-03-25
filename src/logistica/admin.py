from django.contrib import admin

from fo2.admin import intr_adm_site

import logistica.models as models


class NotaFiscalAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['numero', 'faturamento',
                    'saida', 'entrega', 'confirmada',
                    'natu_venda', 'ativa', 'nf_devolucao',
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
    fields = (('numero', 'ativa', 'nf_devolucao'),
              ('dest_cnpj', 'dest_nome', 'uf', 'transp_nome'),
              ('pedido', 'ped_cliente'),
              ('natu_venda', 'natu_descr'),
              ('volumes', 'valor'),
              ('faturamento', 'cod_status', 'msg_status'),
              'saida', 'entrega', 'confirmada', 'observacao', 'id')
    readonly_fields = ['id', 'numero', 'faturamento',
                       'pedido', 'ped_cliente',
                       'volumes', 'valor',
                       'cod_status', 'msg_status', 'ativa', 'nf_devolucao',
                       'dest_cnpj', 'dest_nome', 'uf',
                       'transp_nome', 'natu_descr', 'natu_venda',
                       ]


intr_adm_site.register(models.NotaFiscal, NotaFiscalAdmin)


class PosicaoCargaAdmin(admin.ModelAdmin):
    list_display = ['nome']


intr_adm_site.register(models.PosicaoCarga, PosicaoCargaAdmin)


class RotinaLogisticaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    readonly_fields = ['slug']


intr_adm_site.register(models.RotinaLogistica, RotinaLogisticaAdmin)


class PosicaoCargaAlteracaoAdmin(admin.ModelAdmin):
    list_display = [
        'inicial', 'ordem', 'descricao', 'final', 'efeito']
    ordering = ['inicial', 'ordem']


intr_adm_site.register(
    models.PosicaoCargaAlteracao, PosicaoCargaAlteracaoAdmin)
