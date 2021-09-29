from django.contrib import admin

from fo2.admin import intr_adm_site

import ti.forms
import ti.models


@admin.register(ti.models.OSType, site=intr_adm_site)
class OSTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(ti.models.OS, site=intr_adm_site)
class OSAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'version', 'bits', 'slug']
    search_fields = ['slug', 'type__name', 'type__slug', 'name', 'version', 'bits']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(ti.models.EquipmentType, site=intr_adm_site)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(ti.models.Equipment, site=intr_adm_site)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['slug', 'type', 'name', 'descr', 'use', 'users', 'primary_ip']
    search_fields = ['slug', 'type__name', 'type__slug', 'name', 'descr', 'use', 'users', 'primary_ip']
    ordering = ['slug']
    readonly_fields = ['slug']
    fields = (
        'type',
        ('name', 'slug'),
        'descr',
        'use',
        'users',
        'primary_ip',
    )


@admin.register(ti.models.InterfaceType, site=intr_adm_site)
class InterfaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(ti.models.Interface, site=intr_adm_site)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'type', 'name', 'slug', 'mac_adress', 'fixed_ip']
    search_fields = ['equipment__name', 'interface__name', 'type__name', 'type__slug', 'name', 'slug', 'mac_adress', 'fixed_ip']
    ordering = ['type', 'slug']
    readonly_fields = ['slug']


@admin.register(ti.models.DhcpConfig, site=intr_adm_site)
class DhcpConfigAdmin(admin.ModelAdmin):
    form = ti.forms.DhcpConfigForm
    list_display = ['name', 'slug', 'primary_equipment', 'secondary_equipment']
    search_fields = ['name', 'slug', 'primary_equipment__name', 'secondary_equipment__name']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(ti.models.Share, site=intr_adm_site)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment', 'path', 'read_only']
    search_fields = ['name', 'equipment', 'path', 'read_only']
    ordering = ['name']
