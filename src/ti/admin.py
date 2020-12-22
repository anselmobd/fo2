from django.contrib import admin

from fo2.admin import intr_adm_site

import ti.models


class TipoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.TipoEquipamento, TipoEquipamentoAdmin)


class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'name', 'slug', 'ip_principal']
    search_fields = ['tipo__name', 'tipo__slug', 'name', 'slug', 'ip_principal']
    ordering = ['tipo', 'slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.Equipamento, EquipamentoAdmin)


class TipoInterfaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.TipoInterface, TipoInterfaceAdmin)
