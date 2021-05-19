from pprint import pprint

from django.conf import settings
from django.contrib import admin

from fo2.admin import intr_adm_site

from .forms import ModeloTermicaForm
from .models import (
    EnderecoDisponivel,
    Impresso,
    ImpressoraTermica,
    Lote,
    RegraColecao,
    ModeloTermica,
    SolicitaLote,
    SolicitaLotePedido,
    SolicitaLotePrinted,
    UsuarioImpresso,
)


class ImpressoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    search_fields = ['nome', 'slug']
    fields = ['nome', 'slug']
    readonly_fields = ['slug']


class ImpressoraTermicaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome']


class ModeloTermicaAdmin(admin.ModelAdmin):
    form = ModeloTermicaForm
    list_display = ['codigo', 'nome']
    search_fields = ['codigo', 'nome']
    ordering = ['codigo']
    fields = ['codigo', 'nome', 'gabarito']

    class Media:
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        js = [static_url+'/admin/lotes/modeloTermica.js', ]


class ImpressoInline(admin.TabularInline):
    model = Impresso


class ImpressoraTermicaInline(admin.TabularInline):
    model = ImpressoraTermica


class ModeloTermicaInline(admin.TabularInline):
    model = ModeloTermica


class UsuarioImpressoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'impresso',
                    'impressora_termica', 'modelo']
    ordering = ['usuario__username', 'impresso__nome',
                'impressora_termica__nome', 'modelo__codigo']
    search_fields = ['usuario__username', 'impresso__nome',
                     'impressora_termica__nome', 'modelo__codigo']
    fields = ['usuario', 'impresso',
              'impressora_termica', 'modelo']


class LoteAdmin(admin.ModelAdmin):
    list_display = [
        'lote', 'op', 'referencia', 'tamanho', 'cor', 'qtd_produzir',
        'estagio', 'local'
    ]
    ordering = ['lote']
    search_fields = ['lote', 'op', 'referencia', 'local']
    fields = [
        'lote', 'op', 'referencia', 'tamanho', 'cor', 'qtd_produzir',
        'estagio', 'local'
    ]


class RegraColecaoAdmin(admin.ModelAdmin):
    list_display = ['colecao', 'referencia', 'lead', 'lm_tam', 'lm_cor', 'lotes_caixa']
    ordering = ['colecao']


intr_adm_site.register(Impresso, ImpressoAdmin)
intr_adm_site.register(ImpressoraTermica, ImpressoraTermicaAdmin)
intr_adm_site.register(ModeloTermica, ModeloTermicaAdmin)
intr_adm_site.register(UsuarioImpresso, UsuarioImpressoAdmin)
intr_adm_site.register(Lote, LoteAdmin)
intr_adm_site.register(RegraColecao, RegraColecaoAdmin)


# solicitações


class SolicitaLoteAdmin(admin.ModelAdmin):
    list_display = ['numero', 'codigo', 'descricao', 'can_print']
    ordering = ['-id']


intr_adm_site.register(SolicitaLote, SolicitaLoteAdmin)

class SolicitaLotePedidoAdmin(admin.ModelAdmin):
    ordering = ['-solicitacao', 'pedido']


intr_adm_site.register(SolicitaLotePedido, SolicitaLotePedidoAdmin)


class SolicitaLotePrintedAdmin(admin.ModelAdmin):
    list_display = ['solicitacao', 'printed_at', 'printed_by']
    ordering = ['-printed_at']


intr_adm_site.register(SolicitaLotePrinted, SolicitaLotePrintedAdmin)


class EnderecoDisponivelAdmin(admin.ModelAdmin):
    pass


intr_adm_site.register(EnderecoDisponivel, EnderecoDisponivelAdmin)
