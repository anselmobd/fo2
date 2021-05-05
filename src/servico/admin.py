from django.contrib import admin

from fo2.admin import intr_adm_site

import servico.models


class EquipeAtendimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'descricao']
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


intr_adm_site.register(servico.models.EquipeAtendimento, EquipeAtendimentoAdmin)


class FuncaoExercidaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'nivel_operacional', 'parte']
    fields = list_display
    readonly_fields = ['slug']
    ordering = ['nivel_operacional']


intr_adm_site.register(servico.models.FuncaoExercida, FuncaoExercidaAdmin)


class UsuarioAdminFuncao(admin.ModelAdmin):
    list_display = ['usuario', 'funcao', 'equipe']
    fields = ['usuario', 'funcao', 'equipe']
    ordering = ['usuario', 'funcao', 'equipe']


intr_adm_site.register(servico.models.UsuarioFuncao, UsuarioAdminFuncao)


class ClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'horas']
    fields = ['nome', 'slug', 'horas']
    readonly_fields = ['slug']
    ordering = ['horas']


intr_adm_site.register(servico.models.Classificacao, ClassificacaoAdmin)


class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']


intr_adm_site.register(servico.models.TipoDocumento, TipoDocumentoAdmin)


class StatusAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo']


intr_adm_site.register(servico.models.Status, StatusAdmin)


class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'create_at', 'user', 'ativo']
    fields = list_display
    readonly_fields = ['id', 'create_at']
    ordering = ['create_at']


intr_adm_site.register(servico.models.Documento, DocumentoAdmin)


class TipoEventoAdmin(admin.ModelAdmin):
    list_display = [
        'ordem', 'nome', 'codigo',
        'edita_nivel', 'edita_equipe', 'edita_descricao'
    ]
    fields = list_display
    ordering = ['ordem']


intr_adm_site.register(servico.models.Evento, TipoEventoAdmin)


class StatusEventoAdmin(admin.ModelAdmin):
    list_display = ['status_pre', 'evento', 'status_pos']
    fields = list_display
    ordering = ['status_pre_id', 'evento__ordem', 'status_pos_id']


intr_adm_site.register(servico.models.StatusEvento, StatusEventoAdmin)


class InteracaoAdmin(admin.ModelAdmin):
    list_display = [
        'documento', 'evento', 'status', 'create_at', 'user',
        'nivel', 'equipe', 'descricao'
    ]
    ordering = ['-documento', '-create_at']

intr_adm_site.register(servico.models.Interacao, InteracaoAdmin)
