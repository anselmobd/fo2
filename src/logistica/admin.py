from pprint import pprint

from django.conf import settings
from django.contrib import admin

from fo2.admin import intr_adm_site

import logistica.models as models
from logistica.forms import EntradaNfForm


class NotaFiscalAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = [
        "numero",
        "faturamento",
        "posicao",
        "saida",
        "entrega",
        "confirmada",
        "natu_venda",
        "ativa",
        "nf_devolucao",
        "uf",
        "transp_nome",
        "dest_nome",
        "dest_cnpj",
        "valor",
        "volumes",
        "cod_status",
        "observacao",
    ]
    list_editable = ["saida", "entrega", "confirmada"]
    # list_filter = ['ativa', 'natu_venda', 'saida',
    #                'entrega', 'confirmada',
    #                'faturamento', 'transp_nome', 'cod_status', 'uf']
    search_fields = ["numero", "transp_nome", "dest_nome"]
    ordering = ["-numero"]
    fields = (
        ("numero", "ativa", "nf_devolucao", "posicao"),
        ("dest_cnpj", "dest_nome", "uf", "transp_nome"),
        ("pedido", "ped_cliente"),
        ("natu_venda", "natu_descr"),
        ("volumes", "valor"),
        ("faturamento", "cod_status", "msg_status"),
        "saida",
        "entrega",
        "confirmada",
        "observacao",
        "id",
    )
    readonly_fields = [
        "id",
        "numero",
        "faturamento",
        "posicao",
        "pedido",
        "ped_cliente",
        "volumes",
        "valor",
        "cod_status",
        "msg_status",
        "ativa",
        "nf_devolucao",
        "dest_cnpj",
        "dest_nome",
        "uf",
        "transp_nome",
        "natu_descr",
        "natu_venda",
    ]


intr_adm_site.register(models.NotaFiscal, NotaFiscalAdmin)


class PosicaoCargaAdmin(admin.ModelAdmin):
    list_display = ["nome"]


intr_adm_site.register(models.PosicaoCarga, PosicaoCargaAdmin)


class RotinaLogisticaAdmin(admin.ModelAdmin):
    list_display = ["nome", "slug"]
    readonly_fields = ["slug"]


intr_adm_site.register(models.RotinaLogistica, RotinaLogisticaAdmin)


class PosicaoCargaAlteracaoAdmin(admin.ModelAdmin):
    list_display = ["inicial", "ordem", "descricao", "final", "efeito", "so_nfs_ativas"]
    ordering = ["inicial", "ordem"]


intr_adm_site.register(models.PosicaoCargaAlteracao, PosicaoCargaAlteracaoAdmin)


class NfEntradaAdmin(admin.ModelAdmin):
    def __init__(self, *args):
        super().__init__(*args)
        self.form = EntradaNfForm

        self._list_display = [
            "__str__",
            "emissor",
            "descricao",
            "volumes",
            "chegada",
            "transportadora",
            "motorista",
            "placa",
            "responsavel",
            "usuario",
            "quando",
        ]
        self._fields = [
            "cadastro",
            "numero",
            "tipo",
            "emissor",
            "descricao",
            "volumes",
            "chegada",
            "transportadora",
            "motorista",
            "placa",
            "responsavel",
            "usuario",
            "quando",
        ]

        self.list_per_page = 50
        self.list_display = self._list_display.copy()
        self.list_display.insert(0, "empresa")
        self.search_fields = ["emissor", "numero", "descricao"]
        self.ordering = ["-quando"]
        self.fields = self._fields.copy()
        self.fields.insert(0, "empresa")
        self.readonly_fields = ["usuario", "quando"]

    class Media:
        static_url = getattr(settings, "STATIC_URL", "/static/")
        js = [
            static_url + "/admin/logistica/nfEntrada.js",
        ]


class NfEntradaAgatorAdmin(NfEntradaAdmin):
    def __init__(self, *args):
        super().__init__(*args)

        self.list_display = self._list_display
        self.fields = self._fields


class NfEntradaTussorAdmin(NfEntradaAdmin):
    def __init__(self, *args):
        super().__init__(*args)

        self.list_display = self._list_display
        self.fields = self._fields


intr_adm_site.register(models.NfEntrada, NfEntradaAdmin)
intr_adm_site.register(models.NfEntradaAgator, NfEntradaAgatorAdmin)
intr_adm_site.register(models.NfEntradaTussor, NfEntradaTussorAdmin)
