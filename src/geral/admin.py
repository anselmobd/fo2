from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking, Dispositivos, RoloBipado, Painel, \
    PainelModulo, UsuarioPainelModulo, InformacaoModulo, \
    Pop, PopGrupoAssunto, PopAssunto, \
    UsuarioPopAssunto, TipoParametro, Parametro, Config
from .forms import PainelModelForm, InformacaoModuloModelForm


class RecordTrackingAdmin(admin.ModelAdmin):
    list_display = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    search_fields = ['table', 'log', 'user']
    ordering = ['-id']
    fields = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    readonly_fields = ['time', 'table', 'record_id', 'iud', 'log', 'user']


class DispositivosAdmin(admin.ModelAdmin):
    list_display = ['key', 'nome']
    search_fields = ['key', 'nome']
    ordering = ['nome']
    fields = ['key', 'nome']
    readonly_fields = ['key']


class RoloBipadoAdmin(admin.ModelAdmin):
    list_display = [
        'dispositivo', 'rolo', 'date', 'referencia', 'tamanho', 'cor']
    search_fields = ['rolo', 'date', 'referencia', 'tamanho', 'cor']
    ordering = ['referencia', 'tamanho', 'cor', 'rolo']
    fields = ['dispositivo', 'rolo', 'date', 'referencia', 'tamanho', 'cor']
    readonly_fields = [
        'dispositivo', 'rolo', 'date', 'referencia', 'tamanho', 'cor']


intr_adm_site.register(RecordTracking, RecordTrackingAdmin)

intr_adm_site.register(Dispositivos, DispositivosAdmin)

intr_adm_site.register(RoloBipado, RoloBipadoAdmin)


class PainelAdmin(admin.ModelAdmin):
    form = PainelModelForm
    list_display = ['nome', 'slug', 'habilitado']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'slug', 'layout', 'habilitado']
    readonly_fields = ['slug']


class PainelModuloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'tipo', 'habilitado']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'slug', 'tipo', 'habilitado']
    readonly_fields = ['slug']


class UsuarioPainelModuloAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'painel_modulo']
    fields = ['usuario', 'painel_modulo']


class InformacaoModuloAdmin(admin.ModelAdmin):
    form = InformacaoModuloModelForm
    list_display = [
        'usuario', 'painel_modulo', 'data', 'chamada', 'habilitado']
    search_fields = ['chamada']
    ordering = ['data']
    fields = [
        'usuario', 'painel_modulo', 'data', 'chamada', 'texto', 'habilitado']
    readonly_fields = ['data']


intr_adm_site.register(Painel, PainelAdmin)
intr_adm_site.register(PainelModulo, PainelModuloAdmin)
intr_adm_site.register(UsuarioPainelModulo, UsuarioPainelModuloAdmin)
intr_adm_site.register(InformacaoModulo, InformacaoModuloAdmin)


class PopAdmin(admin.ModelAdmin):
    list_display = ['assunto', 'topico', 'descricao']
    search_fields = ['assunto__nome', 'topico', 'descricao']
    ordering = ['assunto', 'topico', 'descricao']
    fields = ['assunto', 'topico', 'descricao', 'pop', 'habilitado', 'uploaded_at']
    readonly_fields = ['uploaded_at']


intr_adm_site.register(Pop, PopAdmin)


class PopGrupoAssuntoAdmin(admin.ModelAdmin):
    list_display = ['ordem', 'nome', 'slug']
    search_fields = ['ordem', 'nome', 'slug']
    ordering = ['ordem']
    fields = ['ordem', 'nome', 'slug']
    readonly_fields = ['slug']


intr_adm_site.register(PopGrupoAssunto, PopGrupoAssuntoAdmin)


class PopAssuntoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'grupo_assunto', 'diretorio']
    search_fields = ['nome', 'slug', 'grupo_assunto', 'diretorio']
    ordering = ['nome']
    fields = ['nome', 'slug', 'grupo_assunto', 'diretorio']
    readonly_fields = ['slug']


intr_adm_site.register(PopAssunto, PopAssuntoAdmin)


class UsuarioPopAssuntoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'assunto']
    fields = ['usuario', 'assunto']
    list_filter = ['assunto', 'usuario']


intr_adm_site.register(UsuarioPopAssunto, UsuarioPopAssuntoAdmin)


class TipoParametroAdmin(admin.ModelAdmin):
    fields = ['codigo', 'descricao']


intr_adm_site.register(TipoParametro, TipoParametroAdmin)


class ParametroAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descricao', 'tipo', 'habilitado', 'usuario']
    fields = ['codigo', 'descricao', 'tipo', 'ajuda', 'habilitado', 'usuario']


intr_adm_site.register(Parametro, ParametroAdmin)


class ConfigAdmin(admin.ModelAdmin):
    list_display = ['parametro', 'usuario', 'valor']
    fields = ['parametro', 'usuario', 'valor']


intr_adm_site.register(Config, ConfigAdmin)
