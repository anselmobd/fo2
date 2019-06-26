from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import *


class ModeloPassadoAdmin(admin.ModelAdmin):
    fields = ['nome', 'padrao']


intr_adm_site.register(ModeloPassado, ModeloPassadoAdmin)
