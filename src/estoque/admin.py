from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMovStq, DocMovStq


class TipoMovStqAdmin(admin.ModelAdmin):
    list_display = ["codigo", "descricao"]


class DocMovStqAdmin(admin.ModelAdmin):
    pass


intr_adm_site.register(TipoMovStq, TipoMovStqAdmin)
intr_adm_site.register(DocMovStq, DocMovStqAdmin)
