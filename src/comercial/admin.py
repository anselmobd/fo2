from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import *


class ModeloPassadoAdmin(admin.ModelAdmin):
    fields = ['nome', 'padrao']


class ModeloPassadoPeriodoAdmin(admin.ModelAdmin):
    fields = ['modelo', 'ordem', 'meses', 'peso']
    ordering = ['modelo__nome', 'ordem']


intr_adm_site.register(ModeloPassado, ModeloPassadoAdmin)
intr_adm_site.register(ModeloPassadoPeriodo, ModeloPassadoPeriodoAdmin)
