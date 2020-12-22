from django.contrib import admin

from fo2.admin import intr_adm_site

import ti.models


class TipoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.TipoEquipamento, TipoEquipamentoAdmin)
