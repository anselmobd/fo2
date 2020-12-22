from django.contrib import admin

from fo2.admin import intr_adm_site

import ti.models


class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.EquipmentType, EquipmentTypeAdmin)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'slug', 'primary_ip']
    search_fields = ['type__name', 'type__slug', 'name', 'slug', 'primary_ip']
    ordering = ['type', 'slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.Equipment, EquipmentAdmin)


class InterfaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.InterfaceType, InterfaceTypeAdmin)

class InterfaceAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'slug', 'mac_adress', 'ip']
    search_fields = ['type__name', 'type__slug', 'name', 'slug', 'mac_adress', 'ip']
    ordering = ['type', 'slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.Interface, InterfaceAdmin)
