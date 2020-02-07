from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import Servidor, Diretorio


class ServidorAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'hostname', 'ip4']
    search_fields = ['descricao', 'hostname', 'ip4']
    ordering = ['descricao']
    fields = ['descricao', 'hostname', 'ip4', 'user', 'key_file']


class DiretorioAdmin(admin.ModelAdmin):
    list_display = ['servidor', 'descricao', 'caminho']
    search_fields = ['descricao', 'caminho']
    ordering = ['descricao']
    fields = [
        'servidor', 'descricao', 'caminho', 'file_perm', 'file_user',
        'file_group']


intr_adm_site.register(Servidor, ServidorAdmin)
intr_adm_site.register(Diretorio, DiretorioAdmin)
