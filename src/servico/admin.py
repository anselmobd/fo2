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


class NumeroDocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'create_at', 'user', 'ativo']
    fields = ['id', 'tipo', 'create_at', 'user', 'ativo']
    readonly_fields = ['id', 'create_at']
    ordering = ['create_at']


intr_adm_site.register(servico.models.NumeroDocumento, NumeroDocumentoAdmin)


class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['ordem', 'nome', 'slug']
    fields = ['ordem', 'nome', 'slug']
    ordering = ['ordem']


intr_adm_site.register(servico.models.TipoEvento, TipoEventoAdmin)
