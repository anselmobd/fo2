from django.contrib import admin

from fo2.admin import intr_adm_site

import servico.models


class EquipeAtendimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'descricao']
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


intr_adm_site.register(servico.models.EquipeAtendimento, EquipeAtendimentoAdmin)


class TipoFuncaoExercidaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'nivel_operacional']
    fields = ['nome', 'slug', 'nivel_operacional']
    readonly_fields = ['slug']
    ordering = ['nivel_operacional']


intr_adm_site.register(servico.models.TipoFuncaoExercida, TipoFuncaoExercidaAdmin)


class PapelUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'funcao', 'equipe']
    fields = ['usuario', 'funcao', 'equipe']
    ordering = ['usuario', 'funcao', 'equipe']


intr_adm_site.register(servico.models.PapelUsuario, PapelUsuarioAdmin)


class NivelAtendimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'horas']
    fields = ['nome', 'slug', 'horas']
    readonly_fields = ['slug']
    ordering = ['horas']


intr_adm_site.register(servico.models.NivelAtendimento, NivelAtendimentoAdmin)


class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']


intr_adm_site.register(servico.models.TipoDocumento, TipoDocumentoAdmin)


class StatusAdmin(admin.ModelAdmin):
    pass


intr_adm_site.register(servico.models.Status, StatusAdmin)


class NumeroDocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'create_at', 'user', 'ativo', 'status']
    fields = list_display
    readonly_fields = ['id', 'create_at']
    ordering = ['create_at']


intr_adm_site.register(servico.models.NumeroDocumento, NumeroDocumentoAdmin)


class TipoEventoAdmin(admin.ModelAdmin):
    list_display = [
        'ordem', 'nome', 'codigo',
        'edita_nivel', 'edita_equipe', 'edita_descricao'
    ]
    fields = list_display
    ordering = ['ordem']


intr_adm_site.register(servico.models.Evento, TipoEventoAdmin)


class EventoDeStatusAdmin(admin.ModelAdmin):
    list_display = ['status_pre', 'evento', 'status_pos']
    fields = list_display
    ordering = list_display


intr_adm_site.register(servico.models.EventoDeStatus, EventoDeStatusAdmin)


class ServicoEventoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'evento', 'create_at', 'user', 'nivel', 'equipe', 'descricao']
    ordering = ['numero']

intr_adm_site.register(servico.models.ServicoEvento, ServicoEventoAdmin)
