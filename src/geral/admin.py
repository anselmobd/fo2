from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking, Dispositivos, RoloBipado


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
