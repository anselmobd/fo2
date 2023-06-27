from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import \
    TipoMaquina, UnidadeTempo, Frequencia, Maquina, UsuarioTipoMaquina, \
    Atividade, AtividadeMetrica, Rotina, RotinaPasso


class TipoMaquinaAdmin(admin.ModelAdmin):
    list_display = ['slug', 'descricao']
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


class UnidadeTempoAdmin(admin.ModelAdmin):
    fields = ['codigo', 'nome']
    readonly_fields = ['codigo', 'nome']


class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ['ordem', 'nome']
    ordering = ['ordem', 'nome']


class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['tipo_maquina', 'nome', 'descricao', 'data_inicio']
    fields = ['tipo_maquina', 'nome', 'slug', 'descricao', 'data_inicio']
    readonly_fields = ['slug']
    ordering = ['nome']


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


class RotinaAdmin(admin.ModelAdmin):
    list_display = ['tipo_maquina', 'frequencia', 'nome']


class RotinaPassoAdmin(admin.ModelAdmin):
    list_display = ['rotina', 'ordem', 'atividade']
    ordering = ['rotina', 'ordem']


intr_adm_site.register(TipoMaquina, TipoMaquinaAdmin)
intr_adm_site.register(UnidadeTempo, UnidadeTempoAdmin)
intr_adm_site.register(Frequencia, FrequenciaAdmin)
intr_adm_site.register(Maquina, MaquinaAdmin)
intr_adm_site.register(UsuarioTipoMaquina, UsuarioTipoMaquinaAdmin)
intr_adm_site.register(Atividade, AtividadeAdmin)
intr_adm_site.register(AtividadeMetrica, AtividadeMetricaAdmin)
intr_adm_site.register(Rotina, RotinaAdmin)
intr_adm_site.register(RotinaPasso, RotinaPassoAdmin)
