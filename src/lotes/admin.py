from django.contrib import admin

from fo2 import settings
from fo2.admin import intr_adm_site
from .models import ImpressoraTermica, ModeloTermica


class ImpressoraTermicaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome']


class ModeloTermicaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome']
    search_fields = ['codigo', 'nome']
    ordering = ['codigo']
    fields = ['codigo', 'nome', 'modelo', 'campos']

    class Media:
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        js = [static_url+'/admin/lotes/modeloTermica.js', ]


intr_adm_site.register(ImpressoraTermica, ImpressoraTermicaAdmin)
intr_adm_site.register(ModeloTermica, ModeloTermicaAdmin)
