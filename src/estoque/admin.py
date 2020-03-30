from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMovStq, DocMovStq


class TipoMovStqAdmin(admin.ModelAdmin):
    list_display = ["codigo", "descricao"]


class DocMovStqAdmin(admin.ModelAdmin):

    def get_num_doc(self, obj):
        return obj.num_doc

    get_num_doc.short_description = 'Número de documento'

    list_display = ["get_num_doc", "descricao"]


intr_adm_site.register(TipoMovStq, TipoMovStqAdmin)
intr_adm_site.register(DocMovStq, DocMovStqAdmin)
