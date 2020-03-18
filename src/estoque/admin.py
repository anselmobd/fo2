from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMovStq


class TipoMovStqAdmin(admin.ModelAdmin):
    list_display = ["codigo", "descricao"]


intr_adm_site.register(TipoMovStq, TipoMovStqAdmin)
