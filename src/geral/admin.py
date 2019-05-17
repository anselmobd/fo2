from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking, Dispositivos, RoloBipado, Painel, \
    PainelModulo, UsuarioPainelModulo, InformacaoModulo, Pop, PopAssunto, \
    UsuarioPopAssunto, TipoParametro, Parametro, Config
from .forms import PainelModelForm, InformacaoModuloModelForm


class RecordTrackingAdmin(admin.ModelAdmin):
    list_display = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    search_fields = ['table', 'log', 'user']
    ordering = ['-time', '-table', '-record_id']
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
    list_display = ['nome', 'slug', 'tipo']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'slug', 'tipo']
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
    list_display = ['assunto', 'descricao']
    search_fields = ['assunto__nome', 'descricao']
    ordering = ['assunto', 'descricao']
    fields = ['assunto', 'descricao', 'pop', 'habilitado', 'uploaded_at']
    readonly_fields = ['uploaded_at']


intr_adm_site.register(Pop, PopAdmin)


class PopAssuntoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'grupo', 'grupo_slug', 'diretorio']
    search_fields = ['nome', 'slug', 'grupo', 'grupo_slug', 'diretorio']
    ordering = ['nome']
    fields = ['nome', 'slug', 'grupo', 'grupo_slug', 'diretorio']
    readonly_fields = ['slug', 'grupo_slug']


intr_adm_site.register(PopAssunto, PopAssuntoAdmin)


class UsuarioPopAssuntoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'assunto']
    fields = ['usuario', 'assunto']


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
