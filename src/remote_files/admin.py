from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import Servidor


class ServidorAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'hostname', 'ip4']
    search_fields = ['descricao', 'hostname', 'ip4']
    ordering = ['descricao']
    fields = ['descricao', 'hostname', 'ip4']


intr_adm_site.register(Servidor, ServidorAdmin)
