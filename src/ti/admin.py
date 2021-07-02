from django.contrib import admin

from fo2.admin import intr_adm_site

import ti.forms
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
    list_display = ['equipment', 'type', 'name', 'slug', 'mac_adress', 'fixed_ip']
    search_fields = ['equipment__name', 'interface__name', 'type__name', 'type__slug', 'name', 'slug', 'mac_adress', 'fixed_ip']
    ordering = ['type', 'slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.Interface, InterfaceAdmin)


class DhcpConfigAdmin(admin.ModelAdmin):
    form = ti.forms.DhcpConfigForm
    list_display = ['name', 'slug', 'primary_equipment', 'secondary_equipment']
    search_fields = ['name', 'slug', 'primary_equipment__name', 'secondary_equipment__name']
    ordering = ['slug']
    readonly_fields = ['slug']

intr_adm_site.register(ti.models.DhcpConfig, DhcpConfigAdmin)


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment', 'path', 'read_only']
    search_fields = ['name', 'equipment', 'path', 'read_only']
    ordering = ['name']

intr_adm_site.register(ti.models.Share, ShareAdmin)
