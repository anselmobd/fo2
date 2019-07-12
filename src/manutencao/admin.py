from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import \
    TipoMaquina, UnidadeTempo, Maquina, UsuarioTipoMaquina, Atividade, \
    AtividadeMetrica


class TipoMaquinaAdmin(admin.ModelAdmin):
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


class UnidadeTempoAdmin(admin.ModelAdmin):
    fields = ['codigo', 'nome']
    readonly_fields = ['codigo', 'nome']


class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['tipo_maquina', 'nome', 'descricao', 'data_inicio']
    fields = ['tipo_maquina', 'nome', 'slug', 'descricao', 'data_inicio']
    readonly_fields = ['slug']


class UsuarioTipoMaquinaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_maquina']
    ordering = ['usuario__username', 'tipo_maquina__nome']
    search_fields = ['usuario__username', 'tipo_maquina__nome']
    fields = ['usuario', 'tipo_maquina']


class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'resumo']
    ordering = ['id']
    fields = ['resumo', 'descricao']


class AtividadeMetricaAdmin(admin.ModelAdmin):
    list_display = ['atividade', 'ordem', 'descricao']
    ordering = ['atividade', 'ordem']
    fields = ['atividade', 'ordem', 'descricao']


intr_adm_site.register(TipoMaquina, TipoMaquinaAdmin)
intr_adm_site.register(UnidadeTempo, UnidadeTempoAdmin)
intr_adm_site.register(Maquina, MaquinaAdmin)
intr_adm_site.register(UsuarioTipoMaquina, UsuarioTipoMaquinaAdmin)
intr_adm_site.register(Atividade, AtividadeAdmin)
intr_adm_site.register(AtividadeMetrica, AtividadeMetricaAdmin)
