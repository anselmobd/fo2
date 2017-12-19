from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking, Dispositivos, RoloBipado, Painel, \
    PainelModulo, UsuarioPainelModulo, InformacaoModulo
from .forms import PainelForm, InformacaoModuloForm


class RecordTrackingAdmin(admin.ModelAdmin):
    list_display = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    search_fields = ['table', 'log', 'user']
    ordering = ['time', 'table', 'record_id']
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
    form = PainelForm
    list_display = ['nome', 'slug']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'slug', 'layout']
    readonly_fields = ['slug']


class PainelModuloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'tipo']


class UsuarioPainelModuloAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'painel_modulo']
    fields = ['usuario', 'painel_modulo']


class InformacaoModuloAdmin(admin.ModelAdmin):
    form = InformacaoModuloForm
    list_display = ['usuario', 'painel_modulo', 'data', 'chamada']
    search_fields = ['chamada']
    ordering = ['data']
    fields = ['usuario', 'painel_modulo', 'data', 'chamada', 'texto']
    readonly_fields = ['data']


intr_adm_site.register(Painel, PainelAdmin)
intr_adm_site.register(PainelModulo, PainelModuloAdmin)
intr_adm_site.register(UsuarioPainelModulo, UsuarioPainelModuloAdmin)
intr_adm_site.register(InformacaoModulo, InformacaoModuloAdmin)
